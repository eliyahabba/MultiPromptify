import streamlit as st
import json
import os
from src.integration.simple_augmenter import main as simple_augmenter_main

def render():
    st.title("Step 6: Run Augmentations")

    # Ensure we have the output_dir stored from step 5
    if "output_dir" not in st.session_state:
        st.error("No output directory found. Please complete step 5 first.")
        return
    
    output_dir = st.session_state.output_dir
    final_annotations_path = os.path.join(output_dir, "final_annotations.json")

    # Check if final_annotations.json exists
    if not os.path.exists(final_annotations_path):
        st.warning("No final_annotations.json found in the output directory. Please complete step 5 first.")
        return

    # Prepare output file path
    augmented_file = os.path.join(output_dir, "augmented_variations.json")

    st.write("Click the button below to run the augmentation process "
             "using the annotations file from step 5.")

    if st.button("Run Augmentations"):
        # Run the main function of simple_augmenter
        try:
            simple_augmenter_main(final_annotations_path, augmented_file)
            st.success("Augmentations completed successfully!")
        except Exception as e:
            st.error(f"Error running augmentations: {e}")

    # If the augmented file exists, display its contents
    if os.path.exists(augmented_file):
        st.subheader("Augmented Results (Preview)")
        with open(augmented_file, "r") as f:
            data = json.load(f)

        # Display some or all of the results
        st.json(data)

        # Provide a download button
        st.download_button(
            label="Download Augmented Variations as JSON",
            data=json.dumps(data, indent=2),
            file_name="augmented_variations.json",
            mime="application/json"
        ) 