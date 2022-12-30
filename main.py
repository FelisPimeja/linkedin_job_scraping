from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
# import click
import time

from sqlalchemy import create_engine
from sqlalchemy import types

# import environmental variables:
env_vars = {}
with open('./.env') as f:
    for line in f:
        if line.startswith('#') or not line.strip():
            continue
        key, value = line.strip().split('=', 1)
        env_vars[key] = value # Save to a dict, initialized env_vars = {}

# url = "https://www.google.com"

# GIS in Netherlands:
# url = 'https://www.linkedin.com/jobs/search/?keywords=gis%20OR%20geo&location=Netherlands'
# Postgis in Netherlands:
# url = 'https://www.linkedin.com/jobs/search?keywords=postgis&location=Netherlands'
# Postgis in Belgium:
# url = 'https://www.linkedin.com/jobs/search?keywords=postgis&location=Belgium'
# fme in Netherlands:
url = 'https://www.linkedin.com/jobs/search?keywords=fme&location=Netherlands'

proxy = 'localhost:9051'
service = Service(env_vars['chromedriver_path'])
options = webdriver.ChromeOptions()
# Без запуска окна браузера:
# options.add_argument('--headless')
# Чтобы LinkedIn не переводил отдельные элементы на русский:
options.add_argument("--lang=en-GB")
# Фиксируем разрешение окна, чтобы LinkedIn подгружал данные в том же окне, а не открывал новое:
options.add_argument("window-size=1400,600")
# Запуск через проки Тора:
options.add_argument('--proxy-server=socks5://' + proxy)
# Чтобы не мусорить в консоль:
options.add_experimental_option('excludeSwitches', ['enable-logging'])

options.add_experimental_option("detach", True)


wd = webdriver.Chrome(options=options, service=service)
wd.get(url)
ignored_exceptions = (NoSuchElementException, StaleElementReferenceException, TimeoutException)
elem = WebDriverWait(wd, timeout=5, ignored_exceptions=ignored_exceptions)

# Close cookies and 'sign in' messages for easier debugging
accept_cookies_button = elem.until(
    expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'button.artdeco-global-alert-action'))).click()

close_signin_button = elem.until(
    expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'button.cta-modal__dismiss-btn'))).click()

# Get number of Job positions to parse
no_of_jobs_str = elem.until(
    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'h1>span')))
no_of_jobs = int(no_of_jobs_str.text.replace(' ', '').replace('+', '').replace(',', ''))
print(str(no_of_jobs) + ' jobs found. Preprocessing titles list...')

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
print(str(len(jobs)) + ' Processing base info...')


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


print('Gathering details')

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

    try:
        job.find_element(By.XPATH, job_click_path).click()
        # print(job_click.text)
        time.sleep(2)
    except:
        print('Something went wrong (can not click job title to get job details)')

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
        # print(job_func_elements_final)
    except NoSuchElementException:
        pass

    job_func.append(job_func_elements_final)

    industries_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[4] // span'
    industries_elements_final = None
    try:
        industries_elements = job.find_element(By.XPATH, industries_path).get_attribute('innerText')
        industries_elements_list = industries_elements.replace('and ', ',').replace(', ,', ',').split(sep=',')
        industries_elements_final = [s.strip() for s in industries_elements_list]
        # print(industries_elements_final)
    except NoSuchElementException:
        pass

    industries.append(industries_elements_final)

    # Проверяем текущую страницу:
    # get_url = wd.current_url
    # print("The current url is:" + str(get_url))

    print(item + 1)

# print(len(job_id), len(date), len(company_name), len(job_title), len(location), len(jd), len(seniority), len(emp_type), len(job_func), len(industries), len(job_link) )


job_data = pd.DataFrame({
    'id': job_id,
    'date': date,
    'company': company_name,
    'title': job_title,
    'location': location,
    'description': jd,
    'level': seniority,
    'type': emp_type,
    'function': job_func,
    'industry': industries,
    'link': job_link
})

# cleaning description column
# job_data['Description'] = job_data['Description'].str.replace('\n', ' ')
# job_data.to_excel('gis_jobs.xlsx', index=False)

# Write data into Postgres
connection = create_engine(f'postgresql://{env_vars["user"]}:{env_vars["password"]}@{env_vars["host"]}:'
                           f'{env_vars["port"]}/{env_vars["dbname"]}')

job_data.to_sql('open_positions', con=connection, schema='linkedin', if_exists='append',
              dtype={
                  "id": types.BigInteger(),
                  "date": types.Date(),
                  "company": types.Text(),
                  "title": types.Text(),
                  "location": types.Text(),
                  "description": types.Text(),
                  "level": types.Text(),
                  "type": types.Text(),
                  "function": types.ARRAY(types.Text),
                  "industry": types.ARRAY(types.Text),
                  "link": types.Text()
              })


# print(emp_type)
# print(seniority)
# print(job_func)
