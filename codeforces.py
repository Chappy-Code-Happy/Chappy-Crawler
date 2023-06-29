import requests
from bs4 import BeautifulSoup
import time
import os
import warnings
from tqdm import tqdm
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains


warnings.filterwarnings('ignore')
options = Options()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
options.add_argument('user-agent=' + user_agent)
## for background
options.add_argument("headless")
options.add_argument('--window-size=1920, 1080')
options.add_argument('--no-sandbox')
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--start-maximized')
options.add_argument('--start-fullscreen')
options.add_argument('--disable-blink-features=AutomationControlled')

# Save log 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('codeforces.log')
logger.addHandler(file_handler)


class CodeForcesCrawler:
    
    def __init__(self, save_path):
        self.url = "https://codeforces.com/"
        self.mirror_url = "https://mirror.codeforces.com/"
        self.contest_url = self.url + "contest/"

        self.save_path = save_path
        
    def trans_status(self, status):
        # status = "".join([word.upper() for word in status if word.strip()])
        # if status in ["AC(FULL)", "AC", "CORRECT", "ACCEPTED", "CORRECTANSWER"]:
        #     status = "AC"
        # elif status in ["AC(PARTIAL)", "PAC"]:
        #     status = "PAC"
        # elif status in ["WA", "WRONG", "WRONGANSWER"]:
        #     status = "WA"
        return status
    
    def set_extension(self, language):
        language = "".join([word.upper() for word in language if word.strip()])
        if language in ['GNUC11', 'Clang++20Diagnostics', 'Clang++17Diagnostics', \
            'GNUC++14', 'GNUC++17', 'GNUC++20(64)', 'MSC++2017', 'GNUC++17(64)',]:
            extension = '.c' ## cpp .....
        elif language in ['Python2', 'Python3', 'PyPy2', 'PyPy3', 'PyPy3-64']:
            extension = '.py'
        elif language in ['C#8', 'C#10', 'MonoC#']:
            extension = '.cs'
        elif language == 'D':
            extension = '.D'
        elif language == 'GO':
            extension = '.go'
        elif language == 'Haskell':
            extension = '.chs'
        elif language in ['Java11', 'Java17', 'Java8']:
            extension = '.java'
        elif language in ['Kotlin1.6', 'Kotlin1.7']:
            extension = '.kt'
        elif language == 'Ocaml':
            extension = '.ml'
        elif language == 'JavaScript':
            extension = '.js'
        elif language == 'RUST2021':
            extension = '.rs'
        elif language == 'PHP':
            extension = '.php'
        elif language == 'Node.js':
            extension = '.js'
        elif language == 'Ruby3':
            extension = '.R'
        ## Delphi, FPC, PascalABC.NET, Perl, Scala
        else:
            extension = '.txt'
        
        return extension

        
    def __wait_until_find(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)

    def get_contest_list(self, driver):
        contest_list = []

        # page_url = self.mirror_url + 'api/contest.status?contestId=' + project + '&count=500' # just 10
        # print("API: " + page_url)

        # response = requests.get(page_url)
        # results = response.json()['result']
        # for result in tqdm(results):
        #     if result['programmingLanguage'] in ['Python 3', 'PyPy 3'] \
        #         and result['problem']['name'] == 'Merge Sort' \
        #         and result['verdict'] in ['OK', 'WRONG_ANSWER']:
        #         id_verdict_map[result['id']] = result['verdict']
        
        return contest_list
    
    def get_problem_list(self, contest):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        problem_list = {}
        
        problem_url = self.contest_url + contest
        driver.get(problem_url)
        time.sleep(1)

        problem_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody'
        
        try:
            pb_list = self.__wait_until_find(driver, problem_xpath)
            children = pb_list.find_elements(By.XPATH, "./child::*")
            cnt = 0
            tmp_list = []
            for elem in children:
                if cnt == 0:
                    cnt += 1
                    continue
                
                tmp_list.append(elem.text.split('\n')[1])
            problem_list[contest] = tmp_list
        except:
            print("Problem Error")
        
        return problem_list
    
    def get_submission_url_list(self, contest, language):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        submission_url_list = {}
        
        ## using miror_url -> because when click event occur, it rendering to 'mirror.codeforces.com'
        # status_url = self.mirror_url + "contest/" + contest + '/status'
        status_url = self.url + "contest/" + contest + '/status'
        driver.get(status_url)
        time.sleep(1)
        
        try:
            ## Filter Language
            tag = self.__wait_until_find(driver, '//*[@id="sidebar"]/div[4]/div[2]/form/div[2]/input[1]')
            action = ActionChains(driver)
            action.move_to_element(tag).perform()
            
            # just for python 3
            select=driver.find_element(By.XPATH, '//*[@id="programTypeForInvoker"]')
            select.send_keys(language)
            
            self.__wait_and_click(driver, '//*[@id="sidebar"]/div[4]/div[2]/form/div[2]/input[1]')
            time.sleep(1)
        except:
            print("Submission Filter Error")
            
        try:
            ## Get Last Page
            tag = self.__wait_until_find(driver, '//*[@id="pageContent"]/div[8]/div/ul')
            action = ActionChains(driver)
            action.move_to_element(tag).perform()
            
            children = tag.find_elements(By.XPATH, './child::*')
            
            for i in range(len(children)):
                if i == len(children)-2:
                    last_page = int(children[i].text)
            
            # print("last_page: " + str(last_page))
        except:
            print("Get Last Page Error")

        ## Get submission url
        tmp_list = []
        for j in tqdm(range(1, last_page+1), desc='Submission URL'): 
            for i in range (2, 52):
                try:
                    url = self.__wait_until_find(driver, '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[' + str(i) + ']/td[1]/a')
                    
                    # print("url: " + url.text)
                    tmp_list.append(url.text)
                except:
                    print("End Submissions")
                    break
            
            if j == last_page:
                break
            try:
                page_list = self.__wait_until_find(driver, '//*[@id="pageContent"]/div[8]/div/ul')
                next_btn = page_list.find_element(By.XPATH, './child::li/a[contains(text(), \'→\')]')
    
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(next_btn))
                driver.execute_script("arguments[0].click();", next_btn)
                
                ## add when last page
            except:
                break
        submission_url_list[contest] = tmp_list
        # print(submission_url_list)
        
        return submission_url_list
    
    def get_username(self, driver):
        username = ''
        username_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[2]/td[2]/a'
        
        try:
            username = self.__wait_until_find(driver, username_xpath)
        except: 
            print("Username Fail")
            pass 
        return username
    
    def get_status(self, driver):
        status = ''
        status_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[2]/td[5]/span'
        try:
            status = self.__wait_until_find(driver, status_xpath).text
            status = self.trans_status(status)
        except:
            print("Status Fail")
            pass 
        return status
    
    def get_extension(self, driver):
        extension = ''
        language_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[2]/td[4]'
        try:
            language = self.__wait_until_find(driver, language_xpath).text.split('Language:')[-1].strip()
            extension = self.set_extension(language)
        except:
            print("Extension Fail")
            pass 
        return extension
    
    def get_code(self, driver):
        code = ''
        code_xpath = '//*[@id="program-source-text"]/ol'
        try:
            code = self.__wait_until_find(driver, code_xpath).text
            # print("code: " + code)
        except:
            print("Code Fail")
            pass 

        return code
    
    def get_problem(self, driver):
        problem = ''
        problem_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[2]/td[3]/a'
        try:
            problem = self.__wait_until_find(driver, problem_xpath).text
        except:
            print("Problem Fail")
            pass 

        return problem
        
    def get_submission_list(self, contest, submission_url_list):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        submission_list = {}
        
        for sub_url in tqdm(submission_url_list[contest], desc='Sumission'):
            # DO NOT USE MIRROR URL!
            submission_url = self.contest_url + contest + "/submission/" + sub_url
            
            driver.get(submission_url)
            print(submission_url)
            time.sleep(3)
            
            ## Get status, username, code, extension
            username = self.get_username(driver)
            status = self.get_status(driver)
            extension = self.get_extension(driver)
            code = self.get_code(driver)
            problem = self.get_problem(driver)
            
            if status and username and code and extension and problem:
                submission_list[contest] = [status, username, code, extension]
        
        return submission_list

    def save(self, dir_path, file_path, data):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(file_path, 'w') as w:
            w.write(data.strip())

    # def save_data(self, contest, submission_dict):
        # for id, (verdict, code) in tqdm(submission_dict.items()):
        #     dir_path = os.path.join(self.save_path, contest, verdict)
        #     file_path = dir_path+'/'+str(id)+'&'+verdict+'&'+'.py'
        #     self.save(dir_path, file_path, code)

    def run_one(self, contest):
        print('Get contest problem list...')
        problem_list = self.get_problem_list(contest)
        # print("problem_list: " + str(problem_list))
        print('Get submission URL...')
        submission_url_list = self.get_submission_url_list(contest, "Python 3")
        print('Get submissions...')
        submission_list = self.get_submission_list(contest, submission_url_list)
        # print("submission_list: " + str(submission_list))
        # print('Save data...')
        # self.save_data(contest, submission_list)

# def recrawl():
#     urls = open('codeforces.log').read()
#     url_list = urls.split('\n')

#     for page_url in url_list:
#         page_url = 'https://www.codeforces.com/contest/873/submission/167504780'
#         id = page_url.split('/')[-1]

#         page = requests.get(page_url)
#         soup = BeautifulSoup(page.text, "html.parser")
#         code = soup.find('pre', {'id': 'program-source-text'}).text


if __name__ == '__main__':
    language = 'PYTH 3'
    
    save_path = 'codeforceData/'
    
    # Run CodeForcesCrawler with save_path
    cfc = CodeForcesCrawler(save_path)
    
    cfc.run_one('1842')
