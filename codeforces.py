import requests
from bs4 import BeautifulSoup
import time
import os
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import time
import re
import csv
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('codeforces.log')
logger.addHandler(file_handler)

class CodeForcesCrawler:
    def __init__(self, save_path):
        self.url = "https://www.codeforces.com/"

        self.save_path = save_path

    def get_id_verdict_map(self, project):
        id_verdict_map = {}

        page_url = self.url + 'api/contest.status?contestId=' + project

        response = requests.get(page_url)
        results = response.json()['result']
        for result in tqdm(results):
            if result['programmingLanguage'] in ['Python 3', 'PyPy 3'] \
                and result['problem']['name'] == 'Merge Sort' \
                and result['verdict'] in ['OK', 'WRONG_ANSWER']:
                id_verdict_map[result['id']] = result['verdict']
        
        return id_verdict_map
    
    def get_submissions(self, project, id_verdict_map):
        submission_dict = {}
        failed_dict = {}

        submission_url = self.url + 'contest/' + project + '/submission/'
        count = 0

        for id, verdict in tqdm(id_verdict_map.items()):
            if count == 5:
                break
            page_url = submission_url + str(id)
            page = requests.get(page_url)
            soup = BeautifulSoup(page.text, "html.parser")
            try:
                code = soup.find('pre', {'id': 'program-source-text'}).text
                submission_dict[id] = [verdict, code]
                count += 1
            except:
                failed_dict[id] = verdict
                # logger.info(page_url)
        
        if failed_dict:
            rest_submission_dict = self.get_submissions(project, failed_dict)
            submission_dict.update(rest_submission_dict)
                
        return submission_dict


    def save(self, dir_path, file_path, data):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(file_path, 'w') as w:
            w.write(data.strip())

    def save_data(self, project, submission_dict):
        for id, (verdict, code) in tqdm(submission_dict.items()):
            dir_path = os.path.join(self.save_path, project, verdict)
            file_path = dir_path+'/'+str(id)+'&'+verdict+'&'+'.py'
            self.save(dir_path, file_path, code)


    def run_one(self, project):
        print('Get submission list...')
        id_verdict_map = self.get_id_verdict_map(project)
        print('Get submissions...')
        submission_dict = self.get_submissions(project, id_verdict_map)
        print('Save data...')
        self.save_data(project, submission_dict)

def recrawl():
    urls = open('codeforces.log').read()
    url_list = urls.split('\n')

    for page_url in url_list:
        page_url = 'https://www.codeforces.com/contest/873/submission/167504780'
        id = page_url.split('/')[-1]

        page = requests.get(page_url)
        soup = BeautifulSoup(page.text, "html.parser")
        code = soup.find('pre', {'id': 'program-source-text'}).text


cfc = CodeForcesCrawler('codeforceData/')
cfc.run_one('873')
