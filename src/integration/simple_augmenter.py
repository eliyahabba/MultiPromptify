"""
A simplified script that applies augmentation based on dimensions in annotations.
"""
import json
import random
from typing import Dict, List, Any
import re

from src.axis_augmentation.augmentation_pipeline import AugmentationPipeline
from src.axis_augmentation.text_surface_augmenter import TextSurfaceAugmenter
from src.axis_augmentation.context_augmenter import ContextAugmenter
from src.axis_augmentation.paraphrase_instruct import Paraphrase
from src.axis_augmentation.multiple_choice_augmenter import MultipleChoiceAugmenter
from src.axis_augmentation.fewshot_augmenter import FewShotAugmenter
from src.axis_augmentation.multidoc_augmenter import MultiDocAugmenter


# Define mapping between dimensions and augmenter classes
DIMENSION_TO_AUGMENTER = {
    "Paraphrases": Paraphrase,
    "Non-semantic / structural changes": TextSurfaceAugmenter,
    "Which few-shot examples": FewShotAugmenter,
    "How many few-shot examples": FewShotAugmenter,
    "Add irrelevant context": ContextAugmenter,
    "Order of provided documents": MultiDocAugmenter,
    "Enumeration (letters, numbers, etc)": MultipleChoiceAugmenter,
    "Order of answers": MultipleChoiceAugmenter,
}


def load_annotations(file_path: str) -> List[Dict[str, Any]]:
    """Load annotations from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_results(results: List[Dict[str, Any]], output_file: str):
    """Save results to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def augment_part(
    text: str,
    dimensions: List[str],
    part_name: str,
    annotations: List[Dict[str, Any]],
    current_index: int
) -> List[str]:
    """
    Augment a text based on its dimensions.
    
    Args:
        text: Text to augment
        dimensions: List of dimensions to apply
        part_name: Name of the part (for special handling)
        annotations: List of all annotations
        current_index: Index of the annotation being processed
        
    Returns:
        List of augmented texts
    """
    if (not text and part_name != "examples") or not dimensions:
        return [text]
    
    # Select augmenters based on dimensions
    augmenters = []
    special_data = {}
    
    for dim in dimensions:
        if dim in DIMENSION_TO_AUGMENTER:
            augmenter_class = DIMENSION_TO_AUGMENTER[dim]
            
            if augmenter_class == FewShotAugmenter:
                import pandas as pd

                few_shot_data = []
                for i, ann in enumerate(annotations):
                    if i != current_index:
                        placeholder_str = ann["placeholder_prompt"]
                        # Remove any placeholders except {CONTEXT}
                        placeholder_str = re.sub(r"\{(?!CONTEXT)[^}]*\}", "", placeholder_str)
                        # Remove text in parentheses
                        placeholder_str = re.sub(r"\([^)]*\)", "", placeholder_str)
                        # Replace {CONTEXT} with the real context
                        real_context = ann["annotations"]["context"]["text"]
                        placeholder_str = placeholder_str.replace("{CONTEXT}", real_context)
                        fs_input = placeholder_str
                        fs_output = ann["annotations"]["output"]["text"]
                        few_shot_data.append({"input": fs_input, "output": fs_output})

                few_shot_df = pd.DataFrame(few_shot_data)

                special_data = {
                    "dataset": few_shot_df
                }

                augmenter = augmenter_class(num_examples=2, n_augments=3)
            else:
                augmenter = augmenter_class(n_augments=3)
                
            # Special handling for multiple choice
            if augmenter_class == MultipleChoiceAugmenter and part_name == "choices":
                # Simple parsing of options (assuming format like "A) Option1 B) Option2")
                parts = text.split(")")
                markers = []
                options = []
                
                for i, part in enumerate(parts[:-1]):  # Skip the last part after final )
                    marker = part.strip().split()[-1]  # Last word before the )
                    markers.append(marker)
                    
                    # Get text between this marker and the next one
                    if i < len(parts) - 2:
                        next_marker_pos = parts[i+1].rfind(parts[i+1].strip().split()[-1])
                        option_text = parts[i+1][:next_marker_pos].strip()
                    else:
                        option_text = parts[i+1].strip()
                    
                    options.append(option_text)
                
                special_data = {
                    "question": "Placeholder question",  # You might want to get this from context
                    "options": options,
                    "markers": markers
                }
            
            augmenters.append(augmenter)
    
    # If no augmenters selected, return original text
    if not augmenters:
        return [text]
    
    # Create pipeline with selected augmenters
    pipeline = AugmentationPipeline(augmenters=augmenters, max_variations=5)
    
    # Apply augmentation
    return pipeline.augment(text, special_data)


def process_annotations(annotations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process all annotations and generate variations."""
    all_results = []
    
    for idx, annotation in enumerate(annotations):
        # Get the placeholder format
        placeholder_format = annotation["placeholder_prompt"]
        
        # Create results for this annotation
        result = {
            "original_prompt": annotation["full_prompt"],
            "variations": []
        }
        
        # Get augmented texts for each part
        part_variations = {}
        
        for part_name, part_data in annotation["annotations"].items():
            text = part_data["text"]
            dimensions = part_data.get("dimensions", [])
            
            variations = augment_part(text, dimensions, part_name, annotations, idx)
            part_variations[part_name] = variations
            print(f"Generated {len(variations)} variations for {part_name}")
        
        # Combine variations (limit to 10 combinations per annotation)
        max_combinations = 20
        count = 0
        
        for task_desc in part_variations.get("task_description", [""]):
            for context in part_variations.get("context", [""]):
                for examples in part_variations.get("examples", [""]):
                    for choices in part_variations.get("choices", [""]):
                        if count >= max_combinations:
                            break
                        
                        # Create new prompt
                        new_prompt = placeholder_format
                        new_prompt = new_prompt.replace("{TASK_DESCRIPTION}", task_desc)
                        new_prompt = new_prompt.replace("{CONTEXT}", context)
                        new_prompt = new_prompt.replace("{EXAMPLES}", examples)
                        new_prompt = new_prompt.replace("{CHOICES}", choices)
                        
                        # Add to results
                        result["variations"].append(new_prompt)
                        count += 1
                    
                    if count >= max_combinations:
                        break
                if count >= max_combinations:
                    break
            if count >= max_combinations:
                break
        
        all_results.append(result)
    
    return all_results


def main():
    """Main function to run the annotation augmentation process."""
    # Set input and output paths
    input_file = "/Users/ehabba/PycharmProjects/MultiPromptify/src/axis_augmentation/final_annotations.json"
    output_file = "augmented_variations.json"
    
    print(f"Loading annotations from {input_file}...")
    annotations = load_annotations(input_file)
    print(f"Loaded {len(annotations)} annotations.")
    
    print("Processing annotations...")
    results = process_annotations(annotations)
    print(f"Generated variations for {len(results)} annotations.")
    
    print(f"Saving results to {output_file}...")
    save_results(results, output_file)
    
    print("Done!")


if __name__ == "__main__":
    main()
