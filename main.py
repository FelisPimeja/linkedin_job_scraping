import itertools
import bs4, requests
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
        env_vars[key] = value  # Save to a dict, initialized env_vars = {}

# PG connection:
connection = create_engine(f'postgresql://{env_vars["user"]}:{env_vars["password"]}@{env_vars["host"]}:'
                           f'{env_vars["port"]}/{env_vars["dbname"]}')

#  Generate target urls:
base_url = 'https://www.linkedin.com/jobs/api/seeMoreJobPostings/search'
key_words = ['gis', 'geo', 'postgis', 'fme', 'qgis', 'arcgis', 'geospatial']
locations = ['Netherlands', 'Belgium', 'Norway', 'Sweden', 'Denmark', 'Germany', 'Ireland']

url_list = [f'{base_url}?keywords={word}&location={location}&start='
            for word, location in itertools.product(key_words, locations)]

title_stop_words = ['Traineeship', 'Internship', 'Intern', 'Junior']

# https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=geo&location=Netherlands&start=600

# for idx, url in enumerate(url_list): print(idx, url)
urls = url_list[35:41]  # 21

proxy = 'socks5://localhost:9051'
proxies = {"http": proxy, "https": proxy, "ftp": proxy}


for url in urls:

    start = 0
    while start > -1:

        target_url = url + str(start)
        print( f' Parsing page: {target_url}')

        job_list = []
        df = pd.DataFrame(columns=[
            'id', 'date', 'title', 'company', 'company_link', 'location', 'link',
            'description', 'seniority', 'employment_type', 'job_function', 'industries'])

        ref_job_list = list(pd.read_sql_query('select * from linkedin.open_positions', con=connection)['id'])
        # print(ref_job_list)

        page = requests.get(url=target_url, proxies=proxies)
        soup = bs4.BeautifulSoup(page.text, 'html.parser')
        if soup.find('li') is None:
            print('No elements found. Skipping to next url...')
            break

        start = start + 25
        lis = soup.find_all('li')

        for idx, li in enumerate(lis):
            job_id = li.select_one('.base-search-card--link')['data-entity-urn'].split(sep=':')[-1]
            if int(job_id) in ref_job_list:
                print(f' {idx + 1} job_id: {job_id} found in db already. Skipping...')
                continue

            date = li.select_one('time')['datetime']
            job_title = li.select_one('h3.base-search-card__title').get_text().strip()
            if any(word in str(job_title) for word in title_stop_words):
                print(f' {idx + 1} job_id: {job_id} {job_title} filtered because of stop words. Skipping...')
                continue

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

            while True:
                job_details_raw = requests.get(url=job_link, proxies=proxies)
                job_details = bs4.BeautifulSoup(job_details_raw.text, 'html.parser')
                if str(job_details_raw.status_code) == '200' and job_details.select_one(
                        'meta[name = "pageKey"]')['content'] == 'd_jobs_guest_details':
                    break
                else:
                    print(' Redirected to Auth page. Retrying...')

            content = job_details.select_one('div.decorated-job-posting__details')
            description = content.select_one('div.description__text--rich').get_text('\n', strip=True)
            more_details = content.select('li.description__job-criteria-item')
            seniority = None
            employment_type = None
            job_function = None
            industries = None
            for detail in more_details:
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

            info_string = (job_id, date, job_title, company_name, location, job_link, company_link,
                           description, seniority, employment_type, job_function, industries)
            print(f'{idx + 1: 3d}', info_string)
            job_list.append(info_string)
            df = pd.concat([pd.DataFrame(
                [[job_id, date, job_title, company_name, company_link, location, job_link,
                  description, seniority, employment_type, job_function, industries]], columns=df.columns
            ), df], ignore_index=True)

        # print(df.to_string())

        # Write data into Postgres
        df = df.set_index('id')
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

