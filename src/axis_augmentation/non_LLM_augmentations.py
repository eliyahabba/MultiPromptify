# Non-semantic changes / structural changes (UNI TEXT)
import itertools
import random

def _add_white_spaces_to_single_text(value, option_spaces = ["\n", "\t", " ", ""]):
    """
    Add white spaces to the input text.
    :param text: The input text to augment.
    :param option_spaces: List of white space options to add.
    :return: Augmented text with added white spaces.
    """
    import re

    words = re.split(r"(\s+)", value)
    new_value = ""

    for word in words:
        if word.isspace():
            for j in range(random.randint(1, 3)):
                new_value += option_spaces[random.randint(0, 2)]
        else:
            new_value += word
    return new_value

"""
Text augmentation using the UniText library, that does not require an API key.
"""
def add_white_spaces(inputs, max_outputs=1):
    augmented_texts = []
    for input in inputs:
        augmented_input = []
        for i in range(max_outputs):
            # Apply augmentation
            cur_augmented_texts = _add_white_spaces_to_single_text(input)
            augmented_input.append(cur_augmented_texts)
        augmented_texts.append(augmented_input)
    return augmented_texts


# From NL_Augmentor
def butter_finger(text, prob=0.05, keyboard="querty", seed=0, max_outputs=1):
    random.seed(seed)
    key_approx = {}

    if keyboard == "querty":
        key_approx["q"] = "qwasedzx"
        key_approx["w"] = "wqesadrfcx"
        key_approx["e"] = "ewrsfdqazxcvgt"
        key_approx["r"] = "retdgfwsxcvgt"
        key_approx["t"] = "tryfhgedcvbnju"
        key_approx["y"] = "ytugjhrfvbnji"
        key_approx["u"] = "uyihkjtgbnmlo"
        key_approx["i"] = "iuojlkyhnmlp"
        key_approx["o"] = "oipklujm"
        key_approx["p"] = "plo['ik"

        key_approx["a"] = "aqszwxwdce"
        key_approx["s"] = "swxadrfv"
        key_approx["d"] = "decsfaqgbv"
        key_approx["f"] = "fdgrvwsxyhn"
        key_approx["g"] = "gtbfhedcyjn"
        key_approx["h"] = "hyngjfrvkim"
        key_approx["j"] = "jhknugtblom"
        key_approx["k"] = "kjlinyhn"
        key_approx["l"] = "lokmpujn"

        key_approx["z"] = "zaxsvde"
        key_approx["x"] = "xzcsdbvfrewq"
        key_approx["c"] = "cxvdfzswergb"
        key_approx["v"] = "vcfbgxdertyn"
        key_approx["b"] = "bvnghcftyun"
        key_approx["n"] = "nbmhjvgtuik"
        key_approx["m"] = "mnkjloik"
        key_approx[" "] = " "
    else:
        print("Keyboard not supported.")

    prob_of_typo = int(prob * 100)
    perturbed_texts = []
    for _ in itertools.repeat(None, max_outputs):
        butter_text = ""
        for letter in text:
            lcletter = letter.lower()
            if lcletter not in key_approx.keys():
                new_letter = lcletter
            else:
                if random.choice(range(0, 100)) <= prob_of_typo:
                    new_letter = random.choice(key_approx[lcletter])
                else:
                    new_letter = lcletter
            # go back to original case
            if not lcletter == letter:
                new_letter = new_letter.upper()
            butter_text += new_letter
        perturbed_texts.append(butter_text)
    return perturbed_texts

#From NL-Augmentor
def change_char_case(text, prob=0.1, seed=0, max_outputs=1):
    random.seed(seed)
    results = []
    for _ in range(max_outputs):
        result = []
        for c in text:
            if c.isupper() and random.random() < prob:
                result.append(c.lower())
            elif c.islower() and random.random() < prob:
                result.append(c.upper())
            else:
                result.append(c)
        result = "".join(result)
        results.append(result)
    return results


if __name__ == '__main__':
    # Sample text for augmentation
    inputs = ["The quick brown fox jumps over the lazy dog.", "The rain in Spain stays mainly in the plain."]

    # Example usage
    # augmented_texts = add_white_spaces(inputs)
    # print("Augmented Text:", augmented_texts)

    # Example usage of butter_finger
    #butter_texts = butter_finger(inputs[1], prob=0.2, max_outputs=3)
    #print("Butter Text:", butter_texts)

    # Example usage of change_char_case
    char_case_texts = change_char_case(inputs[0], prob=0.2, max_outputs=3)
    print("Change Char Case Text:", char_case_texts)