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
        status = "".join([word.upper() for word in status if word.strip()])
        if status in ["ACCEPTED"]:
            status = "AC"
        elif status in ["REJECTED"]:
            status = "PAC"
        elif status in ["WRONGANSWER"]:
            status = "WA"
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
    
    def get_problem_code_list(self, contest):
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
                
                # tmp_list.append(contest + elem.text.split('\n')[0])
                tmp_list.append(elem.text.split('\n')[0])
            ## ex. contest: 1842 problem: A
            problem_list[contest] = tmp_list
        except:
            print("Problem Error")
        
        return problem_list
    
    def get_problem_info(self, contest, problem_code):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        problem_url = self.contest_url + contest + "/problem/" + problem_code
        
        driver.get(problem_url)
        time.sleep(1)
        print(problem_url)
        
        title = self.get_title(driver)
        tags = self.get_tags(driver)
        problem = self.get_problem(driver)
        input_tc, output_tc = self.get_testcase(problem_url)
        
        if not title:
            logger.info('No Title')
        if not tags:
            logger.info('No Tags')
        if not problem:
            logger.info('No Problem')
        if not input_tc or not output_tc:
            logger.info('No Testcase')

        driver.quit()
        
        return title, tags, problem, input_tc, output_tc
        
    def get_submission_url_list(self, contest, language, title):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        submission_url_list = {}
        last_page = 0
        
        status_url = self.url + "contest/" + contest + '/status'
        driver.get(status_url)
        time.sleep(1)
        
        try:
            ## Filter
            tag = self.__wait_until_find(driver, '//*[@id="sidebar"]/div[4]/div[2]/form/div[2]/input[1]')
            action = ActionChains(driver)
            action.move_to_element(tag).perform()
            
            # Filter problem
            select=driver.find_element(By.XPATH, '//*[@id="frameProblemIndex"]')
            select.send_keys(title)
            
            # Filter language
            select=driver.find_element(By.XPATH, '//*[@id="programTypeForInvoker"]')
            select.send_keys(language)
            
            self.__wait_and_click(driver, '//*[@id="sidebar"]/div[4]/div[2]/form/div[2]/input[1]')
        except:
            print("Submission Filter Error")
            time.sleep(100)
        
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
            last_page = 1
            # print("Get Last Page Error")

        ## Get submission url
        tmp_list = []
        for j in tqdm(range(1, last_page+1), desc='Submission URL'): 
            for i in range (2, 52):
                try:
                    url = self.__wait_until_find(driver, '//*[@id="pageContent"]/div[2]/div[6]/table/tbody/tr[' + str(i) + ']/td[1]/a')
                    
                    # print("url: " + url.text)
                    tmp_list.append(url.text)
                except:
                    # print("End Submissions")
                    break
                
            try:
                page_list = self.__wait_until_find(driver, '//*[@id="pageContent"]/div[8]/div/ul')
                next_btn = page_list.find_element(By.XPATH, './child::li/a[contains(text(), \'→\')]')
    
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(next_btn))
                driver.execute_script("arguments[0].click();", next_btn)
                
            except:
                continue
        submission_url_list[contest] = tmp_list
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
            
        except: 
            print("Problem Fail")
            pass
        
        children = problem_statement.find_elements(By.XPATH, './child::*')
        
        for elem in children:
            problem += elem.text.replace('\n', ' ')

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
            username = self.__wait_until_find(driver, username_xpath)
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
        
    def get_submission_list(self, contest, submission_url_list):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        submission_list = {}
        
        # print(submission_url_list)
        
        for submissionId in tqdm(submission_url_list[contest], desc='Sumission'):
            # DO NOT USE MIRROR URL!
            submission_url = self.contest_url + contest + "/submission/" + submissionId
            
            driver.get(submission_url)
            # print(submission_url)
            time.sleep(3)
            
            ## Get status, username, code, extension
            username = self.get_username(driver)
            status = self.get_status(driver)
            extension = self.get_extension(driver)
            code = self.get_code(driver)
            # problem_code = self.get_problem_code(driver)
            
            if status and username and code and extension:
                submission_list[submissionId] = [status, username, code, extension]
        
        return submission_list
    
    def save_problem(self, contest, problem_code, problem, title, tags):
        # Save Problem
        dir_path = os.path.join(self.save_path, contest, problem_code)
        file_path = dir_path+"/problem.txt"
        describtion = 'Title: %s\nProblem:\n%s\nTags:%s' %(title, problem, tags) 
        self.save(dir_path, file_path, describtion)

    def save_testcase(self, contest, problem_code, input_tc, output_tc):
        # Save Testcase
        dir_path = os.path.join(self.save_path, contest, problem_code, 'testcases')
        file_path = dir_path+"/input_001.txt"
        self.save(dir_path, file_path, input_tc)
        file_path = dir_path+"/output_001.txt"
        self.save(dir_path, file_path, output_tc)
    
    def save_code(self, contest, problem_code, submissionId, status, username, code, extension):
        # Save Code
        status = "".join([word.upper() for word in status if word.strip()])
        if status in ["AC"]:
            result = "correct"
        elif status in ["WA", "PAC"]:
            result = "wrong"
        else:
            result = "error"
            
        dir_path = os.path.join(self.save_path, contest, problem_code, result)
        file_path = dir_path+'/'+str(submissionId)+'&'+status+'&'+str(username)+extension
        self.save(dir_path, file_path, code)
    
    def save_datatime(self, contest, problem_code):
        # Save DateTime
        times = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())
        dir_path = os.path.join(self.save_path, contest, problem_code)
        file_path = dir_path+"/saved_date_time.txt"
        self.save(dir_path, file_path, times)

    def save(self, dir_path, file_path, data):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(file_path, 'w') as w:
            w.write(data.strip())

    ## In ONE contest and problem_code
    def save_data(self, contest, problem_code, title, tags, problem, input_tc, output_tc, submission_list):
        self.save_problem(contest, problem_code, problem, title, tags)
        self.save_testcase(contest, problem_code, input_tc, output_tc)
        for submissionId, (status, username, code, extension) in tqdm(submission_list.items(), desc='Save ONE'):
            self.save_code(contest, problem_code, submissionId, status, username, code, extension)
        self.save_datatime(contest, problem_code)

    ## In ONE contest 
    def run_one(self, contest, language="LANGUAGE"):
        result = {}
        print('Get contest problem list...')
        problem_code_list = self.get_problem_code_list(contest)
        # print("problem_list: " + str(problem_list))
        for problem_code in tqdm(problem_code_list[contest], "Contest Problem"):
            ## In ONE problem
            print("Get problem info...\n")
            title, tags, problem, input_tc, output_tc = self.get_problem_info(contest, problem_code)
            print('Get submission URL...\n')
            submission_url_list = self.get_submission_url_list(contest, language, title)
            print('Get submissions...\n')
            submission_list = self.get_submission_list(contest, submission_url_list)
            print("submission_list: " + str(submission_list))
            result[problem_code] = [title, tags, problem, input_tc, output_tc, submission_list]
        return result


if __name__ == '__main__':
    language = 'Python 3'
    contest = '1842'
    save_path = 'codeforceData/'
    
    # Run CodeForcesCrawler with save_path
    cfc = CodeForcesCrawler(save_path)
    
    ## Run Only ONE Contest
    result = cfc.run_one(contest, language)
    
    for problem_code, (title, tags, problem, input_tc, output_tc, submission_list) in tqdm(result.items(), desc="Save"):
        cfc.save_data(contest, problem_code, title, tags, problem, input_tc, output_tc, submission_list)