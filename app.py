import streamlit as st
import pandas as pd
import plotly.express as px
import getprices

px.set_mapbox_access_token("pk.eyJ1IjoiYWxjYW1pbG8yIiwiYSI6ImNsdzdmODJoMDIzbWYya3BmdjVidWp3ajcifQ.8NGS13nqm6-MNQ_-SzQbgw")


def load_data(data):
    return pd.read_csv(data)

def my_function():
    st.write("Button has been clicked!")
    # Add any additional logic you want to run when the button is clicked
    return "Function executed successfully!"

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
