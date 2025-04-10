import time

import streamlit as st
import json
from src.decompose_tasks import instruction_breakdown
from src.utils.constants import DEFAULT_MODEL
import os

def render():
    st.title("Step 5: Predict Prompt Parts")
    st.markdown("Use a few-shot LLM to automatically extract parts of your prompts.")

    with st.form("prediction_form"):
        st.subheader("🧠 Choose Your Model Platform")
        platform = st.selectbox("Platform", ["TogetherAI", "OpenAI"], key="platform")

        st.subheader(f"🔑 Enter your {platform} API Key")
        api_key = st.text_input(f"{platform} API Key", type="password", key="api_key")

        st.subheader("📦 Model Name")
        model_name = st.text_input("Model Name", key="model_name", value=DEFAULT_MODEL)

        st.subheader("📁 Output Directory")
        output_dir = st.text_input("Output Directory", key="output_dir", value="tmp/")

        submitted = st.form_submit_button("🚀 Start Prediction")

        if submitted:
            missing_fields = []
            for field in ["platform", "api_key", "model_name", "output_dir"]:
                if not st.session_state.get(field):
                    missing_fields.append(field.replace('_', ' ').title())

            if missing_fields:
                st.warning(f"Please fill in the following fields: {', '.join(missing_fields)}.")
            else:
                with st.spinner("Running prediction..."):
                    os.makedirs(output_dir, exist_ok=True)
                    annotations_path = f"{output_dir}/annotations.json"
                    with open(annotations_path, "w") as annotations_file:
                        json.dump(st.session_state.final_annotations_output, annotations_file)

                    all_data_path = f"{output_dir}/all_data.csv"
                    st.session_state.csv_data.to_csv(all_data_path, index=False)
                    out_path = f"{output_dir}/predictions.csv"
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
