import streamlit as st
import json
import os

# You can define background colors for each part here
PART_COLORS = {
    "task_description": "#FFD580",  # light orange
    "context": "#BAE7FF",          # light blue
    "examples": "#D3F261",         # light green
    "choices": "#FF9CDD",          # light pink
}


def highlight_parts(final_prompt, parts):
    """
    Replaces each occurrence of parts[part_name] in final_prompt with a colored span
    to highlight it according to the part_name.
    """
    highlighted = final_prompt
    for part_name, part_text in parts.items():
        if not part_text:
            continue
        color = PART_COLORS.get(part_name, "#FFFFB8")  # default light yellow
        highlighted = highlighted.replace(
            part_text,
            f'<span style="background-color: {color}; padding: 2px; margin: 1px; border-radius: 3px;">{part_text}</span>'
        )
    return highlighted


def render():
    st.title("Step 7: Final Variations Display")

    st.markdown("This step reads the file `augmented_variations.json` and shows all variations for each example, with each part highlighted in a different color.")

    # If output_dir is stored in session_state, use that; otherwise default to "src/integration/augmented_variations.json"
    if "output_dir" in st.session_state:
        augmented_file = os.path.join(st.session_state.output_dir, "augmented_variations.json")
    else:
        augmented_file = "src/integration/augmented_variations.json"

    if not os.path.exists(augmented_file):
        st.warning("Could not find `augmented_variations.json`. Please complete the previous steps successfully.")
        return

    with open(augmented_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Display each example
    for example_index, example_item in enumerate(data):
        original_prompt = example_item.get("original_prompt", "")
        variations = example_item.get("variations", [])

        st.markdown(f"### Example {example_index + 1}")
        st.markdown("**Original Prompt:**")
        st.code(original_prompt, language="")

        for var_index, var_item in enumerate(variations):
            final_prompt = var_item.get("final_prompt", "")
            parts = var_item.get("parts", {})

            highlighted_html = highlight_parts(final_prompt, parts)
            st.markdown(f"**Variation {var_index + 1}:**", unsafe_allow_html=True)
            st.markdown(
                f'<div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:10px;">'
                f'{highlighted_html}'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.success("All variations are displayed above.") 