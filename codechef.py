import requests
from bs4 import BeautifulSoup
import time
import os
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import time
import logging


warnings.filterwarnings('ignore')
options = Options()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
options.add_argument('user-agent=' + user_agent)
options.add_argument("headless")
# options.add_argument('--window-size= x, y')
options.add_argument('--window-size=1920, 1080')
options.add_argument('--no-sandbox')
# options.add_argument("--single-process")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--start-maximized')
options.add_argument('--start-fullscreen')
# options.add_argument('--disable-blink-features=AutomationControlled')

# Save log
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('codechef.log')
logger.addHandler(file_handler)


class CodeChefCrawler:
    # Set language and status
    # Default is "All"
    language = "All"
    status = "All"

    def __init__(self, save_path):
        self.url = "https://www.codechef.com/"
        self.practice_url = self.url + "practice"
        self.problem_url = self.url + "problems/"
        self.status_url = self.url + "status/"
        
        self.save_path = save_path
        
    def set_language(self, language):
        language = "".join([word.upper() for word in language if word.strip()])
        if language in ['LANGUAGE', 'ALL']:
            self.language = 'All'
        elif language in ['C++17', 'C++']:
            self.language = '63'
        elif language in ['PYTH3.6', 'PY3', 'PY36', 'PYTHON3', 'PYTH3']:
            self.language = '116'
        elif language == 'JAVA':
            self.language = '10'
        elif language == 'C':
            self.language = '11'
        elif language == 'C++14':
            self.language = '44'
        elif language in ['PYTH', 'PY27', 'PY2', 'PYTHON']:
            self.language = '4'
        elif language == 'PYPY3':
            self.language = '109'
        elif language == 'C#':
            self.language = '27'
        elif language == 'ADA':
            self.language = '7'
        elif language == 'PYPY':
            self.language = '99'
        elif language == 'TEXT':
            self.language = '62'
        elif language == 'PASFPC':
            self.language = '22'
        elif language == 'NODEJS':
            self.language = '56'
        elif language == 'RUBY':
            self.language = '17'
        elif language == 'PHP':
            self.language = '29'
        elif language == 'GO':
            self.language = '114'
        elif language == 'HASK':
            self.language = '21'
        elif language == 'TCL':
            self.language = '38'
        elif language == 'KTLN':
            self.language = '47'
        elif language == 'PERL':
            self.language = '3'
        elif language == 'SCALA':
            self.language = '39'
        elif language == 'LUA':
            self.language = '26'
        elif language == 'BASH':
            self.language = '28'
        elif language == 'JS':
            self.language = '35'
        elif language == 'RUST':
            self.language = '93'
        elif language == 'LISPSBCL':
            self.language = '31'
        elif language == 'PASGPC':
            self.language = '2'
        elif language == 'BF':
            self.language = '12'
        elif language == 'CLOJ':
            self.language = '111'
        elif language == 'R':
            self.language = '117'
        elif language == 'D':
            self.language = '20'
        elif language == 'CAML':
            self.language = '8'
        elif language == 'SWIFT':
            self.language = '85'
        elif language == 'FORT':
            self.language = '5'
        elif language == 'ASM':
            self.language = '13'
        elif language == 'F#':
            self.language = '124'
        elif language == 'WSPC':
            self.language = '6'
        elif language == 'LISPCLISP':
            self.language = '32'
        elif language == 'SQL':
            self.language = '40'
        elif language == 'SCMGUILE':
            self.language = '33'
        elif language == 'PERL6':
            self.language = '54'
        elif language == 'ERL':
            self.language = '36'
        elif language == 'CLPS':
            self.language = '14'
        elif language == 'PRLG':
            self.language = '15'
        elif language == 'SQLQ':
            self.language = '52'
        elif language == 'ICK':
            self.language = '9'
        elif language == 'NICE':
            self.language = '25'
        elif language == 'ICON':
            self.language = '16'
        elif language == 'COB':
            self.language = '118'
        elif language == 'SCMCHICKEN':
            self.language = '97'
        elif language == 'PIKE':
            self.language = '19'
        elif language == 'SCMQOBI':
            self.language = '18'
        elif language == 'ST':
            self.language = '23'
        elif language == 'NEM':
            self.language = '30'
        else:
            print("NO Exisiting Language.\nPlease Check Possible Language in CodeChef Language index.")
            exit(0)
    
    def get_extension(self, language):
        language = "".join([word.upper() for word in language if word.strip()])
        if language in ['C++17', 'C++', 'C++14', 'C']:
            extension = '.c'
        elif language in ['PYTH3.6', 'PY3', 'PY36', 'PYTHON3', 'PYTH', 'PY27', 'PY2', 'PYTHON', 'PYPY3', 'PYPY', 'PYTH3']:
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
        status = "".join([word.upper() for word in status if word.strip()])
        if status in ["STATUS", "ALL"]:
            self.status = "All"
        elif status in ["AC(FULL)", "AC", "CORRECT", "ACCEPTED", "CORRECTANSWER"]:
            self.status = "FullAC"
        elif status in ["AC(PARTIAL)", "PAC"]:
            self.status = "PartialAC"
        elif status in ["WA", "WRONG", "WRONGANSWER"]:
            self.status = "14"
        elif status in ["TLE", "TIME", "TIMEOUT", "LIMIT", "EXCEEDED", "TIMELIMITEXCEEDED"]:
            self.status = "13"
        elif status in ["RTE", "RUN", "RUNTIME", "RUNTIMEERROR"]:
            self.status = "12"
        elif status in ["CTE", "COMPILE", "COMPILATION", "ERROR", "COMPILATIONERROR"]:
            self.status = "11"
        elif status == "IE":
            self.status = "20"
        else:
            print("NO Exisiting Status.\nPlease Check Possible Status in CodeChef Status index.")
            exit(0)

    def get_status(self, status):
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
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = driver.find_element(By.XPATH, xpath)
        return element
            
    def __wait_and_click(self, driver, xpath):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", button)

    def get_project_list(self):
        # Get the project url of all problems
        project_list = []

        # driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        rows_per_page = 50
        url_a = self.practice_url + "?"
        url_b = "limit="+str(rows_per_page)+"&sort_by=difficulty_rating&sort_order=asc&search=&start_rating=0&end_rating=5000&topic=&tags=&group=all"
        page_url = url_a + "page=0&" + url_b

        driver.get(page_url)
        time.sleep(1)
        
        page_path = '//*[@id="root"]/div/div[1]/div/div[3]/div/div[2]/div/div[4]/div/table/tfoot/tr/td/div/div[2]/div/p[2]'
        page_of_page = self.__wait_until_find(driver, page_path).text
        last_page = int(page_of_page.split('of')[1].strip())
        jump_page = int(last_page/rows_per_page)
        
        # jump_page = 2 # Delete when run
        
        for no in tqdm(range(jump_page), desc='Projects'): # last_page
            page_url = url_a + "page=" + str(no) + "&" + url_b
            driver.get(page_url)
            time.sleep(1)
            
            for i in range(50):
                codename_xpath = '//*[@id="MUIDataTableBodyRow-'+str(i)+'"]/td[1]/div[2]'
                try: codename = driver.find_element(By.XPATH, codename_xpath).text
                except: break
                project_list.append(codename)
        
        driver.quit()
        
        return project_list

    def get_tags(self, driver):
        tags = []

        # expand_xpath = '//*[@id="root"]/div/div[1]/div/div/div[1]/div[1]/div[1]/div[3]' # exist
        expand_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[4]' # feat
        self.__wait_and_click(driver, expand_xpath)

        # show_tags_xpath = '//*[@id="root"]/div/div[1]/div/div/div[1]/div[2]/div/div[3]/div[2]/div/span[1]/span[1]/span[1]/input'
        # show_tags_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[2]/div/div[2]/div/div' # error
        # self.__wait_and_click(driver, show_tags_xpath)

        # tags_xpath = '//*[@id="root"]/div/div[1]/div/div/div[1]/div[2]/div/div[2]/div/div[2]'
        tags_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[2]/div/div[2]/div/div[2]'
        
        try: 
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, tags_xpath)))
            tags_list = driver.find_element(By.XPATH, tags_xpath)
            
            children = tags_list.find_elements(By.XPATH, "./child::*")
            for elem in children:
                tags.append(elem.text)
                print("Tag: " + elem.text)
        except:
            print("Tags Fail")
        
        return tags       

    def get_title(self, driver):
        title = ''
        # title_xpath = '//*[@id="root"]/div/div[1]/div/div/div[1]/div[1]/div[1]/div[1]' # exist
        title_xpath = '//*[@id="root"]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/h1' # feat
        
        try: 
            time.sleep(0.02) # for prevent null
            title = self.__wait_until_find(driver, title_xpath).text
            print("Title: " + title)
        except: 
            print("Title Fail")
            pass

        return title.strip()

    def get_problem(self, driver):
        problem = ""
        problem_xpath = '//*[@id="problem-statement"]'
        
        try: 
            problem_statement = self.__wait_until_find(driver, problem_xpath).text
            children = problem_statement.find_elements(By.XPATH, "./child::*")

            for elem in children:
                tag = elem.tag_name
                text = elem.text
                if tag in ['h2', 'h3']:
                    if text != 'Problem':
                        if not problem:
                            continue
                        break
                else:
                    problem += text
            
        except: 
            print("Problem Fail")
            pass
        
        problem = problem.replace('\n', ' ')

        return problem

    def get_testcase(self, driver):
        # change to problems?
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
                    input_tc, output_tc = self.__wait_until_find(driver, in_xpath).text
                else:
                    input_tc = self.__wait_until_find(driver, in_xpath).text
                    output_tc = self.__wait_until_find(driver, out_xpath).text
                if input_tc.strip() and output_tc.strip():
                    break
            except:
                input_tc = ''
                output_tc = ''
        
        return input_tc, output_tc

    def get_project_info(self, project):
        # driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        page_url = self.problem_url + project
        driver.get(page_url)
        print(page_url)

        time.sleep(3)
        title = self.get_title(driver)
        tags = self.get_tags(driver)
        # tags = ''
        # problem = ''
        # input_tc=''
        # output_tc=''
        problem = self.get_problem(driver)
        input_tc, output_tc = self.get_testcase(driver)

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


    def get_submission_url_list(self, project):
        submission_url_list = []

        # driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        url_a = self.status_url + project + "?"
        url_b = "sort_by=All&sorting_order=asc&language="+self.language+"&status="+self.status+"&handle=&Submit=GO"

        # Get Last Page
        try:
            driver.get(self.status_url + project)
            # Select Language
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Language"]')))
            select_lan = Select(driver.find_element_by_xpath('//*[@id="Language"]'))
            select_lan.select_by_value(self.language)
            # Select Result
            select_res = Select(driver.find_element_by_xpath('//*[@id="Status"]'))
            select_res.select_by_value(self.status)
            # GO
            self.__wait_and_click(driver, '//*[@id="filter"]/table/tbody/tr/td[5]/input')
            # Get Last Page
            time.sleep(1)
            pages = driver.find_element_by_class_name('pageinfo').text
        except:
            pages = "1 of 1"

        last_page = pages.split('of')[1].strip()
        
        # Get Solution View Url
        for no in tqdm(range(int(last_page)), desc='URL'):
            page_url = url_a + "page=" + str(no) + "&" + url_b
            page = requests.get(page_url)
            soup = BeautifulSoup(page.text, "html.parser")
            for solution in soup.find_all("td", "word-break-unset"):
                solution_url = solution.find("a")["href"]
                if solution_url[0] == '/':
                    solution_url = solution_url[1:]
                submission_url_list.append(self.url+solution_url)
        
        driver.quit()

        return submission_url_list

    def get_submission_map(self, project):
        submission_map = {}

        # driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        submission_url_list = self.get_submission_url_list(project)

        for solution_url in tqdm(submission_url_list, desc='Submit'):
            try:
                # Get Username & Id & Status & Code
                driver.get(solution_url)
                time.sleep(1)

                username_path = '//*[@id="root"]/div/div[1]/div/div/div[2]/div[1]/div[3]/a'
                username = self.__wait_until_find(driver, username_path).text
                
                status_path = '//*[@id="root"]/div/div[1]/div/div/div[2]/div[1]/div[4]/span[2]'
                status = self.__wait_until_find(driver, status_path).text
                status = self.get_status(status)

                language_path = '//*[@id="root"]/div/div[1]/div/div/div[4]/div/div/div[1]/div'
                language = self.__wait_until_find(driver, language_path).text.split('Language:')[-1].strip()
                extension = self.get_extension(language)

                id = solution_url.split('/')[-1]

                plaintext_url = solution_url.replace("viewsolution", "viewplaintext")
                plaintext = requests.get(plaintext_url)
                soup = BeautifulSoup(plaintext.text, "html.parser")
                code = soup.find("pre").get_text()

                if status and id and username and code and extension:
                    submission_map[id] = [status, username, code, extension]
            except: pass

        driver.close()
        
        return submission_map

    def save_problem(self, project, problem, title, tags):
        # Save Problem
        dir_path = os.path.join(self.save_path, project)
        file_path = dir_path+"/problem.txt"
        describtion = 'Title: %s\nProblem:\n%s\nTags:%s' %(title, problem, tags) 
        self.save(dir_path, file_path, describtion)

    def save_testcase(self, project, input_tc, output_tc):
        # Save Testcase
        dir_path = os.path.join(self.save_path, project, 'testcases')
        file_path = dir_path+"/input_001.txt"
        self.save(dir_path, file_path, input_tc)
        file_path = dir_path+"/output_001.txt"
        self.save(dir_path, file_path, output_tc)
    
    def save_code(self, id, status, username, code, extension):
        # Save Code
        status = "".join([word.upper() for word in status if word.strip()])
        if status in ["AC"]:
            result = "correct"
        elif status in ["WA", "PAC"]:
            result = "wrong"
        else:
            result = "error"
        dir_path = os.path.join(self.save_path, project, result)
        file_path = dir_path+'/'+str(id)+'&'+status+'&'+str(username)+extension
        self.save(dir_path, file_path, code)
    
    def save_datatime(self, project):
        # Save DateTime
        times = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime())
        dir_path = os.path.join(self.save_path, project)
        file_path = dir_path+"/saved_date_time.txt"
        self.save(dir_path, file_path, times)
        
    def save(self, dir_path, file_path, data):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(file_path, 'w') as w:
            w.write(data.strip())

    def save_data(self, project, title, tags, problem, input_tc, output_tc, submission_map):
        self.save_problem(project, problem, title, tags)
        self.save_testcase(project, input_tc, output_tc)
        for id, (status, username, code, extension) in tqdm(submission_map.items(), desc='Save'):
            self.save_code(id, status, username, code, extension)
        self.save_datatime(project)


    def run_one(self, project, language="LANGUAGE", status="STATUS"):
        logger.info('\n'+project)
        print('\n'+project)
        self.set_language(language)
        self.set_status(status)
        title, tags, problem, input_tc, output_tc = self.get_project_info(project)
        submission_map = self.get_submission_map(project)
        return title, tags, problem, input_tc, output_tc, submission_map
        
    def run(self, language="LANGUAGE", status="STATUS"):
        project_list = self.get_project_list()

        for project in reversed(project_list):
            if os.path.isdir(self.save_path+project):
                continue
            title, tags, problem, input_tc, output_tc, submission_map = self.run_one(project, language, status)
            if submission_map:
                self.save_data(project, title, tags, problem, input_tc, output_tc, submission_map)


if __name__ == '__main__':
    compete = 'UAPRAC' # Default is 'None'
    project = 'ENODE_EASY'
    language = 'PYTH3' # Default is 'Language'
    status = 'ALL' # Default is 'ALL'

    save_path = 'codechefData/'
    
    # Run CodeChefCrawler with save_path
    ccc = CodeChefCrawler(save_path)

    # Update If URL is in Compete
    # ccc.update_url(compete)

    # Run All Project
    # ccc.run(language, status)

    proj_list = ['ENODE_EASY', 'ENODE_HARD', 'PANSTACK', 'XOREQUAL', 'SHUTTLE', 'MUSICHAIR', 'MCHAIRS', 'CHEFLCM']
    lang_list = ['PYPY3', 'PYTH3']
    for project in proj_list:
        for language in lang_list:
            # Run Only One Project  
            title, tags, problem, input_tc, output_tc, submission_map = ccc.run_one(project, language, status)
            ccc.save_data(project, title, tags, problem, input_tc, output_tc, submission_map)
        