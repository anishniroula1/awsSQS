# # Redefining necessary data as the execution state was reset

# # Object with data
# x = {
#     'experiencedMistreatment': {"additionalExplanation": 'response', 'question': True},
#     'fearMistreatment': {"additionalExplanation": 'response', 'question': True},
#     'beenImprisoned': {"additionalExplanation": 'response', 'question': False},
#     'belongsToOrganization': {"additionalExplanation": 'response', 'question': True},
#     'participateInOrganization': {"additionalExplanation": 'response', 'question': True},
#     'afraidOfTorture': {"additionalExplanation": 'response', 'question': True}
# }

# # Key-value mapping for sections
# key_to_section = {
#     'experiencedMistreatment': 'b1a',
#     'fearMistreatment': 'b2a',
#     'beenImprisoned': 'b2',
#     'belongsToOrganization': 'b3a',
#     'participateInOrganization': 'b3b',
#     'afraidOfTorture': 'b4'
# }

# # More concise code using list comprehension
# mapped_data_cleaner = [
#     {'section_name': key_to_section[key], 'content': value['additionalExplanation']}
#     for key, value in x.items() if key in key_to_section and 'additionalExplanation' in value and 'question' in value and value['question']
# ]

# print(mapped_data_cleaner)


# Assuming key_to_question and responses are defined as before

key_to_question = {
    'name': 'What is your name?',
    'place': 'Where you from?',
}

responses = [
    {"question": 'What is your name?', 'explanation': "my name is Jon"}, 
    # {"question": 'Where you from?', 'explanation': "I'm from China"},
    {"question": 'Where you going?', 'explanation': "I'm from China"}
]

# Initialize an empty list to store the results
# listx = []

# for response in responses:
#     # Find the key that corresponds to the question in the response
#     for key, question in key_to_question.items():
#         if question == response["question"]:
#             # Map the key to the response
#             res = {
#                 "section_name": key, 
#                 "content": response.get('explanation')
#             }
#             # Append the res dictionary to listx
#             listx.append(res)

# # Output the result
# print(listx)


# Invert key_to_question so that questions map to keys
question_to_key = {v: k for k, v in key_to_question.items()}

# Now, iterate through responses and build listx in a single loop
listx = [
    {"section_name": question_to_key[response["question"]], "content": response["explanation"]}
    for response in responses
    if response["question"] in question_to_key
]

# Output the result
print(listx)
