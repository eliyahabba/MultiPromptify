import streamlit as st
from src.ui import upload_csv, annotate_prompt, assign_dimensions, add_dimensions

st.set_page_config(layout="wide", page_title="Multi-Prompt Evaluation Tool")

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 1

    # Render pages
    if st.session_state.page == 1:
        upload_csv.render()
    elif st.session_state.page == 2:
        annotate_prompt.render()
    elif st.session_state.page == 3:
        add_dimensions.render()
    elif st.session_state.page == 4:
        assign_dimensions.render()


if __name__ == '__main__':
    main()