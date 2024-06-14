import streamlit as st
import json_req as jr
import schedule_helper as shelp
import mpld3
import streamlit.components.v1 as components


def main():
    st.set_page_config(layout="wide")

    st.subheader("Day-ahead energy prices forecast")

    menu = ["Inicio","Sobre nosotros"]

    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Inicio":
        st.write("Data source: Bundesnetzagentur | SMARD.de. More info: https://www.smard.de/en/datennutzung")
        # Create a dataframe
        df = jr.get_prices()
        st.dataframe(df)

        fig = shelp.get_schedulePlot()
        fig_html = mpld3.fig_to_html(fig)
        components.html(fig_html, height=600)
        #st.pyplot(fig,use_container_width=True)
    else:
        st.subheader("Data")




if __name__ == "__main__":
    main()