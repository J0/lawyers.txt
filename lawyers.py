import httpx
import pandas as pd
from tabulate import tabulate
import pygit2
import logging
from typing import Dict, List, Tuple
import glob
import os
import subprocess
from pathlib import Path

ORG_NAME = "supabase"
DIRECTORY = "lawyers"


# Next let us convert all this to json

def fetch_repository_details(org_name: str) -> List[Tuple]:
    """
    Returns URLs of repositories which are written in the language
    """
    resp = httpx.get(f"https://api.github.com/orgs/{ORG_NAME}/repos?type=all")
    repository_details = []
    for item in resp.json():
        repository_details.append(
            (item.get('name'), item.get('clone_url'), item.get('language')))
    return repository_details


def generate_unified_csv(repo_details: List[Tuple], exclude=None) -> str:
    """
    Go through all urls, generate csv and then combine csv
    """
    import pdb
    pdb.set_trace()
    for repo in repo_details:
        name, url, language = repo
        if language in exclude:
            continue
        generate_dependency_csv(repo)

    files = os.path.join(f"./{DIRECTORY}/csvs/*.csv")
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    df.to_csv(Path('./lawyers/csvs/aggregate.csv'))
    with open('lawyers.txt', 'w') as f:
        f.write(tabulate(df))

    print(tabulate(df))


def generate_dependency_csv(detail: str):
    """
    Clone repo, run command to generate file and then save as csv. Return name of csv
    """
    name, url, language = detail
    logging.info(f"Generating for {name} with {url}")
    pygit2.clone_repository(url, f"./{DIRECTORY}/{name}/")
    logging.info(f"Clone succeeded for {url}")
    # Check type of job
    if language in ['JavaScript', 'TypeScript']:
        subprocess.check_call("npm install", shell=True)
        logging.info("install succeeded")
        subprocess.check_call(
            f"npx npm-license-crawler --production --onlyDirectDependencies --csv ../../csvs/{name}.csv", shell=True)
    else:
        subprocess.check_call(
            f"license_finder report --prepare --save=../../csvs/{name}.csv --format=csv", shell=True)
        # Run license_checker
    os.chdir("../..")


if __name__ == "__main__":
    repository_details = fetch_repository_details(ORG_NAME)
    # Go through details and check details if details  match then generate
    generate_unified_csv(repository_details, exclude=[
                         'TypeScript', 'JavaScript'])
