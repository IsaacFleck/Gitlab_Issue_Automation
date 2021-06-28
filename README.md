# Gitlab Issue Automation
This repository hosts a series of scripts used to automate the usage of Gitlab, making issue management easier for the developer moving most of their data entry to the 'Label' section.

You will need to host this script and run as often as needed as it is currently designed to be ran from another process ever 5 minutes.

!Please note that this script directly changes gitlab issues - I take no responsibility for the use of this script in a production enviroment!

# Issue Management

Python script which automatically manages GitLab issues based on Labels to assist in the management of our issues.

Current features are:
* Assigning Milestones based on their coorisponding Labels
* Assigning Epics based on thier coorisponding Labels 
* If assigned to Milestone and their issue is missing a deadline -> Automatically set to MS Deadline
* Marks all newly created issues as 'New' for weekly Retro meeting
    * Skips any items with 'Future::Feature' as this is used to track potential enhancements that have not come from users  

### Requirements
* Python 3
* requests package
* datetime package
* pandas package 
* logging package
* json package