import requests 
import json 
from datetime import datetime, timedelta, timezone
import pandas as pd
import logging
import secrets

starttime = datetime.now()

scriptrunfreq = 5

# Import token from secrets file (see .\modules\secrets.py)
token = secrets.token

# Import group from secrets file (see .\modules\secrets.py)
group = secrets.group

logging.basicConfig(filename=r"C:\logs\issueManagemet.log", level=logging.INFO)

logging.info('Script Start time: ' + str(starttime))

def putreq(token, projid, iid, label, duedate, milestone, epic):

    baseurl = "https://gitlab.com/api/v4/projects/" + str(projid) + "/issues/" + str(iid) + '?'
    string = ''

    if str(epic) != '':
        string += 'Epic is missing assign to Epic ID: ' + str(epic)
        baseurl += 'epic_iid=' + str(epic) + '&'
    if str(duedate) != '':    
        string += 'Due Date is missing set due date to: ' + str(duedate)
        baseurl += 'due_date=' + str(duedate) + '&'
    if str(milestone) != '':        
        string += 'Milesone is missing assign to Milestone ID: ' + str(milestone)
        baseurl += 'milestone_id=' + str(milestone) + '&'
    if str(label) != '':
        string += 'Issue labels: ' + str(label)
        baseurl += 'labels=' + str(label) + '&'

    if str(string) != '':
        logging.info('Current Issue: ' + str(iid))
        logging.info(string)    
     
    payload={}
    headers = {
      'PRIVATE-TOKEN': token,
    }

    url = baseurl

    if str(string) != '':
        response = requests.request("put", url, headers=headers, data=payload)
        logging.info('Put Request Response Code:' + str(response.status_code))

def getissues(token, group):

    i = 1
    issuelist = []
    while(True):   

        url = "https://gitlab.com/api/v4/groups/{}/issues?state=opened&page={}".format(group,i)
        payload={}
        headers = {
          'PRIVATE-TOKEN': token,
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        i += 1
        if response.text == '[]':
            break 
        j = json.loads(response.text)
        for issue in j:
            issuelist.append(issue)
        issues = pd.DataFrame.from_dict(issuelist)
        issues = issues.drop(columns=['epic','description','updated_at','web_url','closed_at','closed_by','assignees','assignee','time_stats','task_completion_status','_links','references'])
    
    return issues

def getmilestones(token, group):

    url = "https://gitlab.com/api/v4/groups/{}}/milestones".format(group)

    payload={}
    headers = {
      'PRIVATE-TOKEN': token,
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    j = json.loads(response.text)
    milestones = pd.DataFrame.from_dict(j)
    milestones = milestones.drop(columns=['group_id','description','created_at','updated_at','web_url'])
    return milestones

def getepics(token, group):

    url = "https://gitlab.com/api/v4/groups/{}}/epics".format(group)

    payload={}
    headers = {
      'PRIVATE-TOKEN': token,
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    j = json.loads(response.text)
    epics = pd.DataFrame.from_dict(j)
    epics = epics.drop(columns=['group_id','description','created_at','updated_at','web_url','confidential','author','references','upvotes','downvotes','_links'])
    return epics

Milestones = getmilestones(token)
Issues = getissues(token)
Epics = getepics(token)

epics = {}
milestones = {}

# Populates the epic dict 
for index, row in Epics.iterrows():    
    pattern = ["[","]","'"]
    id = str(row['iid'])
    epiclabel = str(row['labels'])
    for i in pattern:
        id = id.replace(i, '')
        epiclabel = epiclabel.replace(i, '')
    epics[epiclabel] = id

# Populates the milestone dict
for index, row in Milestones.iterrows():
    milestones[str(row['id'])] = str(row['due_date'])


cdate = datetime.now() + timedelta(hours=4)

for index, row in Issues.iterrows():
    projid = row['project_id']
    id = ''
    labels = ''
    milestoneid = '' 
    newduedate = ''
    epicid = ''
    pattern = ["[","]","'"]

    id = row['iid']
    
    scriptfreq = timedelta(minutes=scriptrunfreq)
    labels = row['labels']
    label = str(labels).lstrip('[')
    label = label.strip(']')
    for i in pattern:
        label = label.replace(i, '')

    issuedate = row['created_at'][:-1]    
    issuedate = datetime.fromisoformat(issuedate)    
    tdelta =  cdate - issuedate

# This function tacks on New if the item has been created since the script was last run
# If the item has a Future::Features tag it will skip the item then owrk normally for the rest of the scripts functions 
# It then continues to the next item, it will handle the other tasks then 

    if tdelta < scriptfreq:
        if 'Future::Features' in labels:
            continue 
        elif 'New' not in labels:
            if not labels:
                label += "New"
            else:
                label += ",New" 
            labels = label     
            putreq(token,projid,id,labels,newduedate,milestoneid,epicid)
        continue
    else:
        pattern =["\""]
        for i in pattern:
            label = label.replace(i, '')
        labels = label

        # This function checks to see if an Epic label exists and returns 'epicid'
        #  if it does and the item is missing an epic 
        #  This check is performed here THEN removes the Labels value to avoid Creating random labels in Gitlab 
        for e in epics:
            if e in labels:
                if row['epic_iid'] != row['epic_iid']:
                    epicid = epics[str(e)]
        labels = ""
                
# This function checks the due date and the milestone assigned to an issue
# If the Milestone is assinged and there is no Due Date - NewDueDate is set
# Does nothing if due date is set and the Milestone is empty

    if row['milestone'] is not None:
        if row['due_date'] is None:
            newduedate = milestones[str(row['milestone']['id'])] 
    
    putreq(token,projid,id,labels,newduedate,milestoneid,epicid)

endtime = datetime.now()
totaltime = endtime - starttime

logging.info('Script Start time: ' + str(starttime))
logging.info('Total Runtime: ' + str(totaltime))