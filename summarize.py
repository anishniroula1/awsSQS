from transformers import BartForConditionalGeneration, BartTokenizer

def summarize_text(text, tokenizer, model, max_length=150, min_length=30):
    # Encode the input text
    inputs = tokenizer.encode("summarize: " + text, return_tensors='pt', max_length=1024, truncation=True)

    # Generate summary
    summary_ids = model.generate(inputs, max_length=max_length, min_length=min_length, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary

def chunk_text(text, tokenizer, chunk_size=1024):
    # Tokenize the input text
    tokens = tokenizer.encode(text)
    chunks = [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)]
    return chunks

def summarize_large_text(text, chunk_size=1024, max_length=150, min_length=30):
    # Load the BART tokenizer and model
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

    # Chunk the text
    chunks = chunk_text(text, tokenizer, chunk_size=chunk_size)
    summaries = []

    # Summarize each chunk
    for chunk in chunks:
        chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
        summary = summarize_text(chunk_text, tokenizer, model, max_length=max_length, min_length=min_length)
        summaries.append(summary)

    # Combine summaries
    combined_summary = " ".join(summaries)

    # Optionally, summarize the combined summary if it's still too long
    if len(combined_summary) > chunk_size:
        combined_summary = summarize_text(combined_summary, tokenizer, model, max_length=max_length, min_length=min_length)

    return combined_summary

# Example usage
text = """
Your very long essay or text goes here. Make sure it's significantly long to test the chunking and summarizing functionality effectively.
"""
summary = summarize_large_text(text, chunk_size=1024, max_length=300, min_length=50)
print("Summary:", summary)
