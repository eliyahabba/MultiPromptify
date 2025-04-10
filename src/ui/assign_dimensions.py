# File: pages/assign_dimensions.py
import streamlit as st
import json

# # Default flat list of dimensions
# DEFAULT_DIMENSIONS = [
#     ("order_of_composition", "Order of composition"),
#     ("paraphrases", "Paraphrases"),
#     ("non_semantic", "Non-semantic / structural changes"),
#     ("which_few_shot", "Which few-shot examples"),
#     ("how_many_few_shot", "How many few-shot examples"),
#     ("irrelevant_context", "Add irrelevant context"),
#     ("multi_doc_order", "Order of provided documents"),
#     ("multi_doc_concat", "How to concatenate documents"),
#     ("multi_doc_irrelevant", "Add irrelevant documents"),
#     ("mc_order_of_answers", "Order of answers"),
#     ("mc_enumeration", "Enumeration (letters, numbers, etc)"),
# ]

def render():
    st.title("Step 4: Assign Dimensions to Parts")

    if "annotated_parts" not in st.session_state or not st.session_state.annotated_parts:
        st.warning("Please annotate prompt parts first.")
        return

    # Collect all parts across all prompts
    all_parts = {}
    for example_parts in st.session_state.annotated_parts.values():
        for part_key, text in example_parts.items():
            if part_key not in all_parts:
                all_parts[part_key] = text  # take first appearance for display

    # Dimension assignments per part (shared across prompts)
    if "dimension_assignments" not in st.session_state:
        st.session_state.dimension_assignments = {}

    st.subheader("Assign Dimensions to Each Part")

    all_dimensions = st.session_state.base_dimensions + st.session_state.custom_dimensions
    all_dimensions_only_names =  [d["name"] for d in all_dimensions]
    for part_key, text in all_parts.items():
        st.markdown(f"### {part_key.replace('_', ' ').title()}")
        st.text_area("Example Text", value=text, disabled=True, key=f"text_preview_{part_key}")

        assigned = st.multiselect(
            "Select dimensions to vary",
            options=[name for name in all_dimensions_only_names],
            default=st.session_state.dimension_assignments.get(part_key, []),
            key=f"dims_{part_key}"
        )

        st.session_state.dimension_assignments[part_key] = assigned

    # Save final annotations
    if st.button("Save All Assignments to JSON"):
        output = []
        for i, parts in st.session_state.annotated_parts.items():
            entry = {}
            for part, text in parts.items():
                entry[part] = {
                    "text": text,
                    "dimensions": st.session_state.dimension_assignments.get(part, [])
                }
            output.append(entry)

        json_str = json.dumps(output, indent=2)
        st.download_button("Download JSON", data=json_str, file_name="final_annotations.json", mime="application/json")

