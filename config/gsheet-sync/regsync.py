from bs4 import BeautifulSoup
import csv
import requests
import time
import os
import sys
import re
import skopeoutil
import multiprocessing
import concurrent.futures

registries = {
    'docker.io': {'regex': re.compile('^[a-z.]*docker.io/'), 'cred': ''},
    'quay.io': {'regex': re.compile('^[a-z.]*quay.io/'), 'cred': ''},
    'gcr': {'regex': re.compile('^[a-z.]*gcr.io/'), 'cred': ''}
}

def run(sheet_url, sheet_idx, col, start, reg_url, docker_cred, quay_cred, gcr_cred, notify_to):
    sheets = BeautifulSoup(requests.get(sheet_url).text, "lxml").find_all("table")
    table = ([[td.text for td in tr.find_all("td")] for tr in sheets[sheet_idx].find_all("tr")])
#     pool = concurrent.futures.ProcessPoolExecutor(max_workers=2)
#     procs = []
#     for r in table[start:]:
#         if len(row[col]) > 0:
#             print('Copying image', row[col])
#             procs.append(pool.submit(skopeo.copy_image, row[col], reg_url))
#     for p in concurrent.futures.as_completed(procs):
#         print('{img} copied {stat}'.format(img=p.result()[0], stat=p.result()[1]))
#         copied.update({p.result()[0]: p.result()[1]})
    registries['docker.io']['cred'] = docker_cred
    registries['quay.io']['cred'] = quay_cred
    registries['gcr']['cred'] = gcr_cred
    skopeo = skopeoutil.SkopeoUtil(registries)

    successList = []
    failList = []
    for name in [row[col] for row in table[start:] if len(row[col]) > 0]:
        img, ok, reason = skopeo.copy_image(name, reg_url)
        if ok:
            print('Copying {img} success'.format(img=img))
            successList.append(img)
        else:
            print('[WARN] Copying {img} failed... (reason: {reason})'.format(img=img, reason=reason))
            failList.append({img: reason})

    results = {'sync': {}}
    results['sync']['success'] = successList
    results['sync']['failed'] = failList
    return results