from selenium import webdriver

# checking to see if using Selenium can get past JSTOR blocking. It can't

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
path_to_driver = '/Users/hschilli/anaconda/envs/petal_env/bin/chromedriver'
driver = webdriver.Chrome(path_to_driver, options=options)

url = "https://www.jstor.org/stable/2480681?seq=1"
driver.get(url)

page_source = driver.page_source

print(page_source)
