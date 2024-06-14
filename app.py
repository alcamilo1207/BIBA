import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@st.experimental_singleton
def get_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def my_function():
    st.write("Button has been clicked!")
    # Add any additional logic you want to run when the button is clicked
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    
    driver = get_driver()
    driver.get('https://www.iana.org/help/example-domains')
    
    st.code(driver.page_source)
    return "Function executed successfully!"

def load_data(data):
    return pd.read_csv(data)
    
def main():
    st.set_page_config(layout="wide")

    st.subheader("Mapa PML")
    menu = ["Inicio","Sobre nosotros"]

    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Inicio":
        # Streamlit application
        st.title("Streamlit Button Click Example")

        st.write("Click the button below to run the function.")

        if st.button("Run Function"):
            result = my_function()
            st.write(result)

    else:
        st.subheader("Data")
        df = load_data("data.csv")
        st.dataframe(df)



if __name__ == "__main__":
    main()
