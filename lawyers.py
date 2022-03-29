import httpx
import pandas as pd
from tabulate import tabulate
import pygit2
from typing import Dict, List, Tuple
import glob
import os
import subprocess
from pathlib import Path

ORG_NAME = "supabase"
LANGUAGES = ['JavaScript', 'TypeScript']
DIRECTORY = "lawyers"



# Next let us convert all this to json

def fetch_repository_details(org_name: str, languages: List[str])-> List[Tuple]:
  """
  Returns URLs of repositories which are written in the language
  """
  resp = httpx.get(f"https://api.github.com/orgs/{ORG_NAME}/repos?type=all")
  repository_details = []
  for item in resp.json():
    if item.get('language') in LANGUAGES:
      repository_details.append((item.get('name'), item.get('clone_url')))
  return repository_details



def generate_unified_csv()-> str:
  """
  Go through all urls, generate csv and then combine csv
  """
  # for detail in repository_details:
  #  csv_name = generate_dependency_csv(detail)

  files = os.path.join(f"./{DIRECTORY}/csvs/*.csv")
  files = glob.glob(files)
  import pdb;pdb.set_trace()
  df = pd.concat(map(pd.read_csv, files), ignore_index=True)
  df.to_csv(Path('./lawyers/csvs/aggregate.csv'))
  with open('lawyers.txt', 'w') as f:
      f.write(tabulate(df))

  print(tabulate(df))


def generate_dependency_csv(detail: str)->str:
  """
  Clone repo, run command to generate file and then save as csv. Return name of csv
  """
  name, url = detail
  print(f"Generating for {name} with {url}")
  pygit2.clone_repository(url, f"./{DIRECTORY}/{name}/")
  print(f"Clone succeeded for {url}")
  os.chdir(f"./{DIRECTORY}/{name}")
  subprocess.check_call("npm install", shell=True)
  print("install succeeded")
  subprocess.check_call(f"npx npm-license-crawler --production --onlyDirectDependencies --csv ../csvs/{name}.csv", shell=True)
  os.chdir("../..")

if __name__ == "__main__":
  # generate_dependency_csv(("repository.surf", "https://github.com/supabase/repository.surf"))
  #repository_details = fetch_repository_details(ORG_NAME, LANGUAGES)
  generate_unified_csv()




