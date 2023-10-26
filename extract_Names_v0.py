import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


# Inputs
USER = "REPLACE THIS WITH YOUR EMAIL ID"
PASS = "REPLACE THIS WITH YOUR PASSWORD"



#Specify the corner coordinates (diagonals only)
Ulat,Blat = 46,44
Llon,Rlon = 26,28

lat_UL= lat_UR = Ulat
lat_BL= lat_BR = Blat

lon_UR= lon_BR = Rlon
lon_UL= lon_BL = Llon

def login(driver, USER, PASS):

    print(f'\nLogging in with email: {USER}')
    BandD = driver.find_element(By.LINK_TEXT, "BrowseAndDownload")
    BandD.click()

    # Loggin into Pradan
    username = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username.clear()
    username.send_keys(USER)
    time.sleep(2)

    passwd = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    passwd.clear()
    passwd.send_keys(PASS)

    time.sleep(2)
    passwd.submit()
    print("Logged in.\n")
    time.sleep(5)

#A function to apply location filter
def apply_coordinate_filter(driver, lat_UL, lon_UL, lat_UR, lon_UR, lat_BR, lon_BR, lat_BL, lon_BL):
    # Select "SystemLevelCoordinates" from the dropdown
    system_level_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "filterForm:filterTable:0:attr")))
    system_level_dropdown.find_element(By.XPATH, "//option[text()='SystemLevelCoordinates']").click()


    # Input the 8 corner coordinates
    coordinates = [(lat_UL, lon_UL), (lat_UR, lon_UR), (lat_BR, lon_BR), (lat_BL, lon_BL)]

    for i, (lat, lon) in enumerate(coordinates):

        lat_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, f"filterForm:filterTable:0:{'ULLat' if i == 0 else 'URLat' if i == 1 else 'BRLat' if i == 2 else 'BLLat'}")))
        lat_input.clear()
        lat_input.send_keys(lat)

        lon_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, f"filterForm:filterTable:0:{'ULLong' if i == 0 else 'URLong' if i == 1 else 'BRLong' if i == 2 else 'BLLong'}")))
        lon_input.clear()
        lon_input.send_keys(lon)

    # Click the filter button
    filter_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "filterForm:filterButton")))
    filter_button.click()
    time.sleep(5)
    
#Displays 100 rows in each page
def display_100(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    # Find the dropdown element
    dropdown = driver.find_element(By.ID, 'tableForm:lazyDocTable:j_id33')

    # Select the "100" option from the dropdown
    dropdown.find_element(By.XPATH, "//option[text()='100']").click()

    j = 1
    time.sleep(20)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    print('Should be displaying 100 rows a page now.\n')

# Defining Firefox browser preferences
profile=Options()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference("browser.download.manager.showAlertOnComplete", False)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")

service = Service(r'geckodriver')
driver = webdriver.Firefox(service=service, options=profile)
driver.maximize_window()
driver.get("https://pradan.issdc.gov.in/ch2/")

#Login with the provided USERNAME and PASSWORD
login(driver, USER, PASS)


# Selecting the section for CLASS on the website
CLASS_data = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "tableForm:payloads:0:j_idt44"))
)
CLASS_data.click()


#Apply the location filter
apply_coordinate_filter(driver, lat_UL, lon_UL, lat_UR, lon_UR, lat_BR, lon_BR, lat_BL, lon_BL)


#Date filter will be added here
#
#
#


# Display 100 rows in a page
display_100(driver)


#Extract total number of pages to scroll
element = driver.find_element(By.XPATH, "//span[contains(@class, 'ui-paginator-current')]")
total_pages_text = element.text
print(f'Starting with: {total_pages_text}...')
total_pages = int(total_pages_text.split()[2])  # Extract the number from the text
print(f'Total pages to scroll: {total_pages}\n')

i = 1

#Loop through every page
while i <= total_pages :


    #Extract filenames from all the rows
    filename_elements = driver.find_elements(By.XPATH, "//td/a")

    #Save the filenames in the text file
    with open(f"filenames_{Ulat}_{Blat}_{Llon}_{Rlon}.txt", "a") as file:
        print(f'Saving filenames from page: {i}\r')
        for element in filename_elements:
            filename = element.text.strip()

            #exclude the XMLs
            if "XML" not in filename:
                file.write(filename + "\n")

    driver.execute_script("window.scrollTo(0, 7000);")
    time.sleep(3)

    if i == total_pages:
        break

    #Go to the next page now
    next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'ui-icon-seek-next')))
    next_button.click()


    # Wait until the current_page changes
    WebDriverWait(driver, 120).until(
        lambda driver: int(driver.find_element(By.XPATH, "//span[contains(@class, 'ui-paginator-current')]").text.split()[0]) != i
    )

    # Update the current_page
    i = int(driver.find_element(By.XPATH, "//span[contains(@class, 'ui-paginator-current')]").text.split()[0])

# Close the browser when done
driver.quit()
print('\nFilename extraction completed')
print('Next step: Download using automated_wget.sh\n')