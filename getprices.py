from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os, sys

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

_ = installff()
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

def ff():
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    browser = webdriver.Firefox(options=opts)
    
    browser.get('http://example.com')
    st.write(browser.page_source)

def scrap_data():
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("prefs", {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "download.default_directory": r"C:\Users\Camilo Lopez-Salazar\Desktop\code"  # Change this to your desired download directory
        #"download.default_directory": r"C:\Users\Camilo Laptop\PycharmProjects\ATLimplementation\BIBA\Austing"  # Change this to your desired download directory
    })
    
    # Initialize the webdriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the webpage
    driver.get("https://www.smard.de/en/downloadcenter/download-market-data/?downloadAttributes=%7B%22selectedCategory%22:3,%22selectedSubCategory%22:8,%22selectedRegion%22:%22DE-LU%22,%22selectedFileType%22:%22CSV%22,%22from%22:1718143200000,%22to%22:1718488799999%7D")

    print("--> Adjusting parameters")
    print("Waiting...")
    time.sleep(5)


    # Locate the download button (inspect the page to get the correct selector)
    first_button = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/download-center/download-center-market-data/form/div/ui-select[4]/div/select/option[2]')
    download_button = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/download-center/download-center-market-data/form/div/button')

    # Click the download button
    first_button.click()

    print("--> Updating server")
    print("Waiting...")
    time.sleep(5)

    driver.execute_script("arguments[0].scrollIntoView();", download_button)
    download_button.click()

    print("--> Downloading file")
    print("Waiting...")

    # Wait for the file to download
    time.sleep(3)  # Adjust time based on your internet speed and file size

    # Verify the download (optional)
    # download_dir = "/path/to/your/download/directory"
    # files = os.listdir(download_dir)
    # csv_files = [f for f in files if f.endswith('.csv')]
    # if csv_files:
    #     print("CSV file downloaded successfully:", csv_files)
    # else:
    #     print("CSV file not found.")

    # Close the webdriver
    driver.quit()

#if __name__ == "__main__":
#    scrap_data()
