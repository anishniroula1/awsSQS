# Redefining necessary data as the execution state was reset

# Object with data
x = {
    'experiencedMistreatment': {"additionalExplanation": 'response', 'question': True},
    'fearMistreatment': {"additionalExplanation": 'response', 'question': True},
    'beenImprisoned': {"additionalExplanation": 'response', 'question': False},
    'belongsToOrganization': {"additionalExplanation": 'response', 'question': True},
    'participateInOrganization': {"additionalExplanation": 'response', 'question': True},
    'afraidOfTorture': {"additionalExplanation": 'response', 'question': True}
}

# Key-value mapping for sections
key_to_section = {
    'experiencedMistreatment': 'b1a',
    'fearMistreatment': 'b2a',
    'beenImprisoned': 'b2',
    'belongsToOrganization': 'b3a',
    'participateInOrganization': 'b3b',
    'afraidOfTorture': 'b4'
}

# More concise code using list comprehension
mapped_data_cleaner = [
    {'section_name': key_to_section[key], 'content': value['additionalExplanation']}
    for key, value in x.items() if key in key_to_section and 'additionalExplanation' in value and 'question' in value and value['question']
]

print(mapped_data_cleaner)

