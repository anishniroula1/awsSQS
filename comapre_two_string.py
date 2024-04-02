from Levenshtein import ratio

"""
To compare two strings and determine if they match to at least 98.5%, 
we can use a measure of similarity. One common way to measure the similarity 
between two strings is by using the Levenshtein distance, which calculates the 
minimum number of single-character edits (insertions, deletions, or substitutions) 
required to change one word into the other. We can then calculate the percentage 
match by considering the length of the longest string and the Levenshtein distance 
between the two strings.

Match Percentage = ((1 - (Levenshtein Distance / Length of Longest Distance))  * 100)
"""
def compare_strings(str1, str2):
    # Calculate the similarity ratio using Levenshtein distance
    similarity_ratio = ratio(str1, str2) * 100  # Convert to percentage
    print(similarity_ratio)
    
    # Check if the similarity is at least 98.5%
    if similarity_ratio >= 98:
        return similarity_ratio
    else:
        return 0.0

# Example strings for comparison
string1 ="""
To compare two strings and determine if they match to at least 98.5%, 
we can use a measure of similarity. One common way to measure the similarity 
between two strings is by using the Levenshtein distance, which calculates the 
minimum number of single-character edits (insertions, deletions, or substitutions) 
required to change one word into the other. We can then calculate the percentage 
match by considering the length of the longest string and the Levenshtein distance 
between the two strings.
"""
string2 = """
To compare two strings and determine if they match to at least 98.5%, 
we can use a measure of similarity. One common way to measure the similarity 
between two strings is by using the Levenshtein distance, which calculates the 
minimum number of single-character edits (insertions, deletions, or substitutions) 
required to change one word into the other. We can then calculate the percentage 
match by considering the length of the longest string and the Levenshtein distance 
between the two.
"""
# Compare the two strings
print(compare_strings(string1, string2))
