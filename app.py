import streamlit as st
import json_req as jr


def main():
    st.set_page_config(layout="wide")

    st.subheader("Energy prices")
    menu = ["Inicio","Sobre nosotros"]

    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Inicio":
        # Create a dataframe
        df = jr.get_prices()
        st.dataframe(df)
    else:
        st.subheader("Data")




if __name__ == "__main__":
    main()