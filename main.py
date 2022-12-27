from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

# url = "https://www.google.com"
url = 'https://www.linkedin.com/jobs/search?keywords=postgis&location=Netherlands&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'


proxy = 'localhost:9051'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--proxy-server=socks5://' + proxy)

wd = webdriver.Chrome(options=options)
wd.get(url)

# test_value = driver.find_element(By.CSS_SELECTOR, 'input.gNO89b').get_attribute('value') #Тест для гугла
no_of_jobs = int(wd.find_element(By.CSS_SELECTOR, 'h1>span').text)
print(no_of_jobs)


# -----------------------------------------------------------------------

i = 2
while i <= int(no_of_jobs/25)+1:
    wd.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    i = i + 1
    try:
        wd.find_element_by_xpath('/html/body/main/div/section/button').click()
        time.sleep(5)
    except:
        pass
        time.sleep(5)



job_lists = wd.find_element(By.CSS_SELECTOR, '.jobs-search__results-list')

jobs = job_lists.find_elements(By.CSS_SELECTOR, 'li') # return a list

# print(jobs)
# print(len(jobs))

len(jobs)



job_id = []
job_title = []
company_name = []
location = []
date = []
job_link = []
for job in jobs:
    job_id0 = job.find_element(By.CSS_SELECTOR, 'div').get_attribute('data-entity-urn')
    # print(job_id0)
    job_id.append(job_id0)

    job_title0 = job.find_element(By.CSS_SELECTOR, 'div>a>span.sr-only').text
    print(job_title0)
    #
    # job_title.append(job_title0)

    # company_name0 = job.find_element(By.CSS_SELECTOR, 'h4').get_attribute('innerText')
    # company_name.append(company_name0)
    #
    # location0 = job.find_element(By.CSS_SELECTOR, '.job-result-card__location').get_attribute('innerText')
    # location.append(location0)
    #
    # date0 = job.find_element(By.CSS_SELECTOR, 'div > div > time').get_attribute('innerText')
    # date.append(date0)
    #
    # job_link0 = job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
    # job_link.append(job_link0)
    #
    #
    #
    #
    #
    #
    #
    # jd =[]
    # seniority =[]
    # emp_type =[]
    # job_func =[]
    # industries =[]
    # for item in range(len(jobs)):
    #     job_func0 = []
    #
    #
    # industries0 = []
    # # clicking job to view job details
    # job_click_path = f' / html / body / main / div / section[2] / ul / li[{item + 1}] / img'
    # job_click = job.find_element_by_xpath(job_click_path).click()
    # time.sleep(5)
    #
    # jd_path = ' / html / body / main / section / div[2] / section[2] / div'
    # jd0 = job.find_element_by_xpath(jd_path).get_attribute('innerText')
    # jd.append(jd0)
    #
    # seniority_path = ' / html / body / main / section / div[2] / section[2] / ul / li[1] / span'
    # seniority0 = job.find_element_by_xpath(seniority_path).get_attribute('innerText')
    # seniority.append(seniority0)
    #
    # emp_type_path = ' / html / body / main / section / div[2] / section[2] / ul / li[2] / span'
    # emp_type0 = job.find_element_by_xpath(emp_type_path).get_attribute('innerText')
    # emp_type.append(emp_type0)
    #
    # job_func_path = ' / html / body / main / section / div[2] / section[2] / ul / li[3] / span'
    # job_func_elements = job.find_elements_by_xpath(job_func_path)
    # for element in job_func_elements:
    #     job_func0.append(element.get_attribute('innerText'))
    # job_func_final = ', '.join(job_func0)
    # job_func.append(job_func_final)
    # industries_path = ' / html / body / main / section / div[2] / section[2] / ul / li[4] / span'
    # industries_elements = job.find_elements_by_xpath(industries_path)
    # for element in industries_elements:
    #     industries0.append(element.get_attribute('innerText'))
    # industries_final = ', '.join(industries0)
    # industries.append(industries_final)