# Define the list of allowed section names
allowed_section_names = ["b1a", "b2a", "b2", "b3a", "b3b", "b4"]

# Define the object x
x = {
    'experiencedMistreatment': {
        "additionalExplanation": 'hello',
        'question': True
    },
    'fearMistreatment': {
        "additionalExplanation": 'freind',
        'question': True
    },
    'beenImprisoned': {
        "additionalExplanation": 'oh no',
        'question': True
    },
    'belongsToOrganization': {
        # "additionalExplanation": 'response',
        'question': True
    },
    'participateInOrganization': {
        "additionalExplanation": 'hi',
        'question': True
    },
    'afraidOfTorture': {
        "additionalExplanation": 'mother',
        'question': True
    }
}

# Define the key-value mapping
key_to_section = {
    'experiencedMistreatment': 'b1a',
    'fearMistreatment': 'b2a',
    'beenImprisoned': 'b2',
    'belongsToOrganization': 'b3a',
    'participateInOrganization': 'b3b',
    'afraidOfTorture': 'b4'
}

# Process the object and map keys to section names
mapped_data = []
for key, value in x.items():
    if key in key_to_section:
        section_name = key_to_section[key]
        if 'additionalExplanation' in value:
            content = value['additionalExplanation']
            mapped_data.append({'section_name': section_name, 'content': content})

print(mapped_data)

