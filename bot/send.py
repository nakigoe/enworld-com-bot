from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from random import *
import os
os.system("cls") #clear screen from previous sessions
import time
import sqlite3
from datetime import datetime, timedelta

options = webdriver.EdgeOptions()
options.use_chromium = True
options.add_argument("start-maximized")
options.page_load_strategy = 'eager' #do not wait for images to load
options.add_experimental_option("detach", True)
options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.images": 2 # Setting to disable images
})
#options.add_argument('--disable-dev-shm-usage') # uses disk instead of RAM, may be slow

s = 20 #time to wait for a single component on the page to appear, in seconds; increase it if you get server-side errors «try again later»

driver = webdriver.Edge(options=options)
action = ActionChains(driver)
wait = WebDriverWait(driver,s)

username = "nakigoetenshi@gmail.com"
password = "Super Mega Password"
login_page = "https://jobs.enworld.com/s/login/"
jobs_page = "https://jobs.enworld.com/s/"

# Create table to store Facebook pages and dates of sending a message
def create_table():
    conn = sqlite3.connect('jobs-and-dates.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        enworld_job_url TEXT PRIMARY KEY,
        date_sent TEXT
    )
    """)
    conn.commit()
    conn.close()
create_table()
    
def send_a_message(job_url):
    try:
        driver.get(job_url)
        time.sleep(5)
        action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="btn-brand_orange btn-lg"]')))).perform()
        time.sleep(5)
        return 0
    except:
        return 1

def check_and_send_message(enworld_job_url):
    conn = sqlite3.connect('jobs-and-dates.db')
    cursor = conn.cursor()

    # Query for the user by enworld_job_url
    cursor.execute("SELECT date_sent FROM messages WHERE enworld_job_url = ?", (enworld_job_url,))
    result = cursor.fetchone()

    if result:
        date_sent_str = result[0]
        if date_sent_str:
            date_sent = datetime.strptime(date_sent_str, '%Y-%m-%d')
            if datetime.now() - date_sent > timedelta(days=365):
                if send_a_message(enworld_job_url) == 0: #if there is a word 'Sent' in the return message
                    update_date_sent(enworld_job_url)
        else:
            if send_a_message(enworld_job_url) == 0: #if there is a word 'Sent' in the return message
                update_date_sent(enworld_job_url)
    else:
        if send_a_message(enworld_job_url) == 0: #if there is a word 'Sent' in the return message
            insert_user(enworld_job_url)

    conn.close()

def insert_user(enworld_job_url):
    conn = sqlite3.connect('jobs-and-dates.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (enworld_job_url, date_sent) VALUES (?, ?)", (enworld_job_url, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def update_date_sent(enworld_job_url):
    conn = sqlite3.connect('jobs-and-dates.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET date_sent = ? WHERE enworld_job_url = ?", (datetime.now().strftime('%Y-%m-%d'), enworld_job_url))
    conn.commit()
    conn.close()

def login():
    driver.get(login_page)
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@id="input-3"]'))).send_keys(username)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@id="input-4"]'))).send_keys(password)
    action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="btn-brand_orange btn-lg"]')))).perform()

def scroll_to_bottom(): 
    reached_page_end= False
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    #expand the skills list:
    while not reached_page_end:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
            reached_page_end = True
        else:
            last_height = new_height
      
def main():
    login()
    time.sleep(5)
    driver.get(jobs_page)
    time.sleep(5)
    job_links = [] # urls to visit
    
    # harvest all the website job links:
    while True:
        try:
            # harvest all the jobs on the page (can You find a way to display all 2000 jobs on one page?)
            scroll_to_bottom()
            [job_links.append(job_element.get_attribute('href')) for job_element in driver.find_elements(By.XPATH, '//a[@class="job_footer_btn btn-lg"]')]
            
            scroll_to_bottom()
            try:
                action.click(wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "page arrow") and not(@disabled)]/img[@class="rotated"]/parent::button')))).perform()
                time.sleep(3)
            except:
                break # if next page button is inactive
        except: # if no jobs are displayed
            break
    
    for job_link in job_links:
        try:
            check_and_send_message(job_link)
        except:
            continue

    # Close the only tab, will also close the browser.
    os.system("cls") #clear screen from unnecessary logs since the operation has completed successfully
    print("All Your resumes are sent! \n \nSincerely Yours, \nNAKIGOE.ORG\n")
    driver.close()
    driver.quit()
main()