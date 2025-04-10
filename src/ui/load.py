import streamlit as st
from src.ui import ask_user_for_info, upload_csv, annotate_prompt, assign_dimensions, add_dimensions, run_augmentations
from src.ui.progress_indicator import show_progress_indicator
# from src.decompose_tasks import instruction_breakdown
import json

st.set_page_config(layout="wide", page_title="Multi-Prompt Evaluation Tool")


def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 1

    # Total number of pages in the application
    total_pages = 6

    # Display the progress indicator at the top of every page
    current_page = st.session_state.page
    show_progress_indicator(current_page, total_pages)

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
        run_augmentations.render()

if __name__ == '__main__':
    main()