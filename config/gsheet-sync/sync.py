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

dockerio_credential = os.environ['DOCKER_CRED'] if os.environ.get('DOCKER_CRED') is not None else ''
quayio_credential = os.environ['QUAY_CRED'] if os.environ.get('QUAY_CRED') is not None else ''
gcr_credential = os.environ['GCR_CRED'] if os.environ.get('GCR_CRED') is not None else ''

registries = {
'docker.io': {'regex': '^[a-z.]*docker.io/', 'credential': dockerio_credential},
'quay.io': {'regex': '^[a-z.]*quay.io/', 'credential': quayio_credential},
'gcr': {'regex': '^[a-z.]*gcr.io/', 'credential': gcr_credential}}

class SkopeoUtil:
    CHECKCMD = 'skopeo inspect docker://{IMAGE}'
    CHECKCMD_WITH_CRED = 'skopeo inspect --creds={CRED} docker://{IMAGE}'
    COPYCMD = 'skopeo copy --dest-tls-verify=false docker://{IMAGE} docker://{DEST}/{IMAGE}'
    COPYCMD_WITH_CRED = 'skopeo copy --src-creds={CRED} --dest-tls-verify=false docker://{IMAGE} docker://{DEST}/{IMAGE}'

    def __init__(self, registries):
        self.registries = registries

    def check_image(self, name):
        print('check', name)
        for reg in self.registries.values():
            if re.compile(reg['regex']).search(name) != None:
                try:
                    if len(reg['credential']) > 0:
                        subprocess.run(self.CHECKCMD_WITH_CRED.format(IMAGE=name, CRED=reg['credential']), check=True, shell=True, capture_output=True)
                    else:
                        subprocess.run(self.CHECKCMD.format(IMAGE=name), check=True, shell=True, capture_output=True)
                    return True
                except subprocess.SubprocessError as e:
                    return False
        try:
            subprocess.run(self.CHECKCMD_WITH_CRED.format(IMAGE=name, CRED=self.registries['docker.io']['credential']), check=True, shell=True, capture_output=True)
            return True
        except subprocess.SubprocessError as e:
            return False

    def copy_image(self, name, copy_to):
        print('copy', name)
        for reg in self.registries.values():
            if re.compile(reg['regex']).search(name) != None:
                if len(reg['credential']) > 0:
                    subprocess.run(self.COPYCMD_WITH_CRED.format(IMAGE=name, CRED=reg['credential'], DEST=copy_to), check=True, shell=True, capture_output=True)
                else:
                    subprocess.run(self.COPYCMD.format(IMAGE=name, DEST=copy_to), check=True, shell=True, capture_output=True)
                return True
        try:
            subprocess.run(self.COPYCMD_WITH_CRED.format(IMAGE=name, CRED=self.registries['docker.io']['credential'], DEST=copy_to), check=True, shell=True, capture_output=True)
            return True
        except subprocess.SubprocessError as e:
            return False

tables = BeautifulSoup(requests.get(url_from).text, "lxml").find_all("table")
parsed = ([[td.text for td in row.find_all("td")] for row in tables[sheet_number].find_all("tr")])

with open(time.strftime('%Y-%m-%d_%I:%M:%S%p', time.localtime()) + ".json", "w") as f:
    skopeo = SkopeoUtil(registries)
    results = {}
    for row in parsed[row_from:]:
        if len(row[column_number]) > 0:
            results[row[column_number]] = { 'exist': skopeo.check_image(row[column_number]), 'copied': False }

    for row in parsed[row_from:]:
        if len(row[column_number]) > 0:
            try:
                results[row[column_number]]['copied'] = skopeo.copy_image(row[column_number], dest_reg)
            except subprocess.SubprocessError as e:
                print(e)
            finally:
                json.dump(results, f)

