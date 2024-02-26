import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import time

with open('credentials_and_urls.json') as json_file:
    data = json.load(json_file)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

driver = webdriver.Chrome(options=chrome_options)


# time.sleep used to solve the captcha
def wait_for_correct_current_url(desired_url):
    while driver.current_url != desired_url:
        time.sleep(0.01)


url = 'https://www.linkedin.com/login'
driver.get(url)
time.sleep(2)
username = data["login_credentials"]["username"]
password = data["login_credentials"]["password"]

uname = driver.find_element(By.ID, "username")
uname.send_keys(username)
time.sleep(2)
pword = driver.find_element(By.ID, "password")
pword.send_keys(password)
time.sleep(2)

driver.find_element(By.XPATH, "//button[@type='submit']").click()
desired_url = 'https://www.linkedin.com/feed/'
wait_for_correct_current_url(desired_url)

profiles_data = []

for profile_url in data["profile_urls"]:
    driver.get(profile_url)

    start = time.time()

    initialScroll = 0
    finalScroll = 1000
    while True:
        driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")

        initialScroll = finalScroll
        finalScroll += 1000

        time.sleep(3)

        end = time.time()

        if round(end - start) > 15:
            break

    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')

    intro = soup.find('div', {'class': 'mt2 relative'})

    name_loc = intro.find('h1')
    name = name_loc.text.strip()

    company_loc = soup.find('div', class_='text-body-medium')
    company = company_loc.text.strip()

    location_loc = intro.find_all('span', {'class': 'text-body-small'})
    location = location_loc[0].text.strip()

    print("Name -->", name,
          "\nWorks At -->", company,
          "\nLocation -->", location)

    experience_section = soup.find(lambda tag: tag.name == 'section' and tag.find('div', {'id': 'experience'}))
    experience = experience_section.find('div', {'class': 'pvs-list__outer-container'})
    ul_tag = experience.find('ul')
    li_tags = ul_tag.find_all('li', {'class': 'artdeco-list__item'})
    profiles_data.append({'Name': name, 'Company': company, 'Location': location})

    for li_tag in li_tags:
        job_title = li_tag.find('span').text.strip()
        print(job_title)
        company_exp_loc = li_tag.find_all('span', {'class': 't-14'})
        company_exp = company_exp_loc[0].find('span').text.strip()
        print(company_exp)
        joining_date = company_exp_loc[1].find('span').text.strip()
        print(joining_date)

        experience_text = f'{job_title}, {company_exp}, {joining_date}'

        if 'Experience' in profiles_data[-1]:
            profiles_data[-1]['Experience'] += f'\n{experience_text}'
        else:
            profiles_data[-1]['Experience'] = experience_text

        profiles_data.append({'Name': '', 'Company': '', 'Location':''})

profiles_df = pd.DataFrame(profiles_data)
profiles_df.to_csv('linkedIn.csv', index=False, encoding='utf-8')