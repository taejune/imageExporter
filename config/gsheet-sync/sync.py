from bs4 import BeautifulSoup
import csv
import requests
import time
import os
import sys
import subprocess
import re
import json

DEFAULT_URL = 'https://docs.google.com/spreadsheets/d/1zBHhKvdz5sv2HZFWGcbsvAVFspQAvm_yEYtY9ZffSZc/edit#gid=769436284'
DEFAULT_SHEET_NUMBER = 0
DEFAULT_ROW_FROM = 2
DEFAULT_COLUMN_NUMBER = 1
DEFAULT_REGISTRY_URL = "localhost:5000"

url_from = os.environ['SHEET_URL'] if os.environ.get('SHEET_URL') is not None else DEFAULT_URL
sheet_number = os.environ['SHEET_NUMBER'] if os.environ.get('SHEET_NUMBER') is not None else DEFAULT_SHEET_NUMBER
column_number = os.environ['COLUMN_NUMBER'] if os.environ.get('COLUMN_NUMBER') is not None else DEFAULT_COLUMN_NUMBER
row_from = os.environ['ROW_FROM'] if os.environ.get('ROW_FROM') is not None else DEFAULT_ROW_FROM
dest_reg = os.environ['REGISTRY_URL'] if os.environ.get('REGISTRY_URL') is not None else DEFAULT_REGISTRY_URL

dockerMatcher = re.compile(r'^[a-z.]*docker.io/')
quayMatcher = re.compile(r'[a-z.]*quay.io/')
gcrMatcher = re.compile(r'[a-z.]*gcr.io/')

# tables = BeautifulSoup(requests.get(url_from).text, "lxml").find_all("table")
# with open(time.strftime('%Y-%m-%d_%I:%M:%S%p', time.localtime()) + ".txt", "w") as f:
#     parsed=([[td.text for td in row.find_all("td")] for row in tables[sheet_number].find_all("tr")])
#     for row in parsed[row_from:]:
#         f.write(row[column_number] + '\n')

dockerio_credential=''
quayio_credential=''
gcr_credential=''

def check_image_by_subprocess(image, cred):
    CMD = """skopeo inspect --creds={CRED} docker://{IMAGE}"""
    try:
        print(CMD.format(CRED=cred, IMAGE=image))
        subprocess.run(CMD.format(CRED=cred, IMAGE=image), check=True, shell=True)
    except subprocess.SubprocessError as e:
        print(e)

def copy_image_by_subprocess(image, cred, copy_to):
    CMD = """skopeo copy --src-creds={CRED} --dest-tls-verify=false docker://{IMAGE} docker://{DEST}/{IMAGE}"""
    try:
        print(CMD.format(CRED=cred, IMAGE=image, DEST=copy_to))
        subprocess.run(CMD.format(CRED=cred, IMAGE=image, DEST=copy_to), check=True, shell=True)
    except subprocess.SubprocessError as e:
        sys.exit(e)

tables = BeautifulSoup(requests.get(url_from).text, "lxml").find_all("table")
parsed=([[td.text for td in row.find_all("td")] for row in tables[sheet_number].find_all("tr")])

targets = {}
for row in parsed[row_from:]:
    targets[row[column_number]] = { 'exist': False, 'copied': False }

for row in parsed[row_from:]:
    image_path = row[column_number]
    if dockerMatcher.search(image_path) != None:
        check_image_by_subprocess(image_path, dockerio_credential)
    elif quayMatcher.search(image_path) != None:
        check_image_by_subprocess(image_path, quayio_credential)
    elif gcrMatcher.search(image_path) != None:
        check_image_by_subprocess(image_path, gcr_credential)
    else:
        check_image_by_subprocess(image_path, dockerio_credential)

for row in parsed[row_from:]:
    image_path = row[column_number]
    if dockerMatcher.search(image_path) != None:
        copy_image_by_subprocess(image_path, dockerio_credential, dest_reg)
    elif quayMatcher.search(image_path) != None:
        copy_image_by_subprocess(image_path, quayio_credential, dest_reg)
    elif gcrMatcher.search(image_path) != None:
        copy_image_by_subprocess(image_path, gcr_credential, dest_reg)
    else:
        copy_image_by_subprocess(image_path, dockerio_credential, dest_reg)


with open(time.strftime('%Y-%m-%d_%I:%M:%S%p', time.localtime()) + ".json", "w") as f:
    json.dump(targets, f)
