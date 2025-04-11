import json
import os

import pandas as pd
import streamlit as st

from src.integration.simple_augmenter import main as simple_augmenter_main
from src.ui.map_csv_to_json import map_csv_to_json


def render():
    st.title("Step 6: Run Augmentations")

    # Ensure we have the output_dir stored from step 5
    output_dir = st.session_state.get("output_dir")
    st.markdown(f"The output directory is: {output_dir}")

    df = pd.read_csv(os.path.join(output_dir, "predictions.csv"))
    annotations_path = os.path.join(output_dir, "annotations.json")

    # read annotations.json
    with open(annotations_path, "r") as f:
        annotations_data = json.load(f)
    final_json = map_csv_to_json(df, annotations_data)

    # Create a separate button for navigation to avoid conflicts
    col1, col2 = st.columns(2)

    # Only show the Run Augmentations button if no augmented data exists
    if "augmented_data" not in st.session_state:
        with col1:
            st.write(
                "Click the button below to run the augmentation process "
                "using the annotations file from step 5."
            )
            if st.button("Run Augmentations"):
                data = simple_augmenter_main(final_json)
                # Store in session state
                st.session_state["augmented_data"] = data
                st.success("Augmentations completed successfully!")
                # Force a rerun to update the UI state
                st.rerun()

    # Display results if we have augmented data
    if "augmented_data" in st.session_state:
        st.subheader("Augmentation Results")
        st.json(st.session_state["augmented_data"])

        # Provide a download button
        st.download_button(
            label="Download Augmented Variations as JSON",
            data=json.dumps(st.session_state["augmented_data"], indent=2),
            file_name="augmented_variations.json",
            mime="application/json",
            key="download_augmented_file"
        )

        # Clear separation between download and navigation
        st.markdown("---")
        st.subheader("Continue to Next Step")

        # Navigation button in its own container to avoid conflicts
        if st.button("Continue to Step 7 (Show Variants)", key="continue_to_step7"):
            st.session_state.page = 7
            st.rerun()