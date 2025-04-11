import streamlit as st
from src.ui import (
    ask_user_for_info, 
    upload_csv, 
    annotate_prompt, 
    assign_dimensions, 
    add_dimensions, 
    run_augmentations, 
    show_variants
)
from src.ui.progress_indicator import show_progress_indicator
# from src.decompose_tasks import instruction_breakdown
import json

def main():
    # Set up page configuration
    st.set_page_config(layout="wide", page_title="Multi-Prompt Evaluation Tool")
    
    # Initialize session state
    initialize_session_state()

    # Total number of pages in the application
    total_pages = 7

    # Display the progress indicator at the top of every page
    current_page = st.session_state.page
    show_progress_indicator(current_page, total_pages)

    # Render the appropriate page based on the current state
    render_current_page(current_page)

def initialize_session_state():
    """Initialize the session state for navigation"""
    if 'page' not in st.session_state:
        st.session_state.page = 1

def render_current_page(current_page):
    """Render the appropriate page based on the current state"""
    pages = {
        1: upload_csv.render,
        2: annotate_prompt.render,
        3: add_dimensions.render,
        4: assign_dimensions.render,
        5: ask_user_for_info.render,
        6: run_augmentations.render,
        7: show_variants.render
    }
    
    # Call the render function for the current page
    pages[current_page]()

if __name__ == '__main__':
    main()