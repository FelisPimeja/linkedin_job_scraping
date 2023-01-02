# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.common.exceptions import TimeoutException
# from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import StaleElementReferenceException
# from selenium.webdriver.support import expected_conditions
# from selenium.webdriver.support.wait import WebDriverWait
# # import click
# import time

import itertools
import bs4, re, requests
import pandas as pd

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
base_url = 'https://www.linkedin.com/jobs/api/seeMoreJobPostings/search'
key_words = ['gis', 'geo', 'postgis', 'fme', 'qgis', 'arcgis', 'geospatial']
localions = ['Netherlands', 'Belgium', 'Norway', 'Sweden', 'Denmark', 'Germany', 'Ireland']

url_list = [f'{base_url}?keywords={word}&location={location}&start='
            for word, location in itertools.product(key_words, localions)]

# https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=geo&location=Netherlands&start=600

# for idx, url in enumerate(url_list): print(idx, url)
url = url_list[14] #21

proxy = 'socks5://localhost:9051'
proxies = {"http": proxy, "https": proxy, "ftp": proxy }

job_list = []
df = pd.DataFrame(columns=[
    'id', 'date', 'title', 'company', 'company_link', 'location', 'link',
    'description', 'seniority', 'employment_type', 'job_function', 'industries'])
start = 0

while start > -1:
    # print(url + str(start))
    page = requests.get(url=url + str(start), proxies=proxies)
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    if soup.find('li') is None:
        break

    start = start+25
    lis = soup.find_all('li')

    for idx, li in enumerate(lis):
        job_id = li.select_one('.base-search-card--link')['data-entity-urn'].split(sep=':')[-1]
        date = li.select_one('time')['datetime']
        job_title = li.select_one('h3.base-search-card__title').get_text().strip()
        company_name = li.select_one('h4').get_text().strip()
        if li.select_one('a.hidden-nested-link'):
            company_link = li.select_one('a.hidden-nested-link')['href'].split(sep='?')[0]
        else:
            company_link = None
        company_link = company_link
        location = li.select_one('.job-search-card__location').get_text().strip()
        if li.select_one('a.base-card__full-link'):
            job_link = li.select_one('a.base-card__full-link')['href']
        else:
            job_link = li.select_one('a.base-search-card--link')['href']
        job_link = job_link.split(sep='?')[0].replace('nl.linkedin.com', 'linkedin.com')
        # print(f'{idx+1: 3d}', job_id, date, job_title[0:30], company_name[0:10], location, job_link, company_link)

        job_details = requests.get(url=job_link, proxies=proxies)
        content = bs4.BeautifulSoup(job_details.text, 'html.parser').select_one('div.decorated-job-posting__details')
        description = content.select_one('div.description__text--rich').get_text('\n', strip=True)
        further_details = content.select('li.description__job-criteria-item')
        seniority = None
        employment_type = None
        job_function = None
        industries = None
        for detail in further_details:
            detail_type = detail.select_one('h3').get_text().strip()
            detail_detail = detail.select_one('span').get_text().strip()
            if detail_type == 'Seniority level':
                seniority = detail_detail
            elif detail_type == 'Employment type':
                employment_type = detail_detail
            elif detail_type == 'Job function':
                job_function = detail_detail.replace('and', '').replace(', ,', ',').split(sep=', ')
            elif detail_type == 'Industries':
                industries = detail_detail.replace('and', '').replace(', ,', ',').split(sep=', ')
        # print(seniority, employment_type, job_function, industries)

        info_string = (job_id, date, job_title, company_name, location, job_link, company_link,
                       description, seniority, employment_type, job_function, industries)
        print(f'{idx+1: 3d}', info_string)
        job_list.append(info_string)
        df = pd.concat([pd.DataFrame(
            [[job_id, date, job_title, company_name, company_link, location, job_link,
              description, seniority, employment_type, job_function, industries]], columns=df.columns
        ), df], ignore_index=True)

# print(job_list)
print(df.to_string())

# Write data into Postgres
connection = create_engine(f'postgresql://{env_vars["user"]}:{env_vars["password"]}@{env_vars["host"]}:'
                           f'{env_vars["port"]}/{env_vars["dbname"]}')

df.to_sql('open_positions', con=connection, schema='linkedin', if_exists='append',
              dtype={
                  "id": types.BigInteger(),
                  "date": types.Date(),
                  "title": types.Text(),
                  "company_name": types.Text(),
                  "company_link": types.Text(),
                  "location": types.Text(),
                  "job_link": types.Text(),
                  "description": types.Text(),
                  "seniority": types.Text(),
                  "employment_type": types.Text(),
                  "job_function": types.Text(),
                  "industries": types.Text()
              })





#
# jd =[]
# seniority =[]
# emp_type =[]
# job_func =[]
# industries =[]
# for item in range(len(jobs)):
#     job_func0 = []
#     industries0 = []
#
#     job_click_path = f' // ul[contains(@class, "jobs-search__results-list")] / li[{item + 1}] // *'
#     try:
#         job.find_element(By.XPATH, job_click_path).click()
#         time.sleep(1)
#     except:
#         print('Something went wrong (can not click job title to get job details)')
#
#     # clicking job to view job details
#     # job_click_path = f' // ul[contains(@class, "jobs-search__results-list")] / li[{item + 1}] // *'
#     # get_job_details = elem.until(
#     #     expected_conditions.element_to_be_clickable((By.XPATH, job_click_path))).click()
#
#     # jd_path = ' //div[contains(@class, "description__text--rich")]'
#     # jd0 = None
#     # try:
#     #     jd0 = job.find_element(By.XPATH, jd_path).get_attribute('innerText')
#     # except NoSuchElementException:
#     #     pass
#     # jd.append(jd0)
#
#     # test_path = ' //h2[contains(@class, "top-card-layout__title")]'
#     # test = job.find_element(By.XPATH, test_path)
#     # print(test.text)
#     # print(job_title[item])
#
#     a_path = ' //h2[contains(@class, "top-card-layout__title")]'
#     a_check = elem.until(expected_conditions.text_to_be_present_in_element((By.XPATH, a_path), job_title[item]))
#
#     jd_path = ' //div[contains(@class, "description__text--rich")]'
#     jd0 = elem.until(expected_conditions.presence_of_element_located((By.XPATH, jd_path))).get_attribute('innerText')
#     jd.append(jd0)
#
#     seniority_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[1] // span'
#     seniority0 = None
#     try:
#         seniority0 = job.find_element(By.XPATH, seniority_path).get_attribute('innerText').strip()
#     except NoSuchElementException:
#         pass
#
#     seniority.append(seniority0)
#
#     emp_type_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[2] // span'
#     emp_type0 = None
#     try:
#         emp_type0 = job.find_element(By.XPATH, emp_type_path).get_attribute('innerText').strip()
#     except NoSuchElementException:
#         pass
#
#     emp_type.append(emp_type0)
#
#     job_func_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[3] // span'
#     job_func_elements_final = None
#     try:
#         job_func_elements = job.find_element(By.XPATH, job_func_path).get_attribute('innerText')
#         job_func_elements_list = job_func_elements.replace('and ', ',').replace(', ,', ',').split(sep=',')
#         job_func_elements_final = [s.strip() for s in job_func_elements_list]
#     except NoSuchElementException:
#         pass
#
#     job_func.append(job_func_elements_final)
#
#     industries_path = ' // ul[contains(@class, "description__job-criteria-list")] / li[4] // span'
#     industries_elements_final = None
#     try:
#         industries_elements = job.find_element(By.XPATH, industries_path).get_attribute('innerText')
#         industries_elements_list = industries_elements.replace('and ', ',').replace(', ,', ',').split(sep=',')
#         industries_elements_final = [s.strip() for s in industries_elements_list]
#     except NoSuchElementException:
#         pass
#
#     industries.append(industries_elements_final)
#
#     # Check current page address:
#     # get_url = wd.current_url
#     # print("The current url is:" + str(get_url))
#
#     print(f'{item + 1} {jd0[:30]}..., {seniority0}, {emp_type0}, {job_func_elements_final}, {industries_elements_final}')
#
# # print(len(job_id), len(date), len(company_name), len(job_title), len(location), len(jd), len(seniority), len(emp_type), len(job_func), len(industries), len(job_link) )
#
#
# job_data = pd.DataFrame({
#     'id': job_id,
#     'date': date,
#     'company': company_name,
#     'title': job_title,
#     'location': location,
#     'description': jd,
#     'level': seniority,
#     'type': emp_type,
#     'function': job_func,
#     'industry': industries,
#     'link': job_link
# })
#
# # cleaning description column
# # job_data['Description'] = job_data['Description'].str.replace('\n', ' ')
# # job_data.to_excel('gis_jobs.xlsx', index=False)



#
# # print(emp_type)
# # print(seniority)
# # print(job_func)
