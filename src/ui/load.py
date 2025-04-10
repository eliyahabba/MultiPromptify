import streamlit as st
from src.ui import ask_user_for_info, upload_csv, annotate_prompt, assign_dimensions, add_dimensions
# from src.decompose_tasks import instruction_breakdown
import json
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
    elif st.session_state.page == 5:
        ask_user_for_info.render()
    elif st.session_state.page == 6:
        # run augmentations
        print()


if __name__ == '__main__':
    main()
