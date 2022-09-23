from datetime import date, timedelta
import subprocess
import json
import sys
import time
import os

# extract pull request data from GitHub
repos = ['cFE']
for repo in repos:
    subprocess.Popen('gh pr list --repo nasa/' + str(repo) + ' --search "draft:false" --json number,author,title,url,additions,deletions,labels | jq -c ' + '\'reduce range(0, length) as $index (.; (.[$index].author=.[$index].author.login | .[$index].number=(.[$index].number|"\'' + str(repo) + '\' PR #\(.)") )) | .[]\' ' + '>> temp.json', shell=True)

time.sleep(5)
subprocess.Popen('jq -s . temp.json > prs.json', shell=True)
time.sleep(5)

# load a list of pull requests as discrete python dictionaries
with open ('prs.json') as prs_file:
    prs = json.load(prs_file)

PrData          = dict()    # {author: [pr1, pr2, pr3, ...]}

# ignore all prs except ones with CCB:Approved
for pr in prs:
    ignore = True
    for label in pr['labels']:
        if label['name'] == 'CCB:Approved':
            ignore = False
            break
    if ignore == False:
        if pr['author'] not in PrData:
            PrData[pr['author']] = [pr]
        else:
            PrData[pr['author']].append(pr)

# no prs to write, exit program
if len(PrData) == 0:
    print("Failed to find relevant Pull Requests for the changelog. Exiting...\n")
    sys.exit()

# Need to grab changelog from cFE
# Need to open changelog 
with open(fileName, 'w') as f:
    # Need to write the development build from latest commit containing "Bump to"
    f.write("## Development Build:\n\n")
    # Need to write title of all Prs in bulleted list
    # Need to write Pr numbers on one bullet 
    for pr_auth in PrData[author]:
        if (author == pr_auth['author']):
            f.write("[" + pr_auth['number'] + "](" + pr_auth['url'].replace("pull", "issues") + ") " + pr_auth['title'] + "\n\n")

# close files
f.close()
prs_file.close()
time.sleep(5)
try:
    os.remove("prs.json")
    os.remove("temp.json")
except OSError:
    pass

time.sleep(5)

if (os.stat(fileName).st_size != 0):
    print("Changelog markdown has been successfully updated")
