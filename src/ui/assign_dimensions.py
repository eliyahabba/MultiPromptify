# File: pages/assign_dimensions.py
import streamlit as st
import json
from src.utils.constants import DEFAULT_VARIATIONS_PER_AXIS, MIN_VARIATIONS_PER_AXIS, MAX_VARIATIONS_PER_AXIS


def render():
    st.title("Step 4: Assign Dimensions to Parts")

    with st.expander("ℹ️ What are dimensions?"):
        all_dimensions = st.session_state.base_dimensions + st.session_state.custom_dimensions
        st.json(all_dimensions)

    if "annotated_parts" not in st.session_state or not st.session_state.annotated_parts:
        st.warning("Please annotate prompt parts first.")
        return

    # Initialize state variables if they don't exist
    if "dimension_assignments" not in st.session_state:
        st.session_state.dimension_assignments = {}

    if "dimension_variant_counts" not in st.session_state:
        st.session_state.dimension_variant_counts = {}

    # Collect all unique parts across all prompts
    all_parts = {}
    for example_parts in st.session_state.annotated_parts.values():
        for part_key, text in example_parts["annotations"].items():
            if part_key not in all_parts:
                all_parts[part_key] = text

    # Get all dimension names
    all_dimensions = st.session_state.base_dimensions + st.session_state.custom_dimensions
    all_dimension_names = [d["name"] for d in all_dimensions]

    st.subheader("Assign Dimensions to Each Part")

    # Display each part with its dimensions
    for part_key, text in all_parts.items():
        st.markdown(f"### {part_key.replace('_', ' ').title()}")
        st.text_area("Example Text", value=text, disabled=True, key=f"text_preview_{part_key}")

        # Select dimensions to vary
        multiselect_key = f"dims_{part_key}"
        selected_dims = st.multiselect(
            "Select dimensions to vary",
            options=all_dimension_names,
            key=multiselect_key
        )

        st.session_state.dimension_assignments[part_key] = selected_dims

        # Show variant count inputs if dimensions are selected
        if selected_dims:
            st.markdown("##### Number of Variants per Dimension")

            # Create a more efficient column layout
            cols = st.columns(min(3, len(selected_dims)))

            # Setup counter to cycle through columns
            col_idx = 0

            # Make sure the part exists in the variant counts
            if part_key not in st.session_state.dimension_variant_counts:
                st.session_state.dimension_variant_counts[part_key] = {}

            # Display number inputs for each dimension
            for dim_name in selected_dims:
                # Initialize if needed
                if dim_name not in st.session_state.dimension_variant_counts[part_key]:
                    st.session_state.dimension_variant_counts[part_key][dim_name] = DEFAULT_VARIATIONS_PER_AXIS

                with cols[col_idx]:
                    # Display number input with current value
                    count_key = f"count_{part_key}_{dim_name.replace(' ', '_')}"

                    # Initialize the value in session state if it doesn't exist
                    if count_key not in st.session_state:
                        st.session_state[count_key] = st.session_state.dimension_variant_counts[part_key][dim_name]

                    # Display the number input
                    count_value = st.number_input(
                        f"{dim_name}",
                        min_value=MIN_VARIATIONS_PER_AXIS,
                        max_value=MAX_VARIATIONS_PER_AXIS,
                        value=st.session_state[count_key],
                        key=count_key
                    )

                    # Update the session state for dimension_variant_counts
                    st.session_state.dimension_variant_counts[part_key][dim_name] = st.session_state[count_key]

                    # Debugging: Print the updated value
                    st.write(f"Updated value for {dim_name}: {count_value}")

                    # Update value in session state directly
                    st.session_state.dimension_variant_counts[part_key][dim_name] = count_value

                # Move to next column
                col_idx = (col_idx + 1) % len(cols)

        st.markdown("---")

    # Actions section - all buttons in a vertical sequence
    st.markdown("### Actions")

    # Save button
    if st.button("Save All Assignments to JSON"):
        save_assignments()

    # Create a small space between buttons
    st.markdown("")

    # Continue button
    if st.button("Continue to predict breakdown"):
        if "final_annotations_output" not in st.session_state:
            st.warning("Please save the annotations before proceeding.")
        else:
            st.session_state.page = 5
            st.rerun()


def save_assignments():
    """Extract and save the assignments to the session state"""
    output = []
    for i, parts in st.session_state.annotated_parts.items():
        only_annotations = parts["annotations"]
        entry = {}

        for part, text in only_annotations.items():
            entry[part] = {
                "text": text,
                "dimensions": st.session_state.dimension_assignments.get(part, []),
                "variant_counts": st.session_state.dimension_variant_counts.get(part, {})
            }

        parts["annotations"] = entry
        parts["costume_dimensions"] = st.session_state.custom_dimensions
        output.append(parts)

    st.session_state.final_annotations_output = output

    # Create download button
    json_str = json.dumps(output, indent=2)
    st.download_button(
        "Download JSON",
        data=json_str,
        file_name="final_annotations.json",
        mime="application/json"
    )

    st.success("Assignments saved successfully!")