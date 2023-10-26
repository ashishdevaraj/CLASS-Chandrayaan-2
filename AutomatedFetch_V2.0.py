#!/usr/bin/env python3
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Inputs
USER = "GIVE YOUR PRADHAN USER NAME HERE"
PASS = "GIVE YOUR PASSWORD HERE"

start = "2019-11-11 00:00:00" # start datetime to be searched
end = "2019-11-15 00:00:00" # end datetime to be searched
no_files = 39931 # This number should be noted and editted by loging in once to Pradhan before using the code.
count = 0 # Which count to start from incase of broken download?
DOWNLOAD_DIR = 'GIVE THE COMPLETE PATH WHERE DOWNLOADED FILES TO BE KEPT' # Directory where downloaded files are kept.


## This details are for testing
#start = "2019-11-01 00:00:00"
#end = "2019-11-01 01:00:00"
#no_files = 451
#DOWNLOAD_DIR = '/home/chandrayaan/test/' # Directory where downloaded files are kept.

# Defining Firefox browser preferences
profile=Options()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.dir', DOWNLOAD_DIR)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference("browser.download.manager.showAlertOnComplete", False)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")

# Function to check status of download
def did_you_download():

      dpath = DOWNLOAD_DIR
      os.chdir(dpath)

      string = ".zip.part"

      while string == ".zip.part":
          files = sorted(os.listdir(dpath), key=os.path.getmtime)
          newfile = files[-1]
          string = newfile[-9:]
          time.sleep(2)

      status = "Downloaded: "+newfile
      return status


service = Service(r'/usr/local/bin/geckodriver')
driver = webdriver.Firefox(service=service, options=profile)
driver.get("https://pradan.issdc.gov.in/ch2/")

BandD = driver.find_element(By.LINK_TEXT, "BrowseAndDownload")
BandD.click()

try:

    # Loggin into Pradan
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username.clear()
    username.send_keys(USER)
    time.sleep(2)
    
    passwd = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    passwd.clear()
    passwd.send_keys(PASS)

    time.sleep(2)
    passwd.submit()
    print("\nLogged in.")
    
    # Selecting the section for CLASS on the website
    time.sleep(10)
    CLASS_data = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "tableForm:payloads:0:j_idt49"))
    )
    CLASS_data.click()

    # Filtering the data according to START and END time of observation
    From = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "filterForm:filterTable:0:datetime1_input"))
    )
    From.clear()
    From.send_keys(start)
    
    To = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "filterForm:filterTable:0:datetime2_input"))
    )
    To.clear()
    To.send_keys(end)
    
    time.sleep(2)
    Filter = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "filterForm:filterButton"))
    )
    Filter.click()
    print("Starting download.")

    time.sleep(20)
    # Choosing the FITS files and downloading them as batches of 10MB (404 files in each batch)
    
    while count < no_files:
        # Entering the starting index of the batch
        Start_index = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "tableForm:startIndex")))
        Start_index.clear()
        Start_index.send_keys(count)
        
        Select = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "tableForm:selectButton")))
        Select.click()
        
        # Downloading the batch
        time.sleep(40)
        Download = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "tableForm:download")))
        Download.click()

        # Checking the status of download
        time.sleep(1)
        print(did_you_download())

        count+=404
        time.sleep(5)

finally:
    logouturl = "https://idp.issdc.gov.in/auth/realms/issdc/protocol/openid-connect/logout?redirect_uri=https://pradan.issdc.gov.in/pradan"
    driver.find_element(By.XPATH, '//a[@href="'+logouturl+'"]')
    driver.quit()
    print("Done!!")
