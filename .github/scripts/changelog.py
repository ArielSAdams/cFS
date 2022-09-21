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
AuthorPrChanges = dict()    # {author: #TotalChanges}

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
            AuthorPrChanges[pr['author']] = pr['additions'] + pr['deletions']
        else:
            PrData[pr['author']].append(pr)
            AuthorPrChanges[pr['author']] += pr['additions'] + pr['deletions']

# no prs to write, exit program
if len(PrData) == 0:
    print("Failed to find relevant Pull Requests for the changelog. Exiting...\n")
    sys.exit()

# re-order dict according to sum(additions, deletions) of each pr for each author
AuthorPrChanges = {k: v for k, v in sorted(AuthorPrChanges.items(), key=lambda item: item[1])}

# write to markdown
ccb_date = date.today().strftime('%Y.%m.%d')
# prev_ccb_date = (date.today() - timedelta(days=7)).strftime('%Y.%m.%d')
fileName = "CCB.md" #+ ccb_date +
with open(fileName, 'w') as f:
    f.write("## Items for Discussion\n\n")
    for author in AuthorPrChanges.keys():
        f.write("### @" + author + "\n\n")
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
    print("CCB markdown has been successfully created")
