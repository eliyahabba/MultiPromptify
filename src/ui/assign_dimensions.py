# File: pages/assign_dimensions.py
import streamlit as st
import json


def render():
    st.title("Step 4: Assign Dimensions to Parts")

    with st.expander("ℹ️ What are dimensions?"):
        all_dimensions = st.session_state.base_dimensions + st.session_state.custom_dimensions
        st.json(all_dimensions)

    if "annotated_parts" not in st.session_state or not st.session_state.annotated_parts:
        st.warning("Please annotate prompt parts first.")
        return

    # Collect all parts across all prompts
    all_parts = {}
    for example_parts in st.session_state.annotated_parts.values():
        for part_key, text in example_parts["annotations"].items():
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

        if len(assigned) > 0 and assigned != st.session_state.dimension_assignments.get(part_key, []):
            st.session_state.dimension_assignments[part_key] = assigned
            st.rerun()

    # Save final annotations
    if st.button("Save All Assignments to JSON"):
        output = []
        for i, parts in st.session_state.annotated_parts.items():
            only_annotations = parts["annotations"]
            entry = {}
            for part, text in only_annotations.items():
                entry[part] = {
                    "text": text,
                    "dimensions": st.session_state.dimension_assignments.get(part, [])
                }
            parts["annotations"] = entry
            output.append(parts)
        st.session_state.final_annotations_output = output

        json_str = json.dumps(output, indent=2)
        st.download_button("Download JSON", data=json_str, file_name="final_annotations.json", mime="application/json")

    if st.button("Continue to predict breakdown"):
        if not "final_annotations_output" in st.session_state:
            st.warning("Please save the annotations before proceeding.")
            return
        else:
            st.session_state.page = 5
            st.rerun()