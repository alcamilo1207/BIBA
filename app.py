import streamlit as st

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup

# ------------- Settings for Pages -----------
st.set_page_config(layout="wide")

# Keep text only
def get_website_content(url):
    driver = None
    try:
        # Using on Local
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1200')
        options.add_experimental_option("prefs", {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "download.default_directory": r"C:\Users\Camilo Lopez-Salazar\Desktop\code"  # Change this to your desired download directory
            #"download.default_directory": r"C:\Users\Camilo Laptop\PycharmProjects\ATLimplementation\BIBA\Austing"  # Change this to your desired download directory
        })
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                  options=options)
        st.write(f"DEBUG:DRIVER:{driver}")
        driver.get(url)
        time.sleep(5)

        # Locate the download button (inspect the page to get the correct selector)
        first_button = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/download-center/download-center-market-data/form/div/ui-select[4]/div/select/option[2]')
        download_button = driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/download-center/download-center-market-data/form/div/button')

        # Click the download button
        first_button.click()

        st.write("--> Updating server")
        st.write("Waiting...")
        time.sleep(5)

        driver.execute_script("arguments[0].scrollIntoView();", download_button)
        download_button.click()

        st.write("--> Downloading file")
        st.write("Waiting...")

        # Wait for the file to download
        time.sleep(3) 

        driver.quit()

    except Exception as e:
        st.write(f"DEBUG:INIT_DRIVER:ERROR:{e}")
    finally:
        if driver is not None: driver.quit()
    return None




# ---------------- Page & UI/UX Components ------------------------
def main_sidebar():
    # 1.Vertical Menu
    st.header("Running Selenium on Streamlit Cloud")
    site_extraction_page()


def site_extraction_page():
    SAMPLE_URL = "https://www.smard.de/en/downloadcenter/download-market-data/?downloadAttributes=%7B%22selectedCategory%22:3,%22selectedSubCategory%22:8,%22selectedRegion%22:%22DE-LU%22,%22selectedFileType%22:%22CSV%22,%22from%22:1718143200000,%22to%22:1718488799999%7D"
    url = st.text_input(label="URL", placeholder="https://example.com", value=SAMPLE_URL)

    clicked = st.button("Load Page Content",type="primary")
    if clicked:
        with st.container(border=True):
            with st.spinner("Loading page website..."):
                get_website_content(url)
                st.write("File successfully downloaded")


if __name__ == "__main__":
    main_sidebar()
