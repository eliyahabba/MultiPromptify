# File: pages/annotate_prompt.py
import streamlit as st

num_annotations = 1


def render():
    st.title("Step 2: Annotate Prompt Parts")

    if 'csv_data' not in st.session_state or st.session_state.csv_data is None:
        st.warning("Please upload a CSV first.")
        return

    if 'csv_data_sampled' not in st.session_state:
        df = st.session_state.csv_data.sample(num_annotations, random_state=1)
        st.session_state.csv_data_sampled = df
    idx = st.session_state.current_example_index
    prompt = st.session_state.csv_data_sampled['prompt'].iloc[idx]

    st.header(f"Prompt {idx + 1}/{num_annotations}")
    st.text_area("Prompt", value=prompt, height=200, disabled=True)

    predefined_parts = ['Task Description', 'Context', 'Examples']
    parts = {}

    st.subheader("Annotate Prompt Parts")
    for part in predefined_parts:
        part_key = part.lower().replace(" ", "_")
        text = st.text_area(f"{part} Text", key=f"{idx}_text_{part_key}")
        parts[part_key] = text

    # Custom sections
    st.subheader("Custom Sections")
    if "custom_parts" not in st.session_state:
        st.session_state.custom_parts = []

    new_part = st.text_input("Add a new custom section", key="new_custom_part")
    if st.button("Add Section") and new_part.strip():
        st.session_state.custom_parts.append(new_part.strip())

    for custom in st.session_state.custom_parts:
        custom_key = custom.lower().replace(" ", "_")
        text = st.text_area(f"{custom} Text", key=f"{idx}_text_{custom_key}")
        parts[custom_key] = text

    # Save prompt parts to session state
    if "annotated_parts" not in st.session_state:
        st.session_state.annotated_parts = {}
    st.session_state.annotated_parts[idx] = parts

    # Navigation
    col1, col2 = st.columns(2)
    # with col1:
    #     if idx > 0 and st.button("Previous"):
    #         st.session_state.current_example_index -= 1
    #         st.session_state.prompt = df['prompt'].iloc[st.session_state.current_example_index]
    #         st.rerun()

    with col2:
        if idx < num_annotations - 1 and st.button("Next"):
            st.session_state.current_example_index += 1
            st.session_state.prompt = st.session_state.csv_data_sampled['prompt'].iloc[st.session_state.current_example_index]
            st.rerun()

    if idx == num_annotations - 1:
        if st.button("Move to next part"):
            st.session_state.page = 3
            st.session_state.current_example_index = 0
            for i in range(num_annotations):
                parts = st.session_state.annotated_parts[i]
                full_prompt = st.session_state.csv_data_sampled['prompt'].iloc[i]
                placeholder_prompt = full_prompt
                for part in parts:
                    if len(parts[part]) == 0:
                        continue
                    placeholder_prompt = placeholder_prompt.replace(parts[part], "{"+part.upper()+"}")
                st.session_state.annotated_parts[i] = {"full_prompt": full_prompt,
                                                       "placeholder_prompt": placeholder_prompt,
                                                       "annotations": parts}
            print(st.session_state.annotated_parts)
            st.rerun()
