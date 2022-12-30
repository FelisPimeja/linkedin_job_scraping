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

#  Generate target urls:
base_url = 'https://www.linkedin.com/jobs/search/'
key_words = ['gis', 'geo', 'postgis', 'fme', 'qgis', 'arcgis', 'geospatial']
localions = ['Netherlands', 'Belgium', 'Norway', 'Sweden', 'Denmark', 'Germany', 'Ireland']

url_list = [f'{base_url}?keywords={word}&location={location}'
            for word, location in itertools.product(key_words, localions)]

url = url_list[14]

proxy = 'localhost:9051'
service = Service(env_vars['chromedriver_path'])
options = webdriver.ChromeOptions()

# Load Chrome silently without popping up window
# options.add_argument('--headless')

# Override system locale so that LinkedIn using English
options.add_argument("--lang=en-GB")

# Fix window size large enough that LinkedIn will load job info on the same page instead of loading new one:
options.add_argument("window-size=1400,600")

# Use proxy to load pages (in my case LinkedIn is blocked in Russia so I use Tor as local proxi):
options.add_argument('--proxy-server=socks5://' + proxy)

# Prevent from console spam:
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Make Chrome window stay after Python script finished working
options.add_experimental_option("detach", True)

# Disable loading images to speed up things a bit:
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)


wd = webdriver.Chrome(options=options, service=service)
# Load page
wd.get(url)

# Test that we are not redirected to auth page
meta_path = ' / html / head / meta [contains(@name, "pageKey")]'
meta_content = wd.find_element(By.XPATH, meta_path).get_attribute('content')
if meta_content == 'auth_wall_desktop_jserp':
    wd.get(url)


ignored_exceptions = (NoSuchElementException, StaleElementReferenceException, TimeoutException)
elem = WebDriverWait(wd, timeout=10, ignored_exceptions=ignored_exceptions)

# Close cookies and 'sign in' messages for easier debugging
try:
    accept_cookies_button = elem.until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'button.artdeco-global-alert-action'))).click()
except:
    pass

try:
    close_signin_button = elem.until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'button.cta-modal__dismiss-btn'))).click()
except:
    pass

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

jobs = job_lists.find_elements(By.CSS_SELECTOR, 'li')  # return a list

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
    job_id.append(job_id0)

    job_title0 = None
    try:
        job_title0 = job.find_element(By.CSS_SELECTOR, '.base-search-card__info>h3').text
    except NoSuchElementException:
        pass
    job_title.append(job_title0)

    company_name0 = None
    try:
        company_name0 = job.find_element(By.CSS_SELECTOR, '.base-search-card__info>h4').text
    except NoSuchElementException:
        pass
    company_name.append(company_name0)

    location0 = None
    try:
        location0 = job.find_element(By.CSS_SELECTOR, '.job-search-card__location').text
    except NoSuchElementException:
        pass
    location.append(location0)

    date0 = None
    try:
        date0 = job.find_element(By.CSS_SELECTOR, '[class*="job-search-card__listdate"]').get_attribute('datetime')
    except NoSuchElementException:
        pass
    date.append(date0)

    job_link0 = None
    try:
        job_link0 = job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split(sep='?')[0]
    except NoSuchElementException:
        pass
    job_link.append(job_link0)

    print(f'{str(job_id0)}, {job_title0}, {company_name0}, {location0}, {date0}, {job_link0}')


print('Gathering more details...')

jd =[]
seniority =[]
emp_type =[]
job_func =[]
industries =[]
for item in range(len(jobs)):
    job_func0 = []
    industries0 = []

    job_click_path = f' // ul[contains(@class, "jobs-search__results-list")] / li[{item + 1}] // *'
    try:
        job.find_element(By.XPATH, job_click_path).click()
        time.sleep(1)
    except:
        print('Something went wrong (can not click job title to get job details)')

    # clicking job to view job details
    # job_click_path = f' // ul[contains(@class, "jobs-search__results-list")] / li[{item + 1}] // *'
    # get_job_details = elem.until(
    #     expected_conditions.element_to_be_clickable((By.XPATH, job_click_path))).click()

    # jd_path = ' //div[contains(@class, "description__text--rich")]'
    # jd0 = None
    # try:
    #     jd0 = job.find_element(By.XPATH, jd_path).get_attribute('innerText')
    # except NoSuchElementException:
    #     pass
    # jd.append(jd0)

    # test_path = ' //h2[contains(@class, "top-card-layout__title")]'
    # test = job.find_element(By.XPATH, test_path)
    # print(test.text)
    # print(job_title[item])

    a_path = ' //h2[contains(@class, "top-card-layout__title")]'
    a_check = elem.until(expected_conditions.text_to_be_present_in_element((By.XPATH, a_path), job_title[item]))

    jd_path = ' //div[contains(@class, "description__text--rich")]'
    jd0 = elem.until(expected_conditions.presence_of_element_located((By.XPATH, jd_path))).get_attribute('innerText')
    jd.append(jd0)

    seniority_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[1] // span'
    seniority0 = None
    try:
        seniority0 = job.find_element(By.XPATH, seniority_path).get_attribute('innerText').strip()
    except NoSuchElementException:
        pass

    seniority.append(seniority0)

    emp_type_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[2] // span'
    emp_type0 = None
    try:
        emp_type0 = job.find_element(By.XPATH, emp_type_path).get_attribute('innerText').strip()
    except NoSuchElementException:
        pass

    emp_type.append(emp_type0)

    job_func_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[3] // span'
    job_func_elements_final = None
    try:
        job_func_elements = job.find_element(By.XPATH, job_func_path).get_attribute('innerText')
        job_func_elements_list = job_func_elements.replace('and ', ',').replace(', ,', ',').split(sep=',')
        job_func_elements_final = [s.strip() for s in job_func_elements_list]
    except NoSuchElementException:
        pass

    job_func.append(job_func_elements_final)

    industries_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[4] // span'
    industries_elements_final = None
    try:
        industries_elements = job.find_element(By.XPATH, industries_path).get_attribute('innerText')
        industries_elements_list = industries_elements.replace('and ', ',').replace(', ,', ',').split(sep=',')
        industries_elements_final = [s.strip() for s in industries_elements_list]
    except NoSuchElementException:
        pass

    industries.append(industries_elements_final)

    # Check current page address:
    # get_url = wd.current_url
    # print("The current url is:" + str(get_url))

    print(f'{item + 1} {jd0[:30]}..., {seniority0}, {emp_type0}, {job_func_elements_final}, {industries_elements_final}')

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
