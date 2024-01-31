# %%
# Standard Library Imports
import re
import os

# I need an os agnostic way to split on file separator
file_system_separator = os.path.sep[0]


# ----------------------------------------
# Supporting Functions
# ----------------------------------------

def bad_key(
        key: str,
        disallowed_keys=[]) -> bool:
    # Determines if found keyword is a good metadata
    if key.isnumeric():
        return True
    elif key.lower() == 'and':
        return True
    elif len(key) < 3:
        return True
    else:
        return False


def metadata_to_tuples(file_name: str) -> list:
    # Uses regex to find words followed by numbers.

    file_name = file_name.split(file_system_separator)[-1]

    # Insert whitespace between numeric and non-numeric characters
    file_name = re.sub(r'(\d)(\D)', r'\1 \2', file_name)
    file_name = re.sub(r'(\D)(\d)', r'\1 \2', file_name)

    # Replace all whitespace replacement characters with a single space
    file_name = re.sub(r'[_\- ]+', ' ', file_name)

    # Split file_name into keywords and numbers
    metadata_pairs = re.findall(r'(\w+)\s*(\d+)', file_name)

    # Convert number strings to integers, removing numeric keywords
    metadata_pairs = [(key, int(value)) for key, value in metadata_pairs]

    return metadata_pairs


def metadata_to_dict(metadata_tuples: list) -> dict:
    # converts list of tuples to dictionary, filtering out bad pairs
    metadata_dict = {}
    disallowed_keys = []
    for key, value in metadata_tuples:
        if bad_key(key, disallowed_keys):
            continue
        if key in metadata_dict:
            if metadata_dict[key] != value:
                del metadata_dict[key]
                disallowed_keys.append(key)
            continue
        metadata_dict[key] = value
    return metadata_dict


def extract_metadata(file_name: str) -> dict:
    metadata_tuples = metadata_to_tuples(file_name)
    metadata_dict = metadata_to_dict(metadata_tuples)
    return metadata_dict


# ----------------------------------------
# Main Function
# ----------------------------------------


def metadata_from_sample_list(
        sample_list: list,
        frequency_threshold=0.50) -> dict:
    """
    Loops through all sample file names and pulls relevant key value pairs 
    based on regex patterns and filtered based on frequency within experiment

    Args:
        sample_list: A list of sample file paths
        frequency_threshold: The frequency a key needs to exist in the samples to be included

    Returns:
        A dictionary of all samples and pulled metadata:
        {
        full sample loc*: {metadata found in sample file*} 
        }
    """
    threshold = len(sample_list)*frequency_threshold
    sample_metadata = {}
    counter_dict = {}

    # Getting metadata from samples individualy, keeping track of keyword frequency
    for sample in sample_list:
        metadata_dict = extract_metadata(sample)
        for key in metadata_dict.keys():
            if key in counter_dict:
                counter_dict[key] += 1
            else:
                counter_dict[key] = 1
        sample_metadata[sample] = metadata_dict

    # Filter relevant keywords based on frequency
    acceptable_keys = [key for key,
                       value in counter_dict.items() if value > threshold]
    for sample, metadata in sample_metadata.items():
        filtered_metadata = {key: value for key,
                             value in metadata.items() if key in acceptable_keys}
        sample_metadata[sample] = filtered_metadata

    return sample_metadata
