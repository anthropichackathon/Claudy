
# Define function to get tag content
def get_tag_content(text, tag):
    # Get the content between the tags
    try:
        content = text.split(f"<{tag}>")[1].split(f"</{tag}>")[0]
    except:
        content = ""
    return content

# Define the function that is inserting string between tags in the text
def insert_between_tags(text, tag, content):
    # Insert the content between the tags
    text = text.split(f"<{tag}>")[0] + f"<{tag}>{content}</{tag}>" + text.split(f"</{tag}>")[1]
    return text

def extract_chunks(claude_response):
    # Get the content of the long term memory
    lt_mem_content = get_tag_content(claude_response, "chunks")
    # Change the format of the long term memory into the list of chunks (each chunk is a string)
    lt_mem_content = lt_mem_content.split("<chunk>")[1:]
    lt_mem_content = [chunk.split("</chunk>")[0] for chunk in lt_mem_content]
    return lt_mem_content

