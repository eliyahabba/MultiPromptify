import streamlit as st

def show_progress_indicator(current_page, total_pages=6):
    """
    Display a progress indicator showing which page the user is on and how many remain.
    
    Args:
        current_page: The current page number (1-based)
        total_pages: The total number of pages in the process
    """
    # Calculate progress percentage
    progress_value = current_page / total_pages
    
    # Create a container with custom styling
    with st.container():
        # Add a separator line
        st.markdown('<hr style="margin-top: 0; margin-bottom: 10px;">', unsafe_allow_html=True)
        
        # Display progress text
        st.markdown(f'<p style="text-align: center; margin-bottom: 5px;">Step {current_page} of {total_pages}</p>', 
                  unsafe_allow_html=True)
        
        # Show progress bar
        st.progress(progress_value)
        
        # Page descriptions
        page_descriptions = {
            1: "Upload CSV",
            2: "Annotate Prompt Parts",
            3: "Define Dimensions",
            4: "Assign Dimensions to Parts",
            5: "Predict Prompt Parts",
            6: "Run Augmentations"
        }
        
        # Show current page description
        if current_page in page_descriptions:
            st.markdown(f'<p style="text-align: center; font-weight: bold;">{page_descriptions[current_page]}</p>', 
                      unsafe_allow_html=True)
        
        # Add a separator line
        st.markdown('<hr style="margin-top: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
