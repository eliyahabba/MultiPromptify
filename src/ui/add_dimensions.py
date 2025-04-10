# File: pages/2_define_dimensions.py
import time

import streamlit as st

def render():
    st.title("Step 3: Define or Review Dimensions")
    st.write("Here are the current default and custom dimensions. You can add more if needed.")

    # Initialize base dimensions if not present
    if "base_dimensions" not in st.session_state:
        st.session_state.base_dimensions = [
            {"id": "order_of_composition", "name": "Order of composition", "description": "", "examples": []},
            {"id": "paraphrases", "name": "Paraphrases", "description": "", "examples": []},
            {"id": "non_semantic", "name": "Non-semantic / structural changes", "description": "", "examples": []},
            {"id": "which_few_shot", "name": "Which few-shot examples", "description": "", "examples": []},
            {"id": "how_many_few_shot", "name": "How many few-shot examples", "description": "", "examples": []},
            {"id": "irrelevant_context", "name": "Add irrelevant context", "description": "", "examples": []},
            {"id": "multi_doc_order", "name": "Order of provided documents", "description": "", "examples": []},
            {"id": "multi_doc_concat", "name": "How to concatenate documents", "description": "", "examples": []},
            {"id": "multi_doc_irrelevant", "name": "Add irrelevant documents", "description": "", "examples": []},
            {"id": "mc_order_of_answers", "name": "Order of answers", "description": "", "examples": []},
            {"id": "mc_enumeration", "name": "Enumeration (letters, numbers, etc)", "description": "", "examples": []}
        ]

    if "custom_dimensions" not in st.session_state:
        st.session_state.custom_dimensions = []

    all_dimensions = st.session_state.base_dimensions + st.session_state.custom_dimensions

    # Display current dimensions
    st.markdown("### 📋 Current Dimensions")
    # with st.expander("📋 Current Dimensions"):
    for dim in all_dimensions:
        st.markdown(f"""
        - **Name**: {dim['name']}  
          **Explanation**: {dim.get('description', '-') or '-'}  
          **Example**: _{', '.join(dim.get('examples', [])) or '-'}_
        """)

    # Add a new dimension
    st.write("### ➕ Add a new dimension")

    with st.form("add_new_dimension"):
        name = st.text_input("Dimension Name")
        description = st.text_area("Description")
        example = st.text_input("Example (optional)")

        submitted = st.form_submit_button("Add Dimension")

        if submitted:
            if name.strip() == "":
                st.warning("Name is required.")
            else:
                new_dim = {
                    "id": name.lower().replace(" ", "_"),
                    "name": name,
                    "description": description,
                    "examples": [example] if example else []
                }
                st.session_state.custom_dimensions.append(new_dim)
                st.success(f"Added new dimension: {name}")
                # stop for 2 seconds
                time.sleep(1.5)
                st.rerun()

    # Button to continue
    if st.button("Continue to Assign Dimensions"):

        st.session_state.page = 4
        st.markdown(
            """
            <script>
                window.scrollTo(0, 0);
            </script>
            """,
            unsafe_allow_html=True
        )
        st.rerun()
