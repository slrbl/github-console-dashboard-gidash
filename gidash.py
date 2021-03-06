# Author: walid.daboubi@gmail.com
# About: Have a global view of your Github repositories with simple console command
# Last review: CREATED - 07/02/2021

import requests
import datetime
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from database import *

# Create Database/Session
engine = create_engine('sqlite:///./data.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

headers = {
    'Authorization': 'token {}'.format(os.getenv('GITHUB_TOKEN')),
}
repos = requests.get('https://api.github.com/user/repos', headers=headers).json()

total_forks,total_stargazers,total_watchers,total_open_issues = 0,0,0,0

for repo in repos:
    # Check if the repo is a source not forked from another repo and not private
    if repo['fork'] == False and repo['private'] == False:
        total_forks += repo['forks_count']
        total_stargazers += repo['stargazers_count']
        total_watchers += repo['watchers_count']
        total_open_issues += repo['open_issues_count']
        existing_record = session.query(Repo).filter_by(github_id=repo['id']).first()
        if existing_record != None:
            #print('The repo {} has already been added'.format(repo['id']))
            existing_record.name=repo['name']
            existing_record.forks_count=repo['forks_count']
            existing_record.stargazers_count=repo['stargazers_count']
            existing_record.watchers_count=repo['watchers_count']
            existing_record.open_issues_count=repo['open_issues_count']
        else:
            #print('Start tracking a new repository {}'.format(repo['id']))
            repo_record = Repo(
                name=repo['name'],
                github_id=repo['id'],
                forks_count=repo['forks_count'],
                stargazers_count=repo['stargazers_count'],
                watchers_count=repo['watchers_count'],
                open_issues_count=repo['open_issues_count']
            )
            session.add(repo_record)
        #print ('='*100)

from rich.columns import Columns
from rich.panel import Panel
from rich.console import Console
from rich.table import Table


console = Console()
user = requests.get('https://api.github.com/user', headers=headers).json()

console.print('\nABOUT YOUR GITHUB\n'.upper())
console.print('OWNER: {}'.format(user['name']))
console.print('LOGIN: {}'.format(user['login']))
console.print('URL: {}'.format(user['url']))

# Create a new snap
new_snap_record = Snap(
    #date=datetime.datetime.utcnow,
    date=datetime.datetime.now(),
    total_forks=total_forks,
    total_stargazers=total_stargazers,
    total_watchers=total_watchers,
    total_open_issues=total_open_issues,
    followers=user['followers']
)

if session.query(Snap).count()>0:
    latest_snap_record = session.query(Snap).all()[-1]
    news = {}
    new_snap_mapper = inspect(new_snap_record)
    lastest_snap_mapper = inspect(latest_snap_record)
    for new_column,lastest_column in zip(new_snap_mapper.attrs,lastest_snap_mapper.attrs):
        if new_column.key not in ['id','date']:
            diff = new_column.value - lastest_column.value
            formatted_diff = str(diff)
            if (diff) > 0:
                formatted_diff = '+{}'.format(formatted_diff)
            news[new_column.key] = formatted_diff
    # Draw news panels
    panels = []
    for element in news:
        panels.append(
            Panel(news[element], expand=True,title=element.replace('total_','').replace('_',' ').upper())
        )
    console.print('\nYou github news summary\n'.upper())
    console.print(Columns(panels))
    # Current VS previous status table
    table = Table(show_header=True, header_style="bold red")
    table.add_column("Status", style="dim")
    table.add_column("Date", style="dim")
    table.add_column("Forks", justify="center")
    table.add_column("Stars", justify="center")
    table.add_column("Watchers", justify="center")
    table.add_column("Open Issues", justify="center")
    table.add_column("Followers", justify="center")
    table.add_row(
        "CURRENT",
        str(new_snap_record.date),
        str(new_snap_record.total_forks),
        str(new_snap_record.total_stargazers),
        str(new_snap_record.total_watchers),
        str(new_snap_record.total_open_issues),
        str(new_snap_record.followers),
    )
    table.add_row(
        "PREVIOUS",
        str(latest_snap_record.date),
        str(latest_snap_record.total_forks),
        str(latest_snap_record.total_stargazers),
        str(latest_snap_record.total_watchers),
        str(latest_snap_record.total_open_issues),
        str(latest_snap_record.followers),
    )
    console.print('\nCurrent status VS previous know status\n'.upper())
    console.print(table)
# Repositories
repos = session.query(Repo).order_by(desc(Repo.stargazers_count))
table = Table(show_header=True, header_style="bold green")
table.add_column("Github", style="dim")
table.add_column("Name", justify="left")
table.add_column("Forks", justify="center")
table.add_column("Stars", justify="center")
table.add_column("Watchers", justify="center")
table.add_column("Open Issues", justify="center")
for repo in repos:
    table.add_row(
        str(repo.github_id),
        str(repo.name),
        str(repo.forks_count),
        str(repo.stargazers_count),
        str(repo.watchers_count),
        str(repo.open_issues_count),
    )
console.print('\nRepository details\n'.upper())
console.print(table)
# Add snap record to the sessions
session.add(new_snap_record)
# Commit all to the database
session.commit()
