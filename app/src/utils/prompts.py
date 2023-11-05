from anthropic import HUMAN_PROMPT, AI_PROMPT
import os

# print(os.listdir("data"))
data_root = "data"
short_term_memory_template = open(f"{data_root}/short_term_memory/STM_template.xml", "r").read()
medium_term_memory_template = open(f"{data_root}/medium_term_memory/MTM_template.xml", "r").read()
long_term_memory_template = open(f"{data_root}/long_term_memory/LTM_template.xml", "r").read()
bio_template = open(f"{data_root}/bio/bio_template.xml", "r").read()
def bio_prompt(input):
    prompt = f"""{HUMAN_PROMPT}<user_input>{input}</user_input>

<templates>
{bio_template}
{short_term_memory_template} 
</templates>

<instruction>
You are an AI assistant inside a personal notes app that helps users record important memories and information about themselves. The app has just been opened for the first time by a new user. 

Your job is to fill in the biography template and short-term memory template based on the details provided in the user's input. The biography template should contain general facts and background information about the user. The short-term memory template should highlight recent events, conversations, and context-specific details that are important for the user to remember but would not necessarily go in a bio.  

When filling the templates, avoid repeating information between the two. The biography section should only contain the user's core identity, history and facts. The short-term memory section should contain situational details that supplement the biography.
</instruction>

{AI_PROMPT}"""
    return prompt

def decision_prompt(input):
    prompt = f"""{HUMAN_PROMPT}<user_input>{input}</user_input>

<instruction> You are an AI assistant helping a user manage their personal memory and knowledge base. Your job is to analyze the user's input and determine if they are asking you to retrieve existing information or provide new information to store.
If the user asks a direct question or requests specific information, return their query wrapped in <retrieve> tags. Use this tag only when you are sure user wants you to retrieve something from their memory.

If the user provides new information for you to record, return this content wrapped in <store> tags.

The user may provide both a question and new information in the same input. In this case, return both <retrieve> and <store> tags with the appropriate content in each.

The key is to identify what the user intends - do they want you to remind them of something in their memory, or are they giving you new details to add to it? Tag their input accordingly. </instruction>

{AI_PROMPT}"""
    return prompt

def ltm_cleanup_prompt(database_search_results):
    prompt = f"""{HUMAN_PROMPT}

You are an AI agent that manages and optimizes a vector database of text chunks.

The current content of the database related to this search query is:
{database_search_results}

Your job is to analyze these chunks and consolidate any duplicate or overlapping information. Specifically:

If multiple chunks contain the same or very similar content, merge them into a single new chunk.
If any chunks are too long (over 250 words), split them into multiple smaller chunks.
Retain all the information from the original chunks, just organized into consolidated topics.
Return the updated set of chunks wrapped in <chunks> tags, with each chunk wrapped in <chunk> tags. Only include the chunk text itself - no additional info like IDs or quotation marks.

The goal is to refine the database to have non-redundant chunks of a readable length covering distinct topics relevant to the search query.

<chunks> <chunk> ((chunk 1 text)) </chunk> <chunk> ((chunk 2 text)) </chunk>
... </chunks>

{AI_PROMPT}"""
    return prompt

def mtm_update_promt(mtm_current, mtm_update):
    prompt = f"""{HUMAN_PROMPT}

<templates> {medium_term_memory_template} </templates> <instruction> You are an AI assistant helping to manage a user's medium-term memory in a personal notes app.
The user's current medium-term memory information is:
{mtm_current}

You have been provided these updates to the medium-term memory:
{mtm_update}

Your job is to update the current medium-term memory template based on the new information. If the updates indicate a change in status or details for something already in the memory, modify that existing information.

Return the updated medium-term memory using the provided template format. Focus on integrating the relevant new details within the existing structure. </instruction>

{AI_PROMPT}"""
    return prompt

def output_processing_prompt(bio, memory, user_question):
    prompt = f"""<user_bio>{bio}</user_bio>

<memory> {memory} </memory> <instruction> You are an AI assistant designed to help users by retrieving relevant information from their personal biography and memory that you have been provided.
When the user asks you a question, your role is to provide a personalized response based on what you know about them from their bio and memory. Respond only with information contained in the bio and memory - do not make up or guess any additional details.

If the user's question relates to something you do not have any information about in the bio or memory, respond by explaining you do not have enough information to answer that particular question.

Craft your responses to show understanding of the user as an individual based on their unique bio and memories. Provide your answer within <response> tags, do not add any other formatting. </instruction>

<user_question>

{user_question}
</user_question>

{AI_PROMPT}"""
    return prompt

def retrieve_prompt(user_query):
    prompt = f"""{HUMAN_PROMPT}<user_input>{user_query}</user_input>

<instruction> You are an AI assistant that optimizes search queries for semantic search.
Your job is to take the user's original query and refine it to improve results from a semantic search engine. Your optimized version should capture the intent and context of the original query in a way that will return the most relevant results.

Return only the optimized query text within <optimized_query> tags. Do not include any other additional information. </instruction>

{AI_PROMPT}"""
    return prompt

def stm_cleanup_prompt(stm_current):
    prompt = f"""{HUMAN_PROMPT}

<templates> {medium_term_memory_template} {long_term_memory_template} </templates> <instruction> You are an AI assistant helping organize personal memories and plans in a notes app.
You are provided the user's current short-term memory:
{stm_current}

Your role is to take this information and transfer relevant parts to the medium and long-term memory templates.

Information and updates about those information related to specific plans, goals with deadlines, and reminders should be added to the relevant sections of the medium-term memory template.
General future thoughts or memories the user may want to revisit later should be added as separate chunks in the long-term memory template.
Current emotional states or transient facts should be disregarded.
Return the updated medium and long-term memory templates in the provided format, integrating the relevant short-term memory information within each.

The key is to sort the short-term details into the appropriate permanent memory section based on the timeframe and relevance of each fact. </instruction>

{AI_PROMPT}"""
    return prompt

def stm_update_prompt(stm_current, input):
    prompt = f"""{HUMAN_PROMPT}<user_input>{input}</user_input>

<templates> {short_term_memory_template} </templates> <instruction> You are an AI assistant helping manage a user's short-term memory slots in a personal notes app.
The user's current short-term memory slots are:
{stm_current}

Your role is to update these slots based on the new input information. Specifically:

Move existing information to higher numbered slots, replacing it with new information in the lower numbered slots. This pushes existing info back in the memory.
Combine new information with existing related information in the same slot where appropriate.
Return the updated short-term memory slots using the provided 10 slot template format.
The goal is to integrate new information into the limited short-term memory slots, merging it with existing related knowledge. </instruction>

{AI_PROMPT}"""
    return prompt
