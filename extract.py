'''
Kei Imada
20200704
Extracts Swarthmore's GitHub repos
'''

import sys
import time
import getpass
from pathlib import Path

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

import git

PARENT = './github'
Path(PARENT).mkdir(parents=True, exist_ok=True)

GITHUB_URL = 'https://github.swarthmore.edu'
ORG_STUB = '/settings/organizations'

# set selenium options and start
firefox_options = webdriver.FirefoxOptions()
firefox_options.set_headless()
driver = webdriver.Firefox()  # first start with head so user can login

# login
driver.get(GITHUB_URL)
# wait till user logins
print('please log in to github.swarthmore.edu')
wait = WebDriverWait(driver, 60)
try:
    wait.until(lambda driver: GITHUB_URL in driver.current_url)
    print('login successful')
except Exception as e:
    # timeout after 60 seconds
    print('took too long to authenticate')
    driver.quit()
    sys.exit(0)
# save cookies
cookies = driver.get_cookies()
driver.quit()

# start headless session for crawling
driver = webdriver.Firefox(firefox_options=firefox_options)
driver.get(GITHUB_URL + '/api/v3')
for cookie in cookies:
    # load cookies
    driver.add_cookie(cookie)
# scan organizations
print('scanning organizations')
driver.get(GITHUB_URL + ORG_STUB)
# examples of xpaths
# //*[@id="js-pjax-container"]/div/div[2]/div[2]/div[2]/div[1]/strong/a
# //*[@id="js-pjax-container"]/div/div[2]/div[2]/div[3]/div[1]/strong/a
org_elts = driver.find_elements_by_xpath(
    '//*[@id="js-pjax-container"]/div/div[2]/div[2]/div/div[1]/strong/a')
orgs = list(map(lambda e: e.text, org_elts))
print(f'found {len(orgs)} organizations')

git_urls = []

for org in orgs:
    # scan repos from each organization
    print(f'scanning {org}...')
    # make org directory if not exist
    Path(f'{PARENT}/{org}').mkdir(parents=True, exist_ok=True)
    page = 0
    org_repos = []
    while True:
        # while page isn't empty
        page += 1
        url = f'{GITHUB_URL}/{org}?page={page}'
        driver.get(url)
        # examples of xpaths
        # //*[@id="org-repositories"]/div[1]/div/ul/li[1]/div[1]/div[1]/h3/a
        # //*[@id="org-repositories"]/div[1]/div/ul/li[2]/div[1]/div[1]/h3/a
        repo_elements = driver.find_elements_by_xpath(
            '//*[@id="org-repositories"]/div[1]/div/ul/li/div[1]/div[1]/h3/a')
        repos = list(map(lambda e: e.text, repo_elements))
        org_repos += repos
        if not repos:
            break
    # example git url
    # git@github.swarthmore.edu:cs41-02-f17/hw11-kimada1-lpacker1.git
    gurls = list(map(lambda repo: f'git@github.swarthmore.edu:{org}/{repo}.git', org_repos))
    git_urls += gurls
    print(f'found {len(gurls)} repos, extracting...')
    for repo, url in zip(org_repos, gurls):
        print(f'  {repo}', flush=True)
        git.Git(f'{PARENT}/{org}').clone(url)

driver.quit()
