from anthropic import HUMAN_PROMPT, AI_PROMPT

short_term_memory_template = open("../data/short_term_memory/STM_template.xml", "r").read()
medium_term_memory_template = open("../data/medium_term_memory/MTM_template.xml", "r").read()
long_term_memory_template = open("../data/long_term_memory/LTM_template.xml", "r").read()
bio_template = open("../data/bio/bio_template.xml", "r").read()
def bio_prompt(input):
    prompt = f"{HUMAN_PROMPT}<user_input>{input}</user_input>\n\n<templates>{bio_template}\n{short_term_memory_template}</templates>\n\n<instruction>You are AI assistant inside the personal notes app. The app was just open for the first time. Your job is to fill the templates of the bio and the short term memory, based on the user input. The things that user provided in his input and may be relevant for him (that he would not like to forget), that should not be stored in the bio as the context who they are store inside the slots of short term memory. Do not repeat information from bio in the short term memory</instruction>{AI_PROMPT}"
    return prompt

def decision_prompt(input):
    prompt = f"{HUMAN_PROMPT} <user_input>{input}</user_input> <instruction> You are AI Assistant whose job is to decide if the user wants to retrieve info or if wants to input new info. If the user asks question return his query inside <retrieve> tags. If he just brain dumps info return this info inside the <store> tags. In the same input from the user you can get both question and the info to store inside the memory. In this case return both tags with content.</instruction> {AI_PROMPT}"
    return prompt

def ltm_cleanup_prompt(database_search_results):
    prompt = f"{HUMAN_PROMPT} You are the AI agent who is able to update vector database. This is the current content of the vector database {database_search_results} in the close meaning of the search query. Your job is to detect if the topics duplicate or overlap. If the duplicate try merging chunks into new chunk. If the chunks are to long you can split them (Try to keep chunks up to 500 words). Return new chunks inside the <chunks> tag with <chunk> tag over each chunk. Please retain all info from the original chunks. Provide only chunk text between the tags without any additional info like (document ID, quotation marks over string). Keep separate topics in the separate chunks {AI_PROMPT}"
    return prompt

def mtm_update_promt(mtm_current, mtm_update):
    prompt = f"{HUMAN_PROMPT}<templates>{medium_term_memory_template}</templates>\n\n<instruction>You are AI assistant inside the personal notes app. This is current mt_term_memory {mtm_current}. Your job is to update the info. Based on the new information provided here {mtm_update}. Current info should updated if the new status of things stored in the memory was provided. Return in the format provided in the template</instruction>{AI_PROMPT}"
    return prompt

def output_processing_prompt(bio, memory, user_question):
    prompt = f"{HUMAN_PROMPT}<user_bio>{bio}<user_bio> <memory>{memory}</memory><instruction>You are AI assistant who is trained into helping in retrieve from memory relevant info. Your job is answer user question based on the info you were provided in the user bio and memory. Try to be personalized to the person that is described in the bio. Respond with the answer inside the <response> tags. Do not add any tags inside response tags. If you do no know something do not make up that information, tell that you do not have this information in your memory</instruction> <user_question>{user_question}</user_question>{AI_PROMPT}"
    return prompt

def retrieve_prompt(user_query):
    prompt = f"{HUMAN_PROMPT} <user_input>{user_query}</user_input> <instruction> You are AI Assistant whose job is to optimize user query for the semantic search</instruction> Return query inside the xml tags <optimized_query> Do not return any additional info {AI_PROMPT}"
    return prompt

def stm_cleanup_prompt(stm_current):
    prompt = f"""{HUMAN_PROMPT}\n\n<templates>{medium_term_memory_template} {long_term_memory_template}</templates>\n\n<instruction>You are AI assistant inside the personal notes app. This is current short_term_memory {stm_current}. Your job is to decide where each information from each slot should go. The information that is relevant to the categories defined in the medium term memory (to do list, goals with deadlines and reminders) should be inserted inside the relevant tags inside the medium term memory template. Other information (not specific plans) regarding the future, that user probably would like to retrieve in the future should be placed in the long term memory. Place each specific topic between separate chunk tags. Please return the filled templates in the same format. You can regard the information that is not relevant to the future and does not fit into short-term memory anymore, such as information of the current emotional state of the user or other people from his/her life. Do not place facts that are true only for the current time, such as 'my house is dirty' into long-term memory. If there is information about something to do place it into the medium-term memory.</instruction>\n<example>    <memory_slots>
            ...
            <slot_1>I am hungry, I think I could eat a sandwich</slot_1>
            <slot_2>I have not cleaned my kitchen for ages, and my sink is overflowing with dirty dishes. I am so lazy.</slot_2>
            <slot_3>My boss is mad at me.</slot_3>
            <slot_4>I have a lot of paperwork to do.</slot_4>
            <slot_5>My cat is so cute. I love my cat.</slot_5>
            <slot_6>I have to clean the dishes.</slot_6>
            <slot_7>I have to buy some food.</slot_7>
            <slot_8></slot_8>
            <slot_9></slot_9>
            <slot_10></slot_10>
            ...
            Response:
            <short_term_memory>
        <context>
            This is a short memory of the AI assistant. It is used to store the latest information. The memory contains 10 slots for most current topics.
        </context>
        <daily_to_do_list>
        -Do the paperwork
        -Buy food and eat something
        -Clean the kitchen and the dishes
        </daily_to_do_list>
        <goals_with_deadlines></goals_with_deadlines>
        <reminders></reminders>
    </short_term_memory>
    <long_term_memory>
        <context>
            This is a long-term memory of the AI assistant. It is used to store information that will be passed to the vector database. Each chunk is a piece of information that will be stored in the vector database.
        </context>
        <chunks>
            <chunk>My boss is mad at me.</chunk>
            <chunk>My cat is so cute. I love my cat.</chunk>
        </chunks>
    </long_term_memory>
    
        </memory_slots>
    
        </example>{AI_PROMPT}"""
    return prompt

def stm_update_prompt(stm_current, input):
    prompt = f"{HUMAN_PROMPT}<user_input>{input}</user_input>\n\n<templates>{short_term_memory_template}</templates>\n\n<instruction>You are AI assistant inside the personal notes app. This is current short_term_memory {stm_current}. Your job is to update the slots. Current info should be moved to the back of the memory slots. The new info should be places in the lowest number slots. You can marge new info with old existing one inside the same new slot realising one slot. Try merging the similar topics into one slot. Return in the format as the template with the 10 slots. <example_info_to_marge>'My dog is dirty' + 'I have everywhere in my house dog poe prints' = 'My dog is dirty and made everywhere poe prints'</example_info_to_marge> </instruction>{AI_PROMPT}"
    return prompt