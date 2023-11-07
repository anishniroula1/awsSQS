def remove_keys_from_dict(original_dict, keys_to_remove):
    """
    Removes multiple keys from a dictionary.

    :param original_dict: The dictionary from which keys are to be removed.
    :param keys_to_remove: A list of keys that need to be removed.
    :return: A new dictionary with specified keys removed.
    """
    # Create a copy of the dictionary to avoid changing the original one
    filtered_dict = original_dict.copy()
    
    for key in keys_to_remove:
        filtered_dict.pop(key, None)  # Use pop to avoid KeyError if the key is not found
    
    return filtered_dict