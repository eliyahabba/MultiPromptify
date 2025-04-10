"""Constants for the Multi-Prompt Evaluation Tool."""

# Model configuration
DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
MAX_TOKENS = 2048
TEMPERATURE = 0.7

# Variation dimensions that can be selected
VARIATION_DIMENSIONS = [
    {
        "id": "enumeration",
        "name": "Enumeration Style",
        "description": "Change how options are labeled (A/B/C, 1/2/3, etc.)",
        "examples": ["A) Option", "1) Option", "• Option"]
    },
    {
        "id": "separator",
        "name": "Separators",
        "description": "Change how items are separated (commas, newlines, etc.)",
        "examples": ["Option, Option", "Option | Option", "Option\nOption"]
    },
    {
        "id": "order",
        "name": "Order",
        "description": "Change the order of options or information",
        "examples": ["A, B, C", "C, A, B", "B, C, A"]
    },
    {
        "id": "phrasing",
        "name": "Phrasing",
        "description": "Change how instructions are phrased",
        "examples": ["Select one option", "Choose one of the following", "Pick an option"]
    },
    {
        "id": "examples",
        "name": "Examples",
        "description": "Change the examples provided",
        "examples": ["Example X", "Example Y", "Example Z"]
    }
]

# Demo example for users to try
DEMO_EXAMPLE = """
# Customer Satisfaction Survey

Please rate your experience with our service:

A) Very satisfied
B) Satisfied
C) Neutral
D) Dissatisfied
E) Very dissatisfied

Please provide any additional comments below:
"""

# Demo dimensions to vary in the example
DEMO_DIMENSIONS = ["enumeration", "order", "phrasing"]

# Demo highlights in the example
DEMO_HIGHLIGHTS = [
    {
        "dimension": "enumeration",
        "start": 67,
        "end": 182,
        "text": "A) Very satisfied\nB) Satisfied\nC) Neutral\nD) Dissatisfied\nE) Very dissatisfied"
    },
    {
        "dimension": "phrasing",
        "start": 45,
        "end": 66,
        "text": "Please rate your experience with our service:"
    }
]

# Default number of variations to generate per axis
DEFAULT_VARIATIONS_PER_AXIS = 3

# Minimum and maximum number of variations per axis
MIN_VARIATIONS_PER_AXIS = 1
MAX_VARIATIONS_PER_AXIS = 10

# Constants for MultipleChoiceAugmenter
class MultipleChoiceConstants:
    # Enumeration styles for multiple choice options
    ENUMERATION_STYLES = [
        ["A", "B", "C", "D"],  # uppercase letters
        ["a", "b", "c", "d"],  # lowercase letters
        ["1", "2", "3", "4"],  # numbers
        ["A)", "B)", "C)", "D)"],  # uppercase with bracket
        ["a)", "b)", "c)", "d)"],  # lowercase with bracket
        ["1)", "2)", "3)", "4)"],  # numbers with bracket
    ]

# Constants for MultiDocAugmenter
class MultiDocConstants:
    # Concatenation types
    SINGLE_DOC = "single_doc"
    DOUBLE_NEWLINES = "2_newlines"
    TITLES = "titles"
    DASHES = "dashes"
    
    # Default separator for dashes
    DEFAULT_SEPARATOR_LENGTH = 20
    
    # Document title format
    DOC_TITLE_FORMAT = "Document {}: "

# Constants for FewShotAugmenter
class FewShotConstants:
    # Format strings for examples
    EXAMPLE_FORMAT = "Input: {}\nOutput: {}"
    QUESTION_FORMAT = "Input: {}\nOutput:"
    
    # Separator between examples
    EXAMPLE_SEPARATOR = "\n\n"
    
    # Default random seed for sampling
    DEFAULT_RANDOM_SEED = 42

# Constants for NonLLMAugmenter
class TextSurfaceAugmenterConstants:
    # White space options
    WHITE_SPACE_OPTIONS = ["\n", "\t", " ", ""]
    
    # Keyboard layout for butter finger
    QUERTY_KEYBOARD = {
        "q": "qwasedzx",
        "w": "wqesadrfcx",
        "e": "ewrsfdqazxcvgt",
        "r": "retdgfwsxcvgt",
        "t": "tryfhgedcvbnju",
        "y": "ytugjhrfvbnji",
        "u": "uyihkjtgbnmlo",
        "i": "iuojlkyhnmlp",
        "o": "oipklujm",
        "p": "plo['ik",
        "a": "aqszwxwdce",
        "s": "swxadrfv",
        "d": "decsfaqgbv",
        "f": "fdgrvwsxyhn",
        "g": "gtbfhedcyjn",
        "h": "hyngjfrvkim",
        "j": "jhknugtblom",
        "k": "kjlinyhn",
        "l": "lokmpujn",
        "z": "zaxsvde",
        "x": "xzcsdbvfrewq",
        "c": "cxvdfzswergb",
        "v": "vcfbgxdertyn",
        "b": "bvnghcftyun",
        "n": "nbmhjvgtuik",
        "m": "mnkjloik",
        " ": " "
    }
    
    # Default probabilities
    DEFAULT_TYPO_PROB = 0.05
    DEFAULT_CASE_CHANGE_PROB = 0.1
    
    # Default max outputs
    DEFAULT_MAX_OUTPUTS = 1
    
    # Random ranges for white space generation
    MIN_WHITESPACE_COUNT = 1
    MAX_WHITESPACE_COUNT = 3
    
    # Random index range for white space options
    MIN_WHITESPACE_INDEX = 0
    MAX_WHITESPACE_INDEX = 2
    
    # Transformation techniques
    TRANSFORMATION_TECHNIQUES = ["typos", "capitalization", "punctuation", "spacing"]