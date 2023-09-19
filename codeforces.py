import requests
from bs4 import BeautifulSoup
import time
import os
import warnings
from tqdm import tqdm
import logging
import csv
from csv import writer
import pandas as pd
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
# options.add_argument("headless")
options.add_argument('--window-size=1920, 1080')
options.add_argument('--no-sandbox')
options.add_argument("--disable-dev-shm-usage")
# options.add_argument('--start-maximized')
# options.add_argument('--start-fullscreen')
options.add_argument('--disable-blink-features=AutomationControlled')

# Save log 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('codeforces.log')
logger.addHandler(file_handler)


class CodeForcesCrawler:
    language = ['Python 3', 'PyPy 3', 'PyPy 3-64']
    
    def __init__(self, save_path):
        self.url = "https://codeforces.com/"
        self.mirror_url = "https://mirror.codeforces.com/"
        self.contest_url = self.url + "contest/"

        self.save_path = save_path
        
    def trans_status(self, status):
        status = "".join([word.upper() for word in status if word.strip()])
        if "ACCEPTED" in status:
            status = "AC"
        elif "REJECTED" in status:
            status = "PAC"
        elif "WRONGANSWER" in status:
            status = "WA"
        return status
    
    def set_extension(self, language):
        # TODO: change to UPPER
        language = "".join([word.upper() for word in language if word.strip()])
        if language in ['GNUC11', 'Clang++20Diagnostics', 'Clang++17Diagnostics', \
            'GNUC++14', 'GNUC++17', 'GNUC++20(64)', 'MSC++2017', 'GNUC++17(64)',]:
            extension = '.c' ## cpp .....
        elif language in ['PYTHON2', 'PYTHON3', 'PYPY2', 'PYPY3', 'PYPY3-64']:
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

    def set_language(self, language):
        language = "".join([word.upper() for word in language if word.strip()])
        if language == 'PYTHON3':
            self.language = ['Python 3', 'PyPy 3', 'PyPy 3-64']
        elif language == 'PYTHON':
            self.language = ['Python 2', 'PyPy 2']
        elif language == 'C++':
            self.language = ['C++17', 'C++14']
        elif language == 'C':
            self.language = ['C']
        elif language == 'JAVA':
            self.language = ['JAVA']
        
    def __wait_until_find(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)

    def get_contest_list(self):
        contest_list = []
        
        contest_api = self.url + 'api/contest.list'
        res = requests.get(contest_api)
        results = res.json()['result']
        
        for result in tqdm(results, desc="CONTEST"):
            contest_list.append(str(result['id']))
            
        # print(contest_list)
        return contest_list
    
    def get_problem_code_list(self, contest):
        driver = webdriver.Chrome(service=ChromeService(), options=options)
        problem_code_list = []
        
        problem_url = self.contest_url + contest
        driver.get(problem_url)
        print(problem_url)
        time.sleep(10)

        problem_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody'
        
        try:
            pb_list = self.__wait_until_find(driver, problem_xpath)
            children = pb_list.find_elements(By.XPATH, "./child::*")
            cnt = 0
            for elem in children:
                if cnt == 0:
                    cnt += 1
                    continue
                
                # tmp_list.append(contest + elem.text.split('\n')[0])
                problem_code_list.append(elem.text.split('\n')[0])
            ## ex. contest: 1842 problem: A
        except:
            print("No contest")
        
        return problem_code_list
    
    def get_problem_info(self, contest, problem_code):
        driver = webdriver.Chrome(service=ChromeService(), options=options)
        
        problem_url = self.contest_url + contest + "/problem/" + problem_code
        
        driver.get(problem_url)
        time.sleep(2)
        print(problem_url)
        
        # title = self.get_title(driver)
        # tags = self.get_tags(driver)
        problem = self.get_problem(driver)
        input_tc, output_tc = self.get_testcase(problem_url)
        
        ## retry
        # if title == '':
        #     title = self.get_title(driver)
        # if tags == []:
        #     tags = self.get_tags(driver)
        if problem == '':
            problem = self.get_problem(driver)
        if input_tc == '' or output_tc == '':
            input_tc, output_tc = self.get_testcase(problem_url)

        driver.quit()
        
        return problem, input_tc, output_tc
        
    def get_submission_url_list(self, contest, title, category):
        driver = webdriver.Chrome(service=ChromeService(), options=options)
        
        submission_url_list = []
        
        status_url = self.url + "contest/" + contest + '/status'
        driver.get(status_url)
        time.sleep(3)
        
        for lang in self.language:
            try:
                ## Filter
                tag = self.__wait_until_find(driver, '//*[@id="sidebar"]/div[4]/div[2]/form/div[2]/input[1]')
                action = ActionChains(driver)
                action.move_to_element(tag).perform()
                
                # Filter problem
                select=driver.find_element(By.XPATH, '//*[@id="frameProblemIndex"]')
                select.send_keys(title)
                
                # Filter verdict
                select=driver.find_element(By.XPATH, '//*[@id="verdictName"]')
                select.send_keys(category)
                
                # Filter language
                select=driver.find_element(By.XPATH, '//*[@id="programTypeForInvoker"]')
                select.send_keys(lang)
                
                self.__wait_and_click(driver, '//*[@id="sidebar"]/div[4]/div[2]/form/div[2]/input[1]')
            except:
                print("Submission Filter Error")

            ## Get submission url
            ## 현재 25개만 수집
            for i in tqdm(range(2, 27), desc="Submissions"):
                try:
                    url = self.__wait_until_find(driver, '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[' + str(i) + ']/td[1]/a')
                    
                    # print("url: " + url.text)
                    submission_url_list.append(url.text)
                except:
                    # print("End Submissions")
                    break
        # print(submission_url_list)
        
        return submission_url_list
    
    def get_tags(self, driver):
        tags = []

        tags_xpath = '//*[@id="sidebar"]/div[4]/div[2]'
        
        try: 
            tags_list = self.__wait_until_find(driver, tags_xpath)
            action = ActionChains(driver)
            action.move_to_element(tags_list).perform()
            
            children = tags_list.find_elements(By.XPATH, "./child::*")
            for elem in children:
                tags.append(elem.text)
            tags.pop() 
        except:
            print("Tags Fail")
        
        return tags      

    def get_title(self, driver):
        title = ''
        title_xpath = '//*[@id="pageContent"]/div[3]/div[2]/div/div[1]/div[1]'
        
        try: 
            time.sleep(0.1) # for prevent null
            title = self.__wait_until_find(driver, title_xpath).text
        except: 
            print("Title Fail")
            pass

        return title.strip()

    def get_problem(self, driver):
        problem = ""
        problem_xpath = '//*[@id="pageContent"]/div[3]/div[2]/div/div[2]'
        
        try: 
            problem_statement = self.__wait_until_find(driver, problem_xpath)
            children = problem_statement.find_elements(By.XPATH, './child::*')
        
            for elem in children:
                problem += elem.text.replace('\n', ' ')
        except: 
            print("Problem Fail")
            pass

        return problem.replace(".", ".\n")

    def get_testcase(self, problem_url):
        input_tc, output_tc = '', ''
        
        try:
            text = requests.get(problem_url)
            soup = BeautifulSoup(text.text, "html.parser")
            input_tc_list = soup.find_all("pre")[0]
            for el in input_tc_list:
                input_tc += el.text + '\n'
            # print(input_tc)
            output_tc = soup.find_all("pre")[1].get_text()
            # print(output_tc)
        except: 
            print("Testcase Fail")
            pass 
        
        return input_tc, output_tc

    def get_username(self, driver):
        username = ''
        username_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[2]/td[2]/a'
        
        try:
            username = self.__wait_until_find(driver, username_xpath).text
        except: 
            print("Username Fail")
            pass 
        return username
    
    def get_status(self, driver):
        status = ''
        status_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[2]/td[5]'
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
        return language, extension
    
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
    
    def get_problem_code(self, driver):
        problem_code = ''
        problem_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[2]/td[3]/a'
        try:
            problem_enter_code = self.__wait_until_find(driver, problem_xpath).text
            problem_code = str(list(filter(str.isalpha, problem_enter_code)))
        except:
            print("Problem Fail")
            pass 

        return problem_code
    
    def save_contest(self, contest, problem_code_list, datatime):
        f = open(self.save_path + 'contest.csv','a', newline='')
        wr = csv.writer(f)
        
        for problem_code in problem_code_list:
            wr.writerow([contest, problem_code, datatime])
        
        f.close()
    
    def save_problem(self, contest, problem_code, title, problem, tags, points, difficulty,solvedCount, input_tc, output_tc, datatime):
        # Save Problem
        f = open(self.save_path + 'problem.csv','a', newline='')
        wr = csv.writer(f)
        wr.writerow([contest, problem_code, title, problem, tags, points, difficulty, solvedCount, input_tc, output_tc, datatime])
        
        f.close()
    
    def save_code(self, contest, problem_code, submissionId, username, status, language, extension, code, datatime):
        # Save Code

        if status in ["AC"]:
            result = "correct"
        elif status in ["WA", "PAC"]:
            result = "wrong"
        else:
            result = "error" 

        file_path = self.save_path + 'code/' + str(contest) + '/' + problem_code + '/' + result + '/'  + username + '.csv'
        f = open(file_path,'a', newline='')
        wr = csv.writer(f)
        wr.writerow(['contest', 'problem_code', 'submissionId', 'username', 'status', 'language', 'extension', 'code', 'datatime'])
        wr.writerow([contest, problem_code, submissionId, username, result, language, extension, code, datatime])
        
        f.close()
    
    def save(self, file_path, data):
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)
        data.to_csv(self.save_path+file_path, index = False)
    
    def run_contest(self):
        contest_list = self.get_contest_list()[166:]
        for contest in tqdm(contest_list, desc='Save contest'):
            problem_code_list = self.get_problem_code_list(contest)
            datatime = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())
            self.save_contest(contest, problem_code_list, datatime)
            
    def run_problem(self):
        # title_list, tags_list, problem_list, input_tc_list, output_tc_list, problem_datatime_list = [],[],[],[],[],[]
        # contest_list = list(pd.read_csv(self.save_path + 'contest.csv')['contestID'])[3289:]
        # problem_code_list = list(pd.read_csv(self.save_path + 'contest.csv')['problemID'])[3289:]
        # for contest, problem_code in tqdm(zip(contest_list, problem_code_list), desc='Save Problem'):
        #     title, tags, problem, input_tc, output_tc = self.get_problem_info(str(contest), str(problem_code))
        #     datatime = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())

        #     self.save_problem(contest, problem_code, title, problem, tags, input_tc, output_tc, datatime)
        
        problem_api = self.url + 'api/problemset.problems'
        
        res = requests.get(problem_api)
        results = res.json()['result']['problems']
        problemStatistics = res.json()['result']['problemStatistics']
        num = 0
        for result in results:
            if result['contestId'] == 514 and result['index'] == "B":
                break
            num += 1
            
        
        for result, problemStatistic in tqdm(zip(results[num+1:], problemStatistics[num+1:]), desc="CONTEST"):  
            if 'contestId' in result.keys():
                contestID = result['contestId']
            else:
                continue
            if 'index' in result.keys():
                index = result['index']
            else:
                continue
            if contestID == problemStatistic['contestId'] and index ==  problemStatistic['index']:
                solvedCount = problemStatistic['solvedCount'] 
            else:
                continue
            
            rating = result['rating'] if 'rating' in result.keys() else 0
            points = result['points'] if 'points' in result.keys() else 0
            
            problem, input_tc, output_tc = self.get_problem_info(str(contestID), str(index))
            datatime = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())

            self.save_problem(contestID, index, result['name'], problem, result['tags'], points, rating, solvedCount, input_tc, output_tc, datatime)
        
            
    def run_code(self, lang):
        self.set_language(lang)
        submission_list = {}
        driver = webdriver.Chrome(service=ChromeService(), options=options)
        
        contest_list = list(pd.read_csv(self.save_path + 'problem_tmp.csv')['contestID'])
        problem_code_list = list(pd.read_csv(self.save_path + 'problem_tmp.csv')['problemID'])
        title_list = list(pd.read_csv(self.save_path + 'problem_tmp.csv')['title'])
        
        for contest, title, problem_code in tqdm(zip(contest_list, title_list, problem_code_list), desc='Save Code'):
            os.makedirs(self.save_path + 'code/' + str(contest) + '/' + problem_code + '/correct', exist_ok=True)
            os.makedirs(self.save_path + 'code/' + str(contest) + '/' + problem_code + '/wrong', exist_ok=True)
            
            for category in ['Accepted', 'Wrong Answer']:
                submission_url_list = self.get_submission_url_list(str(contest), str(title), category)
                for submissionId in tqdm(submission_url_list, desc='Submission'):
                    
                    # DO NOT USE MIRROR URL!
                    submission_url = self.contest_url + str(contest) + "/submission/" + str(submissionId)
                    
                    try:
                        driver.get(submission_url)
                        print(submission_url)
                        time.sleep(3)
                        
                        ## Get status, username, code, extension
                        username = self.get_username(driver)
                        status = self.get_status(driver)
                        language, extension = self.get_extension(driver)
                        code = self.get_code(driver)
                    # problem_code = self.get_problem_code(driver)
                    except:
                        ## do again
                        print("Submission Crawl Error")
                    
                    ## retry
                    if username == '':
                        username = self.get_username(driver)
                    if status == '':
                        status = self.get_status(driver)
                    if language == '' or extension == '':
                        language, extension = self.get_extension(driver)
                    if code == '':
                        code =self.get_code(driver)
                        
                    if status in ["AC"]:
                        result = "correct"
                    elif status in ["WA", "PAC"]:
                        result = "wrong"
                    else:
                        result = "error"
                        
                    file_path = self.save_path + 'code/' + str(contest) + '/' + problem_code + '/' + result + '/'  + username + '.csv'
                    dir_path = self.save_path + 'code/' + str(contest) + '/' + problem_code + '/' + result + '/'
            
                    ## Delete User Duplicate
                    ## Only Save Correct and Wrong
                    if os.path.isfile(file_path) == False and result in ['correct', 'wrong']:
                    # if status and username and code and language and extension:
                        ## Delete Code Duplicate
                        dup = False
                        file_list = os.listdir(dir_path)
                        for file in file_list:
                            tmp_code = pd.read_csv(dir_path + file)['code'][0]
                            # print(tmp_code)
                            # print(code)
                            if tmp_code == code:
                                dup = True
                                break
                        # submission_map[sub_id] = [username, status, language, extension, code]
                        if dup == False:
                            datatime = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())
                            self.save_code(contest, problem_code, submissionId, username, status, language, extension, code, datatime)
                    
                    # if status and username and code and language and extension:
                    #     # submission_url_list[int(submissionId)] = [username, status, language, extension, code]
                    #     datatime = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())
                    #     self.save_code(contest, problem_code, submissionId, username, status, language, extension, code, datatime)
        
        # return submission_list

if __name__ == '__main__':
    language = 'python3'
    contest = '1842'
    save_path = 'codeforcesData/'
    
    # Run CodeForcesCrawler with save_path
    cfc = CodeForcesCrawler(save_path)
    
    # First: Save contest
    # cfc.run_contest()
    
    # Second: Save problem
    # cfc.run_problem()
    
    # Third: Save code
    cfc.run_code(language)
    
    # cfc.get_contest_list()
    
    ## Run Only ONE Contest
    # result = cfc.run_one(contest, language)
    
    # for problem_code, (title, tags, problem, input_tc, output_tc, submission_list) in tqdm(result.items(), desc="Save"):
    #     cfc.save_data(contest, problem_code, title, tags, problem, input_tc, output_tc, submission_list)
    
    ## TODO: retry option