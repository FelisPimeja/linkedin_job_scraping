import itertools
import re
import bs4
import requests
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
key_words = ['Database%20Engineer', 'Data%20Engineer', 'gis', 'geo', 'postgis', 'fme', 'qgis', 'arcgis', 'geospatial']
locations = ['Netherlands', 'Belgium', 'Norway', 'Sweden', 'Denmark', 'Ireland']

url_list = [f'{base_url}?keywords={word}&location={location}&start='
            for word, location in itertools.product(key_words, locations)]

title_stop_str1 = 'å|ä|ü|ö|ø|é|koordinator|projekt|assistenz|landmeter|tiker|techniker|german\b|analist|techniek|\Biker\b|Merchandiserentwickler|konsulent|udvikler|leider|\ben\b|\btill\b|\Bteur\b|daten|beheer|landschap|ontwerper|ontwikkelaar|ondersteuner|transporten|rojekten|technische|industrie|planarkitekt|werker|geoteknikker|systemansvarlig|samordnare|analytiker|werkvoor|tekenaar|besiktningstekniker|\bopus\b|bilprovning|\bund\b|\ben\b|transportplanner|planoloog|stedenbouwkundige|erfaren|adviseur|\boch\b|deutsche|geotekniker|breitband|werkstudent|\bog\b|bergen|dokumentation|\bdie\b|fachkraft|\binom\b|\bals\b|bereich|\bvan\b|vermessungstechniker|netzdokumentation|\bmit\b|\bstrom\b|stavanger|geomatiker|netzplaner|trondheim|fachbereich|\boder\b|stadterlebnisse|upplands|ecoloog|\bder\b|ingenieur|bij|softwareentwickler|zeichner|schwerpunkt|\bmet\b|bauzeichner|praktikum|fagarbeider|adviseur|entwicklung|\bals\b|technischer|konsult|spezialist|vermessungstechniker|informatiespecialist|informatie|stadterlebnisse|telekommunikation|landskapsarkitekt|ict'
title_stop_str2 = 'traineeship|internship|intern|junior|\bjr\b|trainee|docent|phd|postdoc|doktorand|praktikant|archeoloog|resource\splanner|merchandiser|staff|geotechnical|\bhr\b|Dokument|lawyer|backend|frontend|r&d|part\-time|software engineer|director|hydr[oa]|\bux\b|test|full[\s-]?stack|devops|developer|teacher|sales|\bqa\b|geophysicist|geologist|meteorologist|bosbouwer|hydroloog|c\+\+|c#|\.net|php|java|\bruby\b'
title_stop_str3 = '[a-zA-Z0-9]'


# for idx, url in enumerate(url_list): print(idx, url)
urls = url_list[11:15]  # 21

proxy = 'socks5://localhost:9051'
proxies = {"http": proxy, "https": proxy, "ftp": proxy}

logfile_name = 'logfile.log'


def print_log(*args, **kwargs):
    print(*args, **kwargs)
    with open(logfile_name,'a', encoding="utf-8") as file:
        print(*args, **kwargs, file=file)


for url in urls:

    fid = 0
    start = 0
    while start < 1000:

        target_url = url + str(start)
        print_log( f'      Parsing page: {target_url}')

        job_list = []
        df = pd.DataFrame(columns=[
            'id', 'date', 'title', 'company', 'company_link', 'location', 'link',
            'description', 'seniority', 'employment_type', 'job_function', 'industries'])

        ref_job_list = list(pd.read_sql_query('select * from linkedin.open_positions', con=connection)['id'])

        while True:
            page = requests.get(url=target_url, proxies=proxies)
            if str(page.status_code) == '200':
                break
            else:
                print_log('      Redirected to Auth page. Retrying...')
        soup = bs4.BeautifulSoup(page.text, 'html.parser')
        if soup.find('li') is None:
            print_log(page.status_code)
            print_log(soup)
            print_log('      Empty page. Skipping...')
            break

        start = start + 25
        lis = soup.find_all('li')

        for li in lis:
            fid = fid + 1
            job_id = li.select_one('.base-search-card--link')['data-entity-urn'].split(sep=':')[-1]
            if int(job_id) in ref_job_list:
                print_log(f'{fid: 5d} job_id: {job_id} already in db. Skipping...')
                continue

            date = li.select_one('time')['datetime']
            job_title_str = li.select_one('h3.base-search-card__title').get_text().strip()
            job_title = None
            if (
                    not re.search(title_stop_str1, job_title_str, re.I) and
                    not re.search(title_stop_str2, job_title_str, re.I) and
                    re.search(title_stop_str3, job_title_str, re.I)
            ):
                job_title = job_title_str
            else:
                print_log(f'{fid: 5d} job_id: {job_id} {job_title_str} filtered because of stop words. Skipping...')
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

            while True:
                job_details_raw = requests.get(url=job_link, proxies=proxies)
                job_details = bs4.BeautifulSoup(job_details_raw.text, 'html.parser')
                if str(job_details_raw.status_code) == '200' and job_details.select_one(
                        'meta[name = "pageKey"]')['content'] == 'd_jobs_guest_details':
                    break
                else:
                    print_log('      Redirected to Auth page. Retrying...')

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
            print_log(f'{fid: 5d}', info_string)
            job_list.append(info_string)
            df = pd.concat([pd.DataFrame(
                [[job_id, date, job_title, company_name, company_link, location, job_link,
                  description, seniority, employment_type, job_function, industries]], columns=df.columns
            ), df], ignore_index=True)

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

