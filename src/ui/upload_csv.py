# File: pages/upload_csv.py
import streamlit as st
import pandas as pd


def render():
    st.title("Step 1: Upload Your Prompt Dataset")
    st.write("Please upload a CSV file with a `prompt` column.")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if 'prompt' not in df.columns:
                st.error("CSV must contain a 'prompt' column.")
                return

            st.session_state.csv_data = df
            st.success(f"Uploaded {len(df)} prompts.")
            st.write(df.head())

            if st.button("Continue to Annotation"):
                st.session_state.current_example_index = 0
                st.session_state.annotated_examples = []
                st.session_state.annotation_complete = False
                st.session_state.prompt = df['prompt'].iloc[0]
                st.session_state.page = 2
                js = '''
                <script>
                    var body = window.parent.document.querySelector(".main");
                    console.log(body);
                    body.scrollTop = 0;
                </script>
                '''

                st.components.v1.html(js)
                st.rerun()

        except Exception as e:
            st.error(f"Error reading file: {e}")
