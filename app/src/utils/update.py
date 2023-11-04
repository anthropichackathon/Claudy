import app.src.utils.tags as tags

def bio_update(claude_response):
    bio_template = open("../data/bio/BIO_template.xml", "r").read()
    bio_tags = ["personal_background", "professional_background", "name", "life_goals", "other_info"]
    bio = {}

    for tag in bio_tags:
        # return dict with key: tag, value: content between tags
        bio[tag] = tags.get_tag_content(claude_response, tag)

    # Insert the content between the tags in the bio template
    for tag in bio_tags:
        bio_template = tags.insert_between_tags(bio_template, tag, bio[tag])
    print(bio_template)

    # Save the filled templates to the files
    with open("../data/bio/BIO.xml", "w") as f:
        f.write(bio_template)
    return

def stm_update(claude_response):
    # Update short-term memory

    # Load the template of stm
    stm_template = open("../data/short_term_memory/STM_template.xml", "r").read()

    # Insert the content between the tags in the short-term memory template
    st_memory = []
    for n in range(1, 11):
        st_memory.append(tags.get_tag_content(claude_response, f'slot_{n}'))

    for n in range(1, 11):
        short_term_memory_template = tags.insert_between_tags(stm_template, f'slot_{n}', st_memory[n - 1])

    with open("../data/short_term_memory/STM_current.xml", "w") as f:
        f.write(stm_template)
    return
def mtm_update(claude_response):
    # Update medium term memory
    # Get the content of the medium term memory
    mt_mem_tags = ["to_do_list", "goals_with_deadlines", "reminders"]
    mt_mem_content = {}
    for tag in mt_mem_tags:
        mt_mem_content[tag] = tags.get_tag_content(claude_response, tag)

    # Load the template of mtm
    mtm_template = open("../data/medium_term_memory/MTM_template.xml", "r").read()

    # Fill the template of the medium term memory
    for tag in mt_mem_tags:
        mtm_template = tags.insert_between_tags(mtm_template, tag, mt_mem_content[tag])
    print(mtm_template)

    # Save the filled templates to the files
    with open("../data/medium_term_memory/MTM_current.xml", "w") as f:
        f.write(mtm_template)
    return
