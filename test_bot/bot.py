from selenium import webdriver
import time


driver = webdriver.Chrome(executable_path=r'..\chromedriver_win32\chromedriver.exe')

driver.get("http://localhost:8000/login")

btn = driver.find_element_by_id("button")
login = driver.find_element_by_name("login")
passw = driver.find_element_by_name("pass")

login.send_keys("testUser1")
passw.send_keys("1Q2w3e4r")
btn.click()

driver.get("http://localhost:8000/all_lots")

if len(driver.find_elements_by_class_name("card-title")) == 0:
    driver.get("http://localhost:8000/add_lot")
    driver.find_element_by_id("1").click()
    driver.find_element_by_id("count").send_keys("1")
    driver.find_element_by_id("min_cost").send_keys("1")
    driver.find_element_by_id("max_cost").send_keys("10")
    driver.find_element_by_id("button").click()
    time.sleep(1)
    driver.find_element_by_id("exampleModal").click()
    driver.get("http://localhost:8000/all_lots")
time.sleep(100)
driver.close()