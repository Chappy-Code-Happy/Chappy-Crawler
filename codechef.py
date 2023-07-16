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
file_handler = logging.FileHandler('codechef.log')
logger.addHandler(file_handler)

class CodeChefCrawler:
    # Set language and status
    # Default is "All"
    language = ['PYTH 3', 'PYPY3', 'PYTH', 'PYPY']
    status = ''

    def __init__(self, save_path):
        self.url = "https://www.codechef.com/"
        self.practice_url = self.url + "practice"
        self.problem_url = self.url + "problems/"
        self.status_url = self.url + "status/"
        self.user_url = self.url + "users/"
        
        self.save_path = save_path
    
    def set_language(self, language):
        language = "".join([word.upper() for word in language if word.strip()])
        if language == 'PYTHON':
            self.language = ['PYTH 3', 'PYPY3', 'PYTH', 'PYPY']
        elif language == 'C++':
            self.language = ['C++17', 'C++14']
        elif language == 'C':
            self.language = ['C']
        elif language == 'JAVA':
            self.language = ['JAVA']
        ## add
    
    def set_extension(self, language):
        language = "".join([word.upper() for word in language if word.strip()])
        if language in ['C']:
            extension = '.c'
        elif language in ['C++17', 'C++14']:
            extension = '.cpp'
        elif language in ['PYTH 3', 'PYPY3', 'PYTH', 'PYPY', 'PYTHON3', 'PYTHON']:
            extension = '.py'
        elif language == 'JAVA':
            extension = '.java'
        elif language == 'C#':
            extension = '.cs'
        elif language == 'ADA':
            extension = '.adb'
        elif language == 'TEXT':
            extension = '.txt'
        elif language == 'PASFPC':
            extension = '.pas'
        elif language == 'NODEJS':
            extension = '.js'
        elif language == 'RUBY':
            extension = '.rb'
        elif language == 'PHP':
            extension = '.php'
        elif language == 'GO':
            extension = '.go'
        elif language == 'HASK':
            extension = '.chs'
        elif language == 'TCL':
            extension = '.tcl'
        elif language == 'KTLN':
            extension = '.kt'
        elif language == 'PERL':
            extension = '.pl'
        elif language == 'SCALA':
            extension = '.scala'
        elif language == 'LUA':
            extension = '.lua'
        elif language == 'BASH':
            extension = '.sh'
        elif language == 'JS':
            extension = '.js'
        elif language == 'RUST':
            extension = '.rs'
        elif language == 'LISPSBCL':
            extension = '.lisp'
        elif language == 'R':
            extension = '.R'
        elif language == 'D':
            extension = '.D'
        elif language == 'CAML':
            extension = '.ml'
        elif language == 'SWIFT':
            extension = '.swift'
        elif language == 'FORT':
            extension = '.fourh'
        elif language == 'ASM':
            extension = '.asm'
        elif language == 'SQL':
            extension = '.sql'
        else:
            extension = '.txt'
        
        return extension

    def set_status(self, status):
        self.status = status

    def trans_status(self, status):
        status = "".join([word.upper() for word in status if word.strip()])
        if status in ["AC(FULL)", "AC", "CORRECT", "ACCEPTED", "CORRECTANSWER"]:
            status = "AC"
        elif status in ["AC(PARTIAL)", "PAC"]:
            status = "PAC"
        elif status in ["WA", "WRONG", "WRONGANSWER"]:
            status = "WA"
        return status

    def update_url(self, compete):
        # Update url in case of compete problem
        self.problem_url = self.url + compete + '/problems/'
        self.status_url = self.url + compete + '/status/'

    def __wait_until_find(self, driver, xpath):
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)

    def get_project_list(self):
        # Get the project url of all problems
        project_list = []

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        rows_per_page = 50
        url_a = self.practice_url + "?"
        url_b = "limit="+str(rows_per_page)+"&sort_by=difficulty_rating&sort_order=asc&search=&start_rating=0&end_rating=5000&topic=&tags=&group=all"
        page_url = url_a + "page=0&" + url_b

        driver.get(page_url)
        time.sleep(1)
        
        # print(page_url)
        page_path = '//*[@id="root"]/div/div[3]/div/div[2]/div/div[2]/div/div[3]/div/table/tfoot/tr/td/div/div[2]/div/p[2]'
        page_of_page = self.__wait_until_find(driver, page_path)
        
        action = ActionChains(driver)
        action.move_to_element(page_of_page).perform()
        last_page = int(page_of_page.text.split('of')[1].strip())
        jump_page = int(last_page/rows_per_page) + 1
        
        for no in tqdm(range(jump_page), desc='Projects'): # last_page
            page_url = url_a + "page=" + str(no) + "&" + url_b
            driver.get(page_url)
            time.sleep(1)
            
            for i in range(50):
                codename_xpath = '//*[@id="MUIDataTableBodyRow-'+str(i)+'"]/td[1]/div'
                try: codename = driver.find_element(By.XPATH, codename_xpath).text
                except: break
                project_list.append(codename)
        
        driver.quit()
        
        return project_list

    def get_tags(self, driver):
        tags = []

        expand_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[4]' # feat
        try:
            self.__wait_and_click(driver, expand_xpath)
        except:
            print("error")
        
        ## not necessory && error
        # show_tags_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[2]/div/div[2]/div/div'
        # self.__wait_and_click(driver, show_tags_xpath)

        tags_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[2]/div/div[2]/div/div[2]'
        
        try: 
            tags_list = self.__wait_until_find(driver, tags_xpath)
            
            children = tags_list.find_elements(By.XPATH, "./child::*")
            for elem in children:
                tags.append(elem.text)
        except:
            print("Tags Fail")
        
        return tags       

    def get_title(self, driver):

        title = ''
        title_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/h1'
        
        try: 
            time.sleep(1) # for prevent null
            title = self.__wait_until_find(driver, title_xpath).text
        except: 
            print("Title Fail")
            pass

        return title

    def get_problem(self, driver):
        problem = ""
        problem_xpath = '//*[@id="problem-statement"]'
        
        try: 
            problem_statement = self.__wait_until_find(driver, problem_xpath)
            children = problem_statement.find_elements(By.XPATH, './child::*')

            for elem in children:
                tag = elem.tag_name
                text = elem.text
                if tag in ['h2', 'h3']:
                    if text != 'Problem':
                        if not problem:
                            continue
                        break
                elif tag in ['li']:
                    problem += "\n - " + text.replace('\n', ' ')
                else:
                    problem += text.replace('\n', ' ')
        except: 
            print("Problem Fail")
            pass

        return problem.replace(".", ".\n")

    def get_difficulty(self, driver):
        difficulty = ''
        difficulty_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/span[2]'
        
        try: 
            difficulty = self.__wait_until_find(driver, difficulty_xpath).text
        except: 
            print("Difficulty Fail")
            pass

        return difficulty
    
    def get_testcase(self, project):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        input_tc, output_tc = '', ''

        page_url = self.url + "problems-old/" + project
        driver.get(page_url)

        input_x_paths = ['//*[@id="sample-input-1"]',
                        '//*[@id="problem-statement"]/pre[1]',
                        '//*[@id="problem-statement"]/pre',
                        '//*[@id="problem-statement"]/pre[1]/tt',
                        '//*[@id="problem-statement"]/pre[1]/code']
        
        output_x_paths = ['//*[@id="sample-output-1"]',
                        '//*[@id="problem-statement"]/pre[2]',
                        '//*[@id="problem-statement"]/pre',
                        '//*[@id="problem-statement"]/pre[2]/tt',
                        '//*[@id="problem-statement"]/pre[2]/code']
        
        for in_xpath, out_xpath in zip(input_x_paths, output_x_paths):
            try:
                if in_xpath == out_xpath:
                    ## error
                    input_tc, output_tc = self.__wait_until_find(driver, in_xpath).text
                else:
                    input_tc = self.__wait_until_find(driver, in_xpath).text
                    output_tc = self.__wait_until_find(driver, out_xpath).text
                if input_tc.strip() and output_tc.strip():
                    break
            except:
                input_tc = ''
                output_tc = ''
        
        driver.quit()
        return input_tc, output_tc

    def get_username(self, driver):
        username = ''
        username_xpath = '//*[@id="root"]/div/div[3]/div/div/div[2]/div/div[2]/a'
        try:
            time.sleep(1) # for prevent null
            username = self.__wait_until_find(driver, username_xpath).text
        except: 
            print("Username Fail")
            pass 
        return username
    
    def get_status(self, driver):
        status = ''
        status_xpath = '//*[@id="root"]/div/div[3]/div/div/div[2]/div/div[1]/div/span'
        try:
            status = self.__wait_until_find(driver, status_xpath).text
            status = self.trans_status(status)
        except:
            print("Status Fail")
            pass 
        return status
    
    def get_extension(self, driver):
        extension = ''
        language_xpath = '//*[@id="root"]/div/div[3]/div/div/div[4]/div/div/div/div[1]/div[1]'
        try:
            language = self.__wait_until_find(driver, language_xpath).text.split('Language:')[-1].strip()
            extension = self.set_extension(language)
        except:
            print("Extension Fail")
            pass 
        return language, extension
    
    def get_code(self, solution_url):
        try:
            plaintext_url = solution_url.replace("viewsolution", "viewplaintext")
            plaintext = requests.get(plaintext_url)
            soup = BeautifulSoup(plaintext.text, "html.parser")
            code = soup.find("pre").get_text()
        except:
            print("Code Fail")
            pass 

        return code
        
    def get_project_info(self, project):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        page_url = self.problem_url + project
        driver.get(page_url)
        print(page_url)

        time.sleep(3)
        
        title = self.get_title(driver)
        tags = self.get_tags(driver)
        problem = self.get_problem(driver)
        difficulty = self.get_difficulty(driver)
        input_tc, output_tc = self.get_testcase(project)

        ## retry
        if title == '':
            title = self.get_title(driver)
        if tags == []:
            tags = self.get_tags(driver)
        if problem == '':
            problem = self.get_problem(driver)
        if difficulty == '':
            difficulty = self.get_difficulty(driver)
        if input_tc == '' or output_tc == '':
            input_tc, output_tc = self.get_testcase(project)

        driver.quit()
        # print(title)
        return title, tags, problem, difficulty, input_tc, output_tc

    def get_submission_id_list(self, project):

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        submission_id_list = []
        
        for lang in self.language:
            url_a = self.status_url + project + "?"
            url_b = "limit=100&sort_by=All&sorting_order=asc&language="+lang+"&status="+self.status+"&handle=&Submit=GO"
            
            page_url = url_a + url_b
            print(page_url)
            
            driver.get(page_url)
            time.sleep(1)
                        
            for i in tqdm(range(25), desc="Submissions"):
                sub_xpath = '//*[@id="MUIDataTableBodyRow-' + str(i) + '"]/td[1]/div'
                try:
                    # Go to Submission code
                    sub_id = self.__wait_until_find(driver, sub_xpath)
                    action = ActionChains(driver)
                    action.move_to_element(sub_id).perform() # scroll
                    # print(sub_id.text)
                    submission_id_list.append(sub_id.text)
                except:
                    print("End")
                    break
                
        driver.quit()        
        
        return submission_id_list
    
    def get_user_info(self, username):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        page_url = self.problem_url + project
        driver.get(page_url)
        print(page_url)

        time.sleep(3)
    
    def save_project(self, project_list):
        df = pd.DataFrame(project_list, columns = ['projectID'])
        time_list = []
        for i in range(len(project_list)):
            time_list.append(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime()))
        df['datatime'] = time_list
        
        self.save("project.csv", df)
        
    def save_problem(self, project, title, problem, tags, difficulty, input_tc, output_tc, datatime):
        # Save Problem
        f = open(self.save_path + 'problem_new4.csv','a', newline='')
        wr = csv.writer(f)
        wr.writerow([project, title, problem, tags, difficulty, input_tc, output_tc, datatime])
        
        f.close()
    
    def save_code(self, project, submissionId, username, status, language, extension, code, datatime):
        # Save Code
        f = open(self.save_path + 'code3.csv','a', newline='')
        wr = csv.writer(f)
        
        if status in ["AC"]:
            result = "correct"
        elif status in ["WA", "PAC"]:
            result = "wrong"
        else:
            result = "error"
        wr.writerow([project, submissionId, username, result, language, extension, code, datatime])
        
        f.close()
    
    def save_username(self, username, datatime):
        # df = pd.DataFrame(username_list, columns = ['username'])
        # time_list = []
        # for i in range(len(username_list)):
        #     time_list.append(time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime()))
        # df['datatime'] = time_list
        
        # self.save("username.csv", df)
        f = open(self.save_path + 'username2.csv','a', newline='')
        wr = csv.writer(f)
        wr.writerow([username, datatime])
        
        f.close()
    
    def save(self, file_path, data):
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)  
        data.to_csv(self.save_path+file_path, index = False)
    
    def run_project(self):
        project_list = self.get_project_list()
        self.save_project(project_list)
        
    def run_problem(self):
        # title_list, tags_list, problem_list, input_tc_list, output_tc_list, problem_datatime_list = [],[],[],[],[],[]
        project_list = list(pd.read_csv(self.save_path + 'project.csv')['projectID'])[3408:]
        for project in tqdm(project_list, desc='Save Problem'):
            title, tags, problem, difficulty, input_tc, output_tc = self.get_project_info(project)
            datatime = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())

            self.save_problem(project, title, problem, tags, difficulty, input_tc, output_tc,  datatime)
            
    def run_code(self, language):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        submission_map = {}
        self.set_language(language)
        
        project_list = list(pd.read_csv(self.save_path + 'project.csv')['projectID'])[70:]
        for project in tqdm(project_list, desc='Save Code'):
            submission_id_list = self.get_submission_id_list(project)
            for sub_id in  tqdm(submission_id_list, desc='Save Submission'):
                code_url = self.url + 'viewsolution/' + sub_id
                print(code_url)
                driver.get(code_url)
                time.sleep(3)
                
                try:   
                    # Get status, username, code, extension, language
                    username = self.get_username(driver)
                    status = self.get_status(driver)
                    language, extension = self.get_extension(driver)
                    code = self.get_code(code_url)

                except:
                    print("Submission Error")
                
                ## retry
                if username == '':
                    username = self.get_username(driver)
                if status == '':
                    status = self.get_status(driver)
                if language == '' or extension == '':
                    language, extension = self.get_extension(driver)
                if code == '':
                    code = self.get_code(code_url)
                    
                if status and username and code and language and extension:
                    submission_map[sub_id] = [username, status, language, extension, code]
                    datatime = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())
                    self.save_code(project, sub_id, username, status, language, extension, code, datatime)
            
        driver.quit()
        # print(submission_map)
        return submission_map
    
    def run_username(self):
            
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        url_a = self.url + 'ratings/all?itemsPerPage=50&order=asc&page='
        
        driver.get('https://www.codechef.com/ratings/all?itemsPerPage=50&order=asc&page=1&sortBy=global_rank')
        time.sleep(3)
        
        ## Get last page
        try:
            last_page_xpath = '//*[@id="root"]/div/div[3]/div/div/div[2]/div[2]/div[2]/div/table/tfoot/tr/td/div[1]/nav/ul/li[8]/button'
            last_page = self.__wait_until_find(driver, last_page_xpath)
            action = ActionChains(driver)
            action.move_to_element(last_page).perform() # scroll
            last_page = self.__wait_until_find(driver, last_page_xpath).text
        except:
            print("Last Page Fail")
        
        username_list = []
        for i in tqdm(range(1, int(last_page)+1), desc="Username"):
            url = url_a + str(i) + '&sortBy=global_rank'
            
            driver.get(url)
            time.sleep(3)
            
            for j in range(50):
                username_xpath = '//*[@id="MUIDataTableBodyRow-' + str(j) + '"]/td[1]/div[2]/a/div/span[2]'
                try:
                    time.sleep(0.1)
                    username = self.__wait_until_find(driver, username_xpath).text
                    datatime = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())
                    self.save_username(username, datatime)
                    # print(username)
                    # username_list.append(username)
                except:
                    print("End")
                    break
        driver.quit()
        return username_list
    
    # def run_username(self):
    #     username_list = self.get_username_list()
    #     self.save_username(username_list)
        
    def get_csv(self, file_path):
        ## Get CSV file
        csv_mapping_list = []
        with open(file_path, 'rt', encoding='UTF8') as my_data:
            csv_reader = csv.reader(my_data, delimiter=",")
            line_count = 0
            for line in csv_reader:
                if line_count == 0:
                    header = line
                else:
                    row_dict = {key: value for key, value in zip(header, line)}
                    csv_mapping_list.append(row_dict)
                line_count += 1
        # return csv_mapping_list[58:]
        return csv_mapping_list 
        
if __name__ == '__main__':
    compete = 'UAPRAC' # Default is 'None'
    project = 'SEAFUNC'
    language = 'python' # Default is 'Language'
    status = '' # Default is ''

    save_path = 'codechefData/'
    
    # Run CodeChefCrawler with save_path
    ccc = CodeChefCrawler(save_path)
    ## First: Save project
    # ccc.run_project()
    
    ## Second: Save problem
    # ccc.run_problem()
    
    ## Third: Save code
    # ccc.run_code(language)
    
    ## Fourth: Save Username
    ccc.run_username()
        