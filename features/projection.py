import re
from unidecode import unidecode

def replace_caps_and_punct(obj):
    if isinstance(obj, dict):
        return {k: replace_caps_and_punct(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_caps_and_punct(elem) for elem in obj]
    elif isinstance(obj, str):
        return re.sub(r'[^\w\s]', '.', unidecode(obj).lower())
    else:
        return obj

def extract_all_values(json_obj):
    all_values = []

    def recurse(obj):
        if isinstance(obj, dict):
            for value in obj.values():
                recurse(value)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)
        else:
            all_values.append(obj)

    recurse(json_obj)
    return all_values