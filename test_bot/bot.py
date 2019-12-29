from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
import time


driver = webdriver.Chrome(executable_path=r'H:\PycharmProjects\Auction\chromedriver_win32\chromedriver.exe')

driver.get("http://localhost:8000/login")

btn = driver.find_element_by_id("button")
login = driver.find_element_by_name("login")
passw = driver.find_element_by_name("pass")

login.send_keys("testUser1")
passw.send_keys("1Q2w3e4r")
btn.click()

driver.get("http://localhost:8000/all_lots")

time.sleep(100)

driver.close()