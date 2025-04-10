import json
from datetime import datetime

import pandas as pd
import streamlit as st

from src.integration.combinatorial import VariationCombiner
from src.integration.pipeline import AugmentationPipeline
from src.utils.constants import (
    VARIATION_DIMENSIONS, DEMO_EXAMPLE, DEMO_DIMENSIONS, DEMO_HIGHLIGHTS,
    DEFAULT_VARIATIONS_PER_AXIS, MIN_VARIATIONS_PER_AXIS, MAX_VARIATIONS_PER_AXIS
)


class AppPipeline:
    """
    Manages the application pipeline flow, connecting the UI with the backend processing.
    This class coordinates the different stages of the pipeline within the Streamlit app.
    """

    def __init__(self):
        """Initialize the application pipeline."""
        self.pipeline = AugmentationPipeline()

    def process_annotations(self, df, annotations):
        """Process annotations and apply them to all examples."""
        return self.pipeline.process_annotations(df, annotations)

    def identify_axes(self, prompt, annotations=None):
        """
        Identify variation axes in a prompt.
        
        Args:
            prompt: The input prompt text
            annotations: Optional pre-existing annotations
            
        Returns:
            Dictionary of identified axes
        """
        # Convert annotations to identification data if provided
        identification_data = None
        if annotations:
            identification_data = self._convert_annotations_to_identification_data(
                annotations.get("dimensions", {}),
                annotations.get("highlights", [])
            )

        # Use the pipeline's identifier - FIX: pass only the prompt
        # return self.pipeline.identifier.identify(prompt, identification_data)

        # If we have identification data from annotations, use it directly
        if identification_data:
            return identification_data
        else:
            # Otherwise, use the identifier to generate it
            return self.pipeline.identifier.identify(prompt)

    def generate_variations(self, prompt, identification_data, max_combinations=100):
        """
        Generate variations for a prompt based on identified axes.
        
        Args:
            prompt: The input prompt text
            identification_data: Data about identified variation points
            max_combinations: Maximum number of combinations to generate
            
        Returns:
            Dictionary of variations by axis
        """
        # Use the pipeline to generate variations
        return self.pipeline.process(prompt, identification_data)

    def combine_variations(self, variations_by_axis, max_combinations=100):
        """
        Combine variations from different axes.
        
        Args:
            variations_by_axis: Dictionary mapping axis names to lists of variations
            max_combinations: Maximum number of combinations to generate
            
        Returns:
            List of combined variations
        """
        combiner = VariationCombiner(max_combinations=max_combinations)
        return combiner.combine(variations_by_axis)

    def process_all(self, prompt, annotations=None, max_combinations=100, variations_per_axis=3):
        """
        Process a prompt through the entire pipeline.
        
        Args:
            prompt: The input prompt text
            annotations: Optional pre-existing annotations
            max_combinations: Maximum number of combinations to generate
            variations_per_axis: Number of variations to generate per axis
            
        Returns:
            Dictionary containing results from each stage
        """
        results = {
            "prompt": prompt,
            "identification_data": None,
            "variations_by_axis": {},
            "combined_variations": []
        }

        # Step 1: Identify axes
        results["identification_data"] = self.identify_axes(prompt, annotations)

        # Step 2: Generate variations - pass the number of variations per axis
        # Update the pipeline to use the variations_per_axis parameter
        self.pipeline.augmenter.n_augments = variations_per_axis

        results["variations_by_axis"] = self.generate_variations(
            prompt,
            results["identification_data"],
            max_combinations
        )

        # Step 3: Combine variations
        if results["variations_by_axis"]:
            results["combined_variations"] = self.combine_variations(
                results["variations_by_axis"],
                max_combinations
            )

        return results

    def process_batch(self, all_annotations, max_combinations=100, variations_per_axis=3):
        """
        Process multiple examples based on annotations.
        
        Args:
            all_annotations: List of annotation dictionaries for all examples
            max_combinations: Maximum number of combinations to generate
            variations_per_axis: Number of variations to generate per axis
            
        Returns:
            Dictionary mapping example indices to their results
        """
        results = {}

        for annotation in all_annotations:
            prompt = annotation.get("prompt", "")
            index = annotation.get("index", 0)

            # Process this example
            example_results = self.process_all(
                prompt,
                annotation,
                max_combinations,
                variations_per_axis
            )
            results[index] = example_results

        return results

    def _convert_annotations_to_identification_data(self, dimensions, highlights):
        """
        Convert annotation format to the format expected by the pipeline.
        
        This is a helper method to bridge between the UI annotation format
        and the format expected by the identification/augmentation components.
        """
        # This would contain the actual conversion logic
        # For now, return a simple placeholder
        return {
            "dimensions": dimensions,
            "highlights": highlights
        }


def main():
    """Streamlit app for Multi-Prompt Evaluation Tool."""
    st.set_page_config(layout="wide", page_title="Multi-Prompt Evaluation Tool")

    # Initialize session state variables if they don't exist
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""
    if 'selected_dimensions' not in st.session_state:
        st.session_state.selected_dimensions = []
    if 'highlights' not in st.session_state:
        st.session_state.highlights = []
    if 'variations' not in st.session_state:
        st.session_state.variations = {}
    if 'max_combinations' not in st.session_state:
        st.session_state.max_combinations = 100  # ערך ברירת מחדל
    if 'add_highlight_clicked' not in st.session_state:
        st.session_state.add_highlight_clicked = {}
    if 'csv_data' not in st.session_state:
        st.session_state.csv_data = None
    if 'current_example_index' not in st.session_state:
        st.session_state.current_example_index = 0
    if 'annotated_examples' not in st.session_state:
        st.session_state.annotated_examples = []
    if 'annotation_complete' not in st.session_state:
        st.session_state.annotation_complete = False
    if 'navigation_action' not in st.session_state:
        st.session_state.navigation_action = None
    if 'save_requested' not in st.session_state:
        st.session_state.save_requested = False

    st.title("Multi-Prompt Evaluation Tool")
    st.write("""
    This tool generates variations of prompts without changing their meaning,
    allowing for more robust evaluation of language models.
    """)

    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")

        # Demo button
        if st.button("Load Demo Example"):
            st.session_state.prompt = DEMO_EXAMPLE
            st.session_state.selected_dimensions = DEMO_DIMENSIONS
            st.session_state.highlights = DEMO_HIGHLIGHTS
            # Reset CSV mode
            st.session_state.csv_data = None
            st.session_state.current_example_index = 0
            st.session_state.annotated_examples = []
            st.session_state.annotation_complete = False

    # Input section
    st.header("Input")

    # Two columns for input method
    col1, col2 = st.columns(2)

    with col1:
        input_method = st.radio(
            "Choose input method:",
            ["Text Input", "CSV Upload"]
        )

    with col2:
        # Clear button
        if st.button("Clear All"):
            st.session_state.prompt = ""
            st.session_state.selected_dimensions = []
            st.session_state.highlights = []
            st.session_state.variations = {}
            st.session_state.add_highlight_clicked = {}
            st.session_state.csv_data = None
            st.session_state.current_example_index = 0
            st.session_state.annotated_examples = []
            st.session_state.annotation_complete = False

    # Handle input based on method
    if input_method == "Text Input":
        # Reset CSV mode
        st.session_state.csv_data = None
        st.session_state.current_example_index = 0
        st.session_state.annotated_examples = []
        st.session_state.annotation_complete = False

        col1, col2 = st.columns([3, 1])
        with col1:
            prompt = st.text_area("Enter your prompt:",
                                  value=st.session_state.prompt,
                                  height=200,
                                  key="prompt_input")
        with col2:
            st.write("")  # Add some space
            st.write("")  # Add more space to align with text area
            submit_prompt = st.button("Submit Prompt", key="submit_prompt")

            if submit_prompt and prompt != st.session_state.prompt:
                st.session_state.prompt = prompt
                st.session_state.highlights = []  # Reset highlights when prompt changes
                st.success("Prompt submitted! Now you can select dimensions to vary.")
                # Scroll down to the dimension selection section
                st.markdown('<div id="dimension-selection"></div>', unsafe_allow_html=True)
                st.markdown("""
                <script>
                    document.querySelector('#dimension-selection').scrollIntoView();
                </script>
                """, unsafe_allow_html=True)
    else:
        st.write("Please upload a CSV file with a 'prompt' column containing the prompts to process.")
        uploaded_file = st.file_uploader("Upload CSV file:", type=["csv"])

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if 'prompt' in df.columns:
                    # Store the CSV data in session state
                    if st.session_state.csv_data is None or not df.equals(st.session_state.csv_data):
                        st.session_state.csv_data = df
                        st.session_state.current_example_index = 0
                        st.session_state.annotated_examples = []
                        st.session_state.annotation_complete = False
                        st.session_state.highlights = []

                    # Display CSV info
                    total_examples = len(df)
                    st.info(f"CSV contains {total_examples} examples. You can annotate up to 10 examples.")

                    # Determine how many examples to annotate
                    max_examples = min(10, total_examples)
                    num_examples = st.slider("Number of examples to annotate:", 1, max_examples, 3)

                    # If we have annotated examples, show a way to review them
                    if st.session_state.annotated_examples:
                        st.subheader("Review Annotated Examples")

                        # Create a selection box with the titles of annotated examples
                        annotated_titles = []
                        for ex in st.session_state.annotated_examples:
                            # Extract the title (first line) from the prompt
                            title = ex["prompt"].split('\n')[0][:50] + "..."
                            annotated_titles.append(f"Example {ex['index'] + 1}: {title}")

                        selected_example = st.selectbox(
                            "Select an example to review or edit:",
                            options=range(len(annotated_titles)),
                            format_func=lambda i: annotated_titles[i]
                        )

                        # Button to go to the selected example
                        if st.button("Edit Selected Example", on_click=lambda: edit_selected_example(selected_example)):
                            pass  # The actual editing happens in the callback

                    # If we're in annotation mode
                    if not st.session_state.annotation_complete:
                        # Get the current example
                        current_index = st.session_state.current_example_index

                        if current_index < num_examples:
                            # Display progress
                            st.progress((current_index) / num_examples)
                            st.write(f"Annotating example {current_index + 1} of {num_examples}")

                            # Get the prompt for the current example
                            prompt = df['prompt'].iloc[current_index]
                            st.session_state.prompt = prompt

                            # Navigation buttons
                            col1, col2, col3 = st.columns([1, 1, 1])

                            with col1:
                                if current_index > 0:
                                    st.button("Previous Example", on_click=go_to_previous_example)

                            with col2:
                                # Replace the two separate buttons with a single save button
                                if st.button("Save Annotations", on_click=save_current_annotations_callback):
                                    # Generate JSON data
                                    json_data = generate_json_from_annotations()

                                    if json_data:
                                        # Convert to JSON string
                                        json_str = json.dumps(json_data, indent=2)

                                        # Create a download button
                                        st.download_button(
                                            label="Download JSON",
                                            data=json_str,
                                            file_name=f"prompt_annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                            mime="application/json"
                                        )

                                    # The actual saving of current annotations happens in the callback

                            with col3:
                                next_button_label = "Next Example" if current_index < num_examples - 1 else "Finish Annotation"
                                if st.button(next_button_label, on_click=lambda: go_to_next_example(num_examples)):
                                    pass  # The actual navigation happens in the callback

                            # Display a success message if save was requested
                            if st.session_state.save_requested:
                                if hasattr(st.session_state, 'save_message'):
                                    st.success(st.session_state.save_message)
                                else:
                                    st.success("Annotations saved!")
                                # Reset the flag
                                st.session_state.save_requested = False

                else:
                    st.error("CSV file must contain a 'prompt' column.")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

    # Only proceed with annotation UI if we have a prompt and we're not in the complete state
    if st.session_state.prompt and (input_method == "Text Input" or not st.session_state.annotation_complete):
        # Display the prompt with highlights
        # Display the prompt with highlights
        st.header("Your Prompt")

        # Convert the prompt to HTML with proper line breaks
        prompt_lines = st.session_state.prompt.split('\n')
        html_lines = []

        # Process each line individually to avoid span tag issues across line breaks
        for line_index, line in enumerate(prompt_lines):
            html_line = line
            line_start = sum(len(l) + 1 for l in prompt_lines[:line_index])

            # Find highlights for this line
            line_highlights = []
            for highlight in st.session_state.highlights:
                # Check if highlight overlaps with this line
                h_start = highlight['start']
                h_end = highlight['end']

                # Calculate if the highlight is in this line
                if (h_start >= line_start and h_start < line_start + len(line)) or \
                        (h_end > line_start and h_end <= line_start + len(line)) or \
                        (h_start <= line_start and h_end >= line_start + len(line)):

                    # Calculate relative positions within this line
                    rel_start = max(0, h_start - line_start)
                    rel_end = min(len(line), h_end - line_start)

                    if rel_start < len(line) and rel_end > 0:
                        line_highlights.append({
                            'start': rel_start,
                            'end': rel_end,
                            'dimension': highlight['dimension']
                        })

            # Apply highlights to this line only (in reverse order to avoid index shifting)
            for highlight in sorted(line_highlights, key=lambda h: h['start'], reverse=True):
                dim_id = highlight['dimension']
                dim_color = get_dimension_color(dim_id)

                # Get dimension name for the tooltip
                dim_name = next((dim['name'] for dim in VARIATION_DIMENSIONS if dim['id'] == dim_id), dim_id)

                # Create a highlighted version of the text with styling
                highlighted_text = (
                    f'<span style="background-color: {dim_color}; '
                    f'padding: 2px; border: 1px solid #666; border-radius: 3px;" '
                    f'title="{dim_name}">'
                    f'{html_line[highlight["start"]:highlight["end"]]}'
                    f'</span>'
                )

                # Replace the text in the line
                html_line = (
                        html_line[:highlight['start']] +
                        highlighted_text +
                        html_line[highlight['end']:]
                )

            html_lines.append(html_line)

        # Join the lines with HTML line breaks
        highlighted_prompt = '<br>'.join(html_lines)

        # Create a container with styling to display the highlighted text
        st.markdown("""
        <style>
        .highlighted-prompt {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
            line-height: 1.5;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f'<div class="highlighted-prompt">{highlighted_prompt}</div>', unsafe_allow_html=True)

        # Dimension selection
        st.header("Select Dimensions to Vary")

        # Display dimensions as checkboxes in multiple columns
        cols = st.columns(3)
        selected_dimensions = []

        for i, dim in enumerate(VARIATION_DIMENSIONS):
            col_idx = i % 3
            with cols[col_idx]:
                is_selected = st.checkbox(
                    f"{dim['name']}",
                    help=f"{dim['description']}\nExamples: {', '.join(dim['examples'])}",
                    value=dim['id'] in st.session_state.selected_dimensions
                )
                if is_selected:
                    selected_dimensions.append(dim['id'])

        # Update session state if dimensions changed
        if selected_dimensions != st.session_state.selected_dimensions:
            st.session_state.selected_dimensions = selected_dimensions

        # Only show tabs if dimensions are selected
        if st.session_state.selected_dimensions:
            st.header("Highlight Variation Points")
            st.write("Copy and paste the parts of your prompt that you want to vary for each dimension.")

            # Create tabs for each selected dimension
            tabs = st.tabs([next((dim['name'] for dim in VARIATION_DIMENSIONS if dim['id'] == dim_id), dim_id)
                            for dim_id in st.session_state.selected_dimensions])

            # Process each tab
            for i, tab in enumerate(tabs):
                dim_id = st.session_state.selected_dimensions[i]
                dim_info = next((dim for dim in VARIATION_DIMENSIONS if dim['id'] == dim_id), None)

                # Define callback functions for this dimension
                def add_highlight_callback(dim_id=dim_id, dim_info=dim_info):
                    text_key = f"text_to_vary_{dim_id}"
                    if text_key in st.session_state and st.session_state[text_key]:
                        text_to_vary = st.session_state[text_key]
                        # Find the text in the prompt
                        start_idx = st.session_state.prompt.find(text_to_vary)

                        if start_idx >= 0:
                            end_idx = start_idx + len(text_to_vary)

                            # Check if this text is already highlighted
                            is_duplicate = False
                            for h in st.session_state.highlights:
                                if h['start'] == start_idx and h['end'] == end_idx:
                                    is_duplicate = True
                                    break

                            if not is_duplicate:
                                # Add the highlight
                                st.session_state.highlights.append({
                                    "dimension": dim_id,
                                    "start": start_idx,
                                    "end": end_idx,
                                    "text": text_to_vary
                                })
                                # Clear the text area
                                st.session_state[text_key] = ""
                                return True
                    return False

                with tab:
                    st.write(f"**{dim_info['name']}**: {dim_info['description']}")
                    st.write("Examples: " + ", ".join(dim_info['examples']))

                    # Text area for pasting the text to vary
                    text_to_vary = st.text_area(
                        "Paste the text you want to vary for this dimension:",
                        key=f"text_to_vary_{dim_id}",
                        height=100
                    )

                    # Button to add the highlight with on_click callback
                    if st.button("Add Highlight", key=f"add_highlight_{dim_id}", on_click=add_highlight_callback,
                                 args=(dim_id, dim_info)):
                        st.success(f"Added highlight for {dim_info['name']}")

                    # Display current highlights for this dimension
                    dim_highlights = [h for h in st.session_state.highlights if h['dimension'] == dim_id]
                    if dim_highlights:
                        st.subheader(f"Current Highlights for {dim_info['name']}")
                        for j, highlight in enumerate(dim_highlights):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.text_area(f"Highlight {j + 1}", highlight['text'], height=80,
                                             key=f"highlight_{dim_id}_{j}", disabled=True)
                            with col2:
                                # Define remove callback
                                def remove_highlight(highlight=highlight):
                                    for k, h in enumerate(st.session_state.highlights):
                                        if h == highlight:
                                            st.session_state.highlights.pop(k)
                                            break

                                if st.button("Remove", key=f"remove_{dim_id}_{j}", on_click=remove_highlight,
                                             args=(highlight,)):
                                    pass  # The actual removal happens in the callback

        # Only show processing UI for single text input mode
        if input_method == "Text Input":
            # Processing parameters
            st.header("Processing Parameters")

            col1, col2 = st.columns(2)

            with col1:
                max_combinations = st.slider("Maximum number of combinations:", 1, 500, 100)

            with col2:
                variations_per_axis = st.slider(
                    "Variations per dimension:",
                    MIN_VARIATIONS_PER_AXIS,
                    MAX_VARIATIONS_PER_AXIS,
                    DEFAULT_VARIATIONS_PER_AXIS
                )
                # Store in session state
                st.session_state.variations_per_axis = variations_per_axis

    # Process button
    process_button = st.button("Generate Variations")

    if process_button:
        if not st.session_state.selected_dimensions:
            st.warning("Please select at least one dimension to vary.")
        elif not st.session_state.highlights:
            st.warning("Please highlight at least one variation point in your prompt.")
        else:
            max_combinations = st.session_state.get('max_combinations', 100)

            with st.spinner("Processing..."):
                # Create annotation data from current state
                annotation = {
                    "prompt": st.session_state.prompt,
                    "dimensions": {
                        dim_id: {"name": next((d['name'] for d in VARIATION_DIMENSIONS if d['id'] == dim_id), dim_id)}
                        for dim_id in st.session_state.selected_dimensions},
                    "highlights": st.session_state.highlights
                }

                # Initialize the app pipeline
                app_pipeline = AppPipeline()

                # Process the prompt through the entire pipeline
                results = app_pipeline.process_all(
                    st.session_state.prompt,
                    annotation,
                    max_combinations,
                    st.session_state.get('variations_per_axis', DEFAULT_VARIATIONS_PER_AXIS)
                )

                # Store results in session state
                st.session_state.variations = results["variations_by_axis"]
                st.session_state.combined_variations = results["combined_variations"]

            # Display results if available
            if st.session_state.variations:
                st.header("Results")

                # Display variations by axis
                st.subheader("Variations by Dimension")
                for axis_name, variations in st.session_state.variations.items():
                    with st.expander(f"{axis_name} ({len(variations)} variations)"):
                        for i, var in enumerate(variations):
                            st.text_area(f"Variation {i + 1}", var, height=100, key=f"var_{axis_name}_{i}",
                                         disabled=True)

                # Display combined variations
                if 'combined_variations' in st.session_state:
                    st.subheader(f"Combined Variations ({len(st.session_state.combined_variations)} total)")

                # Create a dataframe for easier viewing
                df = pd.DataFrame({
                    "Variation #": range(1, len(st.session_state.combined_variations) + 1),
                    "Text": st.session_state.combined_variations
                })

                st.dataframe(df)

                # Download button for results
                st.download_button(
                    label="Download Results as CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name='prompt_variations.csv',
                    mime='text/csv',
                )

    # In the annotation complete section
    if st.session_state.annotation_complete:
        st.success("Annotation complete!")

        # Generate JSON data
        json_data = generate_json_from_annotations()

        # Display the JSON in a more readable format
        st.subheader("Annotation Results")

        # Display a summary first
        st.write(f"**Total examples annotated:** {len(json_data)}")

        # Create tabs for different views of the data
        tab1, tab2, tab3 = st.tabs(["Summary View", "JSON View", "Download Options"])

        with tab1:
            # Display a more user-friendly summary of the annotations
            for i, example in enumerate(json_data):
                with st.expander(f"Example {i + 1}: {example['prompt'].split('\\n')[0][:50]}..."):
                    st.write("**Prompt:**")
                    st.text(example["prompt"])

                    st.write("**Dimensions:**")
                    for dim_id, dim_data in example["dimensions"].items():
                        st.write(f"- **{dim_data['name']}**: {len(dim_data['highlights'])} highlights")
                        for j, highlight in enumerate(dim_data['highlights']):
                            st.write(f"  - Highlight {j + 1}: \"{highlight['text']}\"")

        with tab2:
            # Display the raw JSON
            st.json(json_data)

        with tab3:
            # Provide multiple download options
            st.write("**Download Options:**")

            # JSON download
            json_str = json.dumps(json_data, indent=2)
            st.download_button(
                label="Download as JSON",
                data=json_str,
                file_name="prompt_annotations.json",
                mime="application/json"
            )

            # CSV download (flattened version)
            try:
                # Create a flattened version for CSV
                csv_data = []
                for example in json_data:
                    for dim_id, dim_data in example["dimensions"].items():
                        for highlight in dim_data["highlights"]:
                            csv_data.append({
                                "prompt": example["prompt"].replace("\n", " ")[:100] + "...",
                                "dimension": dim_data["name"],
                                "highlight": highlight["text"],
                                "start": highlight["start"],
                                "end": highlight["end"]
                            })

                if csv_data:
                    csv_df = pd.DataFrame(csv_data)
                    st.download_button(
                        label="Download as CSV",
                        data=csv_df.to_csv(index=False).encode('utf-8'),
                        file_name="prompt_annotations.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data to export as CSV.")
            except Exception as e:
                st.error(f"Error creating CSV: {e}")

            # Add a button to return to annotation mode
            if st.button("Return to Annotation Mode", on_click=return_to_annotation_mode):
                pass  # The actual return happens in the callback

            # Button to start processing all examples
            if st.button("Process All Examples"):
                # Count total examples in CSV
                total_examples = len(st.session_state.csv_data) if st.session_state.csv_data is not None else 0
                # Count annotated examples
                annotated_count = len(st.session_state.annotated_examples)

                if st.session_state.csv_data is not None and st.session_state.annotated_examples:
                    with st.spinner("Processing all examples..."):
                        try:
                            # Generate JSON data from annotations
                            annotations = generate_json_from_annotations()

                            # Initialize the app pipeline
                            app_pipeline = AppPipeline()

                            # Step 1: Process annotations to apply to all examples
                            all_annotations = app_pipeline.process_annotations(
                                st.session_state.csv_data,
                                annotations
                            )

                            st.success(f"Successfully processed {len(all_annotations)} examples!")

                            # Step 2: Process all examples through the pipeline
                            max_combinations = 100  # This could be a user input
                            variations_per_axis = st.session_state.get('variations_per_axis',
                                                                       DEFAULT_VARIATIONS_PER_AXIS)

                            batch_results = app_pipeline.process_batch(
                                all_annotations,
                                max_combinations,
                                variations_per_axis
                            )

                            # Store results in session state
                            st.session_state.batch_results = batch_results

                            # Extract variations for display
                            variations_results = {}
                            for idx, result in batch_results.items():
                                variations_results[idx] = result.get("combined_variations", [])

                            # Display summary of results
                            total_variations = sum(len(vars) for vars in variations_results.values())
                            st.success(
                                f"Generated {total_variations} variations across {len(variations_results)} examples!")

                            # Display detailed results
                            st.subheader("Variation Results")

                            # Create tabs for different views
                            tab1, tab2 = st.tabs(["Summary", "Details"])

                            with tab1:
                                # Create a summary table
                                summary_data = []
                                for idx, variations in variations_results.items():
                                    # Get the prompt for this example
                                    example_prompt = next((a["prompt"] for a in all_annotations if a["index"] == idx),
                                                          "")
                                    # Truncate for display
                                    short_prompt = example_prompt[:50] + "..." if len(
                                        example_prompt) > 50 else example_prompt

                                    summary_data.append({
                                        "Example": idx + 1,
                                        "Prompt": short_prompt,
                                        "Variations": len(variations)
                                    })

                                if summary_data:
                                    summary_df = pd.DataFrame(summary_data)
                                    st.dataframe(summary_df)

                            with tab2:
                                # Allow user to select an example to view in detail
                                example_indices = list(variations_results.keys())
                                if example_indices:
                                    selected_example = st.selectbox(
                                        "Select an example to view:",
                                        options=example_indices,
                                        format_func=lambda i: f"Example {i + 1}"
                                    )

                                    # Display variations for the selected example
                                    if selected_example in variations_results:
                                        example_variations = variations_results[selected_example]
                                        st.write(
                                            f"**Example {selected_example + 1} has {len(example_variations)} variations:**")

                                        for i, variation in enumerate(example_variations):
                                            with st.expander(f"Variation {i + 1}"):
                                                st.text(variation)

                            # Provide download options
                            st.subheader("Download Options")

                            # Prepare data for download
                            all_variations = []
                            for idx, variations in variations_results.items():
                                for var in variations:
                                    all_variations.append({
                                        "example_id": idx + 1,
                                        "variation": var
                                    })

                            if all_variations:
                                variations_df = pd.DataFrame(all_variations)

                                # CSV download
                                csv_data = variations_df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="Download All Variations (CSV)",
                                    data=csv_data,
                                    file_name="all_variations.csv",
                                    mime="text/csv"
                                )

                                # JSON download
                                json_data = json.dumps(variations_results, indent=2)
                                st.download_button(
                                    label="Download All Variations (JSON)",
                                    data=json_data,
                                    file_name="all_variations.json",
                                    mime="application/json"
                                )

                        except Exception as e:
                            st.error(f"Error processing examples: {e}")
                else:
                    st.info(f"""
                    This would process all {total_examples} examples in the CSV using the annotations from {annotated_count} examples as a guide.
                    
                    The system would:
                    1. Use the patterns identified in your annotations
                    2. Automatically detect similar patterns in all examples
                    3. Generate variations for each detected pattern
                    4. Create a comprehensive set of prompt variations
                    
                    Please upload a CSV and annotate at least one example to use this feature.
                    """)


def save_current_annotations():
    """Save the current example's annotations to the annotated_examples list."""
    current_index = st.session_state.current_example_index
    prompt = st.session_state.prompt

    # Check if we already have annotations for this example
    existing_index = None
    for i, example in enumerate(st.session_state.annotated_examples):
        if example.get('index') == current_index:
            existing_index = i
            break

    # Prepare the annotation data
    annotation_data = {
        "index": current_index,
        "prompt": prompt,
        "dimensions": st.session_state.selected_dimensions,
        "highlights": st.session_state.highlights
    }

    # Update or append
    if existing_index is not None:
        st.session_state.annotated_examples[existing_index] = annotation_data
    else:
        st.session_state.annotated_examples.append(annotation_data)


def load_annotations_for_current_example():
    """Load annotations for the current example if they exist."""
    current_index = st.session_state.current_example_index

    # Look for annotations for this example
    for example in st.session_state.annotated_examples:
        if example.get('index') == current_index:
            # Load the annotations
            st.session_state.selected_dimensions = example.get('dimensions', [])
            st.session_state.highlights = example.get('highlights', [])
            break


def generate_json_from_annotations():
    """Generate a JSON structure from the annotated examples."""
    json_data = []

    for example in st.session_state.annotated_examples:
        # Create a clean version of the example data
        example_data = {
            "prompt": example["prompt"],
            "dimensions": {}
        }

        # Group highlights by dimension
        for dim_id in example["dimensions"]:
            dim_highlights = [h for h in example["highlights"] if h["dimension"] == dim_id]

            # Get dimension name
            dim_name = next((dim['name'] for dim in VARIATION_DIMENSIONS if dim['id'] == dim_id), dim_id)

            # Add dimension data
            example_data["dimensions"][dim_id] = {
                "name": dim_name,
                "highlights": [
                    {
                        "text": h["text"],
                        "start": h["start"],
                        "end": h["end"]
                    }
                    for h in dim_highlights
                ]
            }

        json_data.append(example_data)

    return json_data


def get_dimension_color(dim_id):
    """Get a color for a dimension."""
    colors = {
        "enumeration": "#FF9999",  # Brighter red
        "separator": "#99FF99",  # Brighter green
        "order": "#9999FF",  # Brighter blue
        "phrasing": "#FFFF99",  # Brighter yellow
        "examples": "#FF99FF"  # Brighter purple
    }
    return colors.get(dim_id, "#CCCCCC")  # Default to light gray


# Define callback functions for navigation
def go_to_previous_example():
    # Save current annotations
    if st.session_state.highlights:
        save_current_annotations()

    # Set navigation action
    st.session_state.navigation_action = "previous"

    # Update the current example index
    if st.session_state.current_example_index > 0:
        st.session_state.current_example_index -= 1

    # Load annotations for the new example
    load_annotations_for_current_example()


def go_to_next_example(num_examples):
    # Save current annotations
    if st.session_state.highlights:
        save_current_annotations()

    # Set navigation action
    st.session_state.navigation_action = "next"

    # Update the current example index
    if st.session_state.current_example_index < num_examples - 1:
        st.session_state.current_example_index += 1
        # Reset highlights for the new example
        st.session_state.highlights = []
        # Load annotations if they exist
        load_annotations_for_current_example()
    else:
        # Finish annotation
        st.session_state.annotation_complete = True


def save_current_annotations_callback():
    """Callback for saving annotations with user feedback."""
    # Set the save requested flag
    st.session_state.save_requested = True

    # Save the annotations
    save_current_annotations()

    # Count how many highlights were saved
    current_index = st.session_state.current_example_index
    highlight_count = 0

    # Find the saved example
    for example in st.session_state.annotated_examples:
        if example.get('index') == current_index:
            highlight_count = len(example.get('highlights', []))
            break

    # Update the save message with more details
    if highlight_count > 0:
        st.session_state.save_message = f"Saved {highlight_count} highlights for example {current_index + 1}."
    else:
        st.session_state.save_message = "No highlights to save for this example."

    # Add information about the JSON download option
    if st.session_state.annotated_examples:
        st.session_state.save_message += " JSON download option is now available."


def edit_selected_example(selected_example):
    # Save current annotations if we're in the middle of annotating
    if not st.session_state.annotation_complete and st.session_state.highlights:
        save_current_annotations()

    # Set the current example index to the selected example
    st.session_state.current_example_index = st.session_state.annotated_examples[selected_example]["index"]

    # Load the annotations for the selected example
    load_annotations_for_current_example()

    # If we were in complete state, go back to annotation mode
    st.session_state.annotation_complete = False


def return_to_annotation_mode():
    st.session_state.annotation_complete = False


if __name__ == "__main__":
    main()
