from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time


# url = "https://www.google.com"

# GIS in Netherlands:
# url = 'https://www.linkedin.com/jobs/search/?currentJobId=3354264177&geoId=102890719&keywords=gis%20OR%20geo&location=Netherlands&refresh=true'
# Postgis in Netherlands:
url = 'https://www.linkedin.com/jobs/search?keywords=postgis&location=Netherlands'
# fme in Netherlands:
# url = 'https://www.linkedin.com/jobs/search?keywords=fme&location=Netherlands'

proxy = 'localhost:9051'
options = webdriver.ChromeOptions()
# Без запуска окна браузера:
options.add_argument('--headless')
# Чтобы LinkedIn не переводил отдельные элементы на русский:
options.add_argument("--lang=en-GB")
# Фиксируем разрешение окна, чтобы LinkedIn подгружал данные в том же окне, а не открывал новое:
options.add_argument("window-size=1400,600")
# Запуск через проки Тора:
options.add_argument('--proxy-server=socks5://' + proxy)
# Чтобы не мусорить в консоль:
options.add_experimental_option('excludeSwitches', ['enable-logging'])

options.add_experimental_option("detach", True)


wd = webdriver.Chrome(options=options)
wd.get(url)

no_of_jobs = None
try:
    # no_of_jobs = driver.find_element(By.CSS_SELECTOR, 'input.gNO89b').get_attribute('value') #Тест для гугла
    no_of_jobs = int(wd.find_element(By.CSS_SELECTOR, 'h1>span').text.replace(' ', ''))
    print('no_of_jobs = ' + str(no_of_jobs))
except NoSuchElementException:
    print('Something went wrong (check connection!)')



# -----------------------------------------------------------------------

i = 2
while i <= int(no_of_jobs/25) + 1:
    wd.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    i = i + 1
    try:
        wd.find_element(By.XPATH, '/html/body/main/div/section/button').click()
        time.sleep(5)
    except:
        pass
        time.sleep(5)



job_lists = wd.find_element(By.CSS_SELECTOR, '.jobs-search__results-list')

jobs = job_lists.find_elements(By.CSS_SELECTOR, 'li') # return a list

# print('jobs' + jobs[0].text)
print('len(jobs) = ' + str(len(jobs)))

len(jobs)



job_id = []
job_title = []
company_name = []
location = []
date = []
job_link = []
for job in jobs:
    job_id0 = None
    try:
        job_id0 = str(job.find_element(By.CSS_SELECTOR, '.base-card').get_attribute('data-entity-urn')).split(sep=':')[-1]
    except NoSuchElementException:
        pass
    # print(job_id0)
    job_id.append(job_id0)


    job_title0 = None
    try:
        job_title0 = job.find_element(By.CSS_SELECTOR, '.base-search-card__info>h3').text
    except NoSuchElementException:
        pass
    # print(job_title0)
    job_title.append(job_title0)

    company_name0 = None
    try:
        company_name0 = job.find_element(By.CSS_SELECTOR, '.base-search-card__info>h4').text
    except NoSuchElementException:
        pass
    # print(company_name0)
    company_name.append(company_name0)


    location0 = None
    try:
        location0 = job.find_element(By.CSS_SELECTOR, '.job-search-card__location').text
    except NoSuchElementException:
        pass
    # print(location0)
    location.append(location0)

    date0 = None
    try:
        date0 = job.find_element(By.CSS_SELECTOR, '[class*="job-search-card__listdate"]').get_attribute('datetime')
    except NoSuchElementException:
        pass
    # print(date0)
    date.append(date0)


    job_link0 = None
    try:
        job_link0 = job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(sep='?')[0]
    except NoSuchElementException:
        pass
    # print(job_link0)
    job_link.append(job_link0)




jd =[]
seniority =[]
emp_type =[]
job_func =[]
industries =[]
for item in range(len(jobs)):
    job_func0 = []


    industries0 = []
    # clicking job to view job details
    job_click_path = f' // ul[contains(@class, "jobs-search__results-list")] / li[{item + 1}] // *'


    job_click = job.find_element(By.XPATH, job_click_path).click()
    # print(job_click.text)
    time.sleep(2)

    jd_path = ' //div[contains(@class, "description__text--rich")]'
    jd0 = None
    try:
        jd0 = job.find_element(By.XPATH, jd_path).get_attribute('innerText')
        # print(jd0)
    except NoSuchElementException:
        pass
    jd.append(jd0)

    seniority_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[1] // span'
    seniority0 = None
    try:
        seniority0 = job.find_element(By.XPATH, seniority_path).get_attribute('innerText').strip()
        # print(seniority0)
    except NoSuchElementException:
        pass

    seniority.append(seniority0)


    emp_type_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[2] // span'
    emp_type0 = None
    try:
        emp_type0 = job.find_element(By.XPATH, emp_type_path).get_attribute('innerText').strip()
        # print(emp_type0)
    except NoSuchElementException:
        pass

    emp_type.append(emp_type0)


    job_func_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[3] // span'
    job_func_elements_final = None
    try:
        job_func_elements = job.find_element(By.XPATH, job_func_path).get_attribute('innerText')
        job_func_elements_list = job_func_elements.replace('and ', ',').replace(', ,', ',').split(sep=',')
        job_func_elements_final = [s.strip() for s in job_func_elements_list]
        print(job_func_elements_final)
    except NoSuchElementException:
        pass

    job_func.append(job_func_elements_final)


    # industries_path = ' / html / body / main / section / div[2] / section[2] / ul / li[4] / span'
    # industries_elements = job.find_elements_by_xpath(industries_path)
    # for element in industries_elements:
    #     industries0.append(element.get_attribute('innerText'))
    # industries_final = ', '.join(industries0)
    # industries.append(industries_final)

    # Проверяем текущую страницу:
    # get_url = wd.current_url
    # print("The current url is:" + str(get_url))

print(emp_type)
print(seniority)
print(job_func)
