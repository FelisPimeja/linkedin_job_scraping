from selenium import webdriver
from selenium.webdriver.common.by import By


# url = "https://www.google.com"
url = 'https://www.linkedin.com/jobs/search?keywords=postgis&location=Netherlands&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'


proxy = 'localhost:9051'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--proxy-server=socks5://' + proxy)

driver = webdriver.Chrome(options=options)
driver.get(url)

# test_value = driver.find_element(By.CSS_SELECTOR, 'input.gNO89b').get_attribute('value') #Тест для гугла
test_value = driver.find_element(By.CSS_SELECTOR, 'h1.results-context-header__context').text
print(test_value)
