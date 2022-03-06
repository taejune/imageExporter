from bs4 import BeautifulSoup
import csv
import requests
import time
import os
import sys
import skopeoutil
import json
import multiprocessing
import concurrent.futures

DEFAULT_URL = 'https://docs.google.com/spreadsheets/d/1zBHhKvdz5sv2HZFWGcbsvAVFspQAvm_yEYtY9ZffSZc/edit#gid=769436284'
DEFAULT_SHEET_NUMBER = 0
DEFAULT_ROW_FROM = 2
DEFAULT_COLUMN_NUMBER = 1
DEFAULT_REGISTRY_URL = "localhost:5000"
DEFAULT_OUTPUT_DIR = "."

url_from = os.environ['SHEET_URL'] if os.environ.get('SHEET_URL') is not None else DEFAULT_URL
sheet_number = os.environ['SHEET_NUMBER'] if os.environ.get('SHEET_NUMBER') is not None else DEFAULT_SHEET_NUMBER
image_idx = os.environ['COLUMN_NUMBER'] if os.environ.get('COLUMN_NUMBER') is not None else DEFAULT_COLUMN_NUMBER
row_from = os.environ['ROW_FROM'] if os.environ.get('ROW_FROM') is not None else DEFAULT_ROW_FROM
dest_reg = os.environ['REGISTRY_URL'] if os.environ.get('REGISTRY_URL') is not None else DEFAULT_REGISTRY_URL
output_dir = os.environ['OUTPUT_DIR'] if os.environ.get('OUTPUT_DIR') is not None else DEFAULT_OUTPUT_DIR

dockerio_credential = os.environ['DOCKER_CRED'] if os.environ.get('DOCKER_CRED') is not None else ''
quayio_credential = os.environ['QUAY_CRED'] if os.environ.get('QUAY_CRED') is not None else ''
gcr_credential = os.environ['GCR_CRED'] if os.environ.get('GCR_CRED') is not None else ''

registries = {
'docker.io': {'regex': '^[a-z.]*docker.io/', 'credential': dockerio_credential},
'quay.io': {'regex': '^[a-z.]*quay.io/', 'credential': quayio_credential},
'gcr': {'regex': '^[a-z.]*gcr.io/', 'credential': gcr_credential}}

sheets = BeautifulSoup(requests.get(url_from).text, "lxml").find_all("table")
table = ([[td.text for td in row.find_all("td")] for row in sheets[sheet_number].find_all("tr")])

now = time.strftime('%Y-%m-%d_%I:%M:%S%p', time.localtime())
filename = now + ".json"

if os.path.isdir(output_dir):
    filename = os.path.join(output_dir, filename)

with open(filename, "w") as f:
    skopeo = skopeoutil.SkopeoUtil(registries)
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=4)

    checking_procs = []
    checked = {}
    for row in table[row_from:]:
        if len(row[image_idx]) > 0:
            checking_procs.append(pool.submit(skopeo.check_image, row[image_idx]))
    for p in concurrent.futures.as_completed(checking_procs):
        checked.update({p.result()[0]: p.result()[1]})

    copying_procs = []
    copied = {}
    for row in table[row_from:]:
        if len(row[image_idx]) > 0:
            copying_procs.append(pool.submit(skopeo.copy_image, row[image_idx], dest_reg))
    for p in concurrent.futures.as_completed(copying_procs):
        copied.update({p.result()[0]: p.result()[1]})

    results = {}
    for image in checked.keys():
        results[image] = { 'access':  checked[image], 'copied': copied[image] }

    json.dump(results, f)