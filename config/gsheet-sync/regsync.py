from bs4 import BeautifulSoup
import csv
import requests
import time
import os
import sys
import skopeoutil
import multiprocessing
import concurrent.futures

def run(sheet_url, sheet_idx, col, row, reg_url, docker_cred, quay_cred, gcr_cred, notify_to):
    registries = {
    'docker.io': {'regex': '^[a-z.]*docker.io/', 'credential': docker_cred},
    'quay.io': {'regex': '^[a-z.]*quay.io/', 'credential': quay_cred},
    'gcr': {'regex': '^[a-z.]*gcr.io/', 'credential': gcr_cred}}

    sheets = BeautifulSoup(requests.get(sheet_url).text, "lxml").find_all("table")
    table = ([[td.text for td in row.find_all("td")] for row in sheets[sheet_idx].find_all("tr")])

    skopeo = skopeoutil.SkopeoUtil(registries)
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=5)
    procs = []
    checked = {}
    for r in table[row:]:
        if len(r[col]) > 0:
            procs.append(pool.submit(skopeo.check_image, r[col]))
    for p in concurrent.futures.as_completed(procs):
        checked.update({p.result()[0]: p.result()[1]})

    copied = {}
    for r in table[row:]:
        if len(r[col]) > 0:
            procs.append(pool.submit(skopeo.copy_image, r[col], reg_url))
    for p in concurrent.futures.as_completed(procs):
        copied.update({p.result()[0]: p.result()[1]})

    results = {'sync': {}}
    for image in checked.keys():
        results['sync'][image] = { 'access':  checked[image], 'copied': copied[image] }

    response = requests.get(notify_to)
    results['upload'] = { 'status': response.status_code, 'msg': response.text }

    return results