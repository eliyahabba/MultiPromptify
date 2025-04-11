import time
import os
import json

import streamlit as st
from src.decompose_tasks import instruction_breakdown
from src.utils.constants import DEFAULT_MODEL
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment
API_KEY = os.getenv("TOGETHER_API_KEY")


def render():
    st.title("Step 5: Predict Prompt Parts")
    st.markdown("Use a few-shot LLM to automatically extract parts of your prompts.")

    # Initialize session state variables if they don't exist
    if 'output_dir' not in st.session_state:
        st.session_state['output_dir'] = "tmp/"

    # Initialize other form-related session state variables
    if 'platform' not in st.session_state:
        st.session_state['platform'] = "TogetherAI"
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = API_KEY
    if 'model_name' not in st.session_state:
        st.session_state['model_name'] = DEFAULT_MODEL
    if 'submitted' not in st.session_state:
        st.session_state['submitted'] = False

    # Create a callback function to handle form submission
    def handle_form_submit():
        st.session_state['submitted'] = True
        st.session_state['output_dir'] = st.session_state.output_dir_input
        # Other form values are already in session state due to the keys in the input widgets

    # Create form with pre-filled values from session state
    with st.form(key="prediction_form"):
        st.subheader("🧠 Choose Your Model Platform")
        st.selectbox("Platform", ["TogetherAI", "OpenAI"], key="platform")

        st.subheader(f"🔑 Enter your API Key")
        st.text_input("API Key", type="password", key="api_key", value=API_KEY)

        st.subheader("📦 Model Name")
        st.text_input("Model Name", key="model_name", value=DEFAULT_MODEL)

        st.subheader("📁 Output Directory")
        st.text_input("Output Directory", key="output_dir_input", value=st.session_state['output_dir'])

        # Submit button with callback
        submitted = st.form_submit_button("🚀 Start Prediction", on_click=handle_form_submit)

    # Process form submission based on session state flag
    if st.session_state['submitted']:
        # Reset the submitted flag for next time
        st.session_state['submitted'] = False

        missing_fields = []
        for field in ["platform", "api_key", "model_name", "output_dir_input"]:
            if not st.session_state.get(field):
                missing_fields.append(field.replace('_', ' ').title())

        if missing_fields:
            st.warning(f"Please fill in the following fields: {', '.join(missing_fields)}.")
        else:
            with st.spinner("Running prediction..."):
                output_dir = st.session_state['output_dir']
                os.makedirs(output_dir, exist_ok=True)
                annotations_path = os.path.join(output_dir, "annotations.json")
                with open(annotations_path, "w") as annotations_file:
                    json.dump(st.session_state.final_annotations_output, annotations_file)

                all_data_path = os.path.join(output_dir, "all_data.csv")
                st.session_state.csv_data.to_csv(all_data_path, index=False)
                out_path = os.path.join(output_dir, "predictions.csv")
                if st.session_state.get("platform").lower() == "togetherai":
                    os.environ["TOGETHER_API_KEY"] = st.session_state.api_key
                instruction_breakdown.main(annotation_file=annotations_path,
                                           input_csv=all_data_path,
                                           output_csv=out_path,
                                           input_column="prompt",
                                           model_id=st.session_state.model_name,
                                           delay=0.5,
                                           provider="together")
                st.success("✅ Prediction successful!")
                st.session_state.page = 6
                time.sleep(3)
                st.rerun()