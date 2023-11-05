import os

from dotenv import load_dotenv

import app.src.utils.claude as claude
import app.src.utils.prompts as prompts
import app.src.utils.tags as tags
import app.src.utils.update as update
from src.utils.db import SingletonDataFrame
from src.utils.openai import setup_openai

load_dotenv()
setup_openai()
llm_setup = claude.get_anthropic()

DATA_ROOT = "data/"

def run(processed_input: str, logger):
    decision_response = claude.claude_call(
        llm_setup,
        prompts.decision_prompt(processed_input),
        max_tokens=10_000
    )

    db_instance = SingletonDataFrame()

    # Create store query
    try:
        store_query = tags.get_tag_content(decision_response, "store")
        logger.info(f"Information to store: {store_query}")
    except:
        store_query = None

    # Create retrieve query
    try:
        retrieve_query = tags.get_tag_content(decision_response, "retrieve")
        logger.info(f"Information to retrieve: {retrieve_query}")
    except:
        retrieve_query = None

    if store_query:
        update_stm(store_query, logger)
        needs_clean_up = stm_cleanup(db_instance, logger)
        if needs_clean_up:
            update_mtm(logger)
            db_count = len(db_instance.get_df())
            if db_count > 1_000:
                ltm_reorganization(db_instance, logger)

    if retrieve_query:
        final_user_response = retrieve_all_memory(db_instance, retrieve_query, logger)
    else:
        final_user_response = ""

    return final_user_response


def update_stm(store_query: str, logger) -> None:
    logger.info(f"Running short term memory update module...")
    stm_current = open(f"{DATA_ROOT}/short_term_memory/STM_current.xml", "r").read()

    stm_update_response = claude.claude_call(
        llm_setup,
        prompts.stm_update_prompt(stm_current, store_query),
        max_tokens=10_000)

    # Update the short term memory
    update.stm_update(stm_update_response)
    logger.info(f"Short term memory updated.")


def stm_cleanup(db_instance, logger) -> bool:
    logger.info(f"Checking if short term memory needs cleanup...")
    stm_current = open(f"{DATA_ROOT}/short_term_memory/STM_current.xml", "r").read()

    # Check if <slot_7> is filled
    if tags.get_tag_content(stm_current, "slot_7") == "":
        clean_up = False
        logger.info(f"Memory still has some capacity.")
    else:
        clean_up = True
        logger.info(f"Running short term memory cleanup module...")

    if clean_up:
        response = claude.claude_call(
            llm_setup,
            prompts.stm_cleanup_prompt(stm_current),
            max_tokens=10_000
        )

        # Get the list of chunks for ltm update
        ltm_update = tags.extract_chunks(response)
        ltm_update_dict = [{"content": chunk} for chunk in ltm_update]
        # Medium term memory update
        update.mtm_temporary(response)

        # overwrite STM_current with STM_template
        stm_template = open(f"{DATA_ROOT}/short_term_memory/STM_template.xml", "r").read()
        with open(f"{DATA_ROOT}/short_term_memory/STM_current.xml", "w") as f:
            f.write(stm_template)
        db_instance.insert_embeddings(ltm_update_dict)
        logger.info(f"Short term memory moved into medium and long term memory.")

    return clean_up


def update_mtm(logger) -> None:
    logger.info(f"Running medium term memory update module...")
    mtm_template = open(f"{DATA_ROOT}/medium_term_memory/MTM_template.xml", "r").read()
    # Check if the mtm_update.xml file exists in the directory
    # If it does, load it
    if os.path.isfile(f"{DATA_ROOT}/medium_term_memory/MTM_current.xml"):
        mtm_current = open(f"{DATA_ROOT}/medium_term_memory/MTM_current.xml", "r").read()
    else:
        mtm_current = mtm_template

    # Check if the mtm_update.xml file exists in the directory "../data/short_term_memory/"
    # If it does, load it
    if os.path.isfile(f"{DATA_ROOT}/medium_term_memory/MTM_update.xml"):
        mtm_update = open(f"{DATA_ROOT}/medium_term_memory/MTM_update.xml", "r").read()
    else:
        mtm_update = None

    if mtm_update is not None:
        # If the mtm_update.xml file exists, load it into the LLM
        mtm_response = claude.claude_call(
            llm_setup,
            prompts.mtm_update_promt(mtm_current, mtm_update),
            max_tokens=10_000
        )
        # Update the medium term memory
        update.mtm_update(mtm_response)
        # Delete the mtm_update.xml file
        os.remove(f"{DATA_ROOT}/medium_term_memory/MTM_update.xml")
        logger.info(f"Medium term memory updated.")


def retrieve_all_memory(db_instance, retrieve_query: str, logger) -> str:
    logger.info(f"Running all memory retrieval module...")
    # Load short-term memory
    if os.path.isfile(f"{DATA_ROOT}/short_term_memory/STM_current.xml"):
        stm_current = open(f"{DATA_ROOT}/short_term_memory/STM_current.xml", "r").read()
    else:
        stm_current = ""

    if os.path.isfile(f"{DATA_ROOT}/medium_term_memory/MTM_current.xml"):
        mtm_current = open(f"{DATA_ROOT}/medium_term_memory/MTM_current.xml", "r").read()
    else:
        mtm_current = ""

    ltm_query = claude.claude_call(
        llm_setup,
        prompts.retrieve_prompt(retrieve_query),
        max_tokens=300
    )

    # Get the optimized query
    logger.info(f"Optimizing user's query for semantic search...")
    optimized_query = tags.get_tag_content(ltm_query, "optimized_query")
    logger.info(f"Optimized query: {optimized_query}")

    # Get the search result
    search_result = db_instance.semantic_search(optimized_query, top_k=20)
    content_results = [el[0] for el in search_result]

    # Connect all memories into one string
    all_memories = stm_current + mtm_current + f"\n<long_term_memory>{content_results}</long_term_memory>"

    bio = open(f"{DATA_ROOT}/bio/BIO.xml", "r").read()

    final_user_response = claude.claude_call(
        llm_setup,
        prompts.output_processing_prompt(bio, all_memories, retrieve_query),
        max_tokens=10_000
    )

    return final_user_response

def ltm_reorganization(db_instance, logger) -> None:
    logger.info(f"More than 1000 instances, running long term memory reorganization module...")
    latest_results = db_instance.get_latest_data()
    latest_content = [f"{idx + 1}. {el[0]}" for idx, el in enumerate(latest_results)]
    latest_content = "\n".join(latest_content)
    latest_ids = [el[1] for el in latest_results]

    response = claude.claude_call(
        llm_setup,
        prompts.ltm_cleanup_prompt(latest_content),
        max_tokens=10_000
    )
    # Get the list of chunks for ltm update
    ltm_update = tags.extract_chunks(response)
    ltm_update_dict = [{"content": chunk} for chunk in ltm_update]

    db_instance.delete_data(latest_ids)
    db_instance.insert_embeddings(ltm_update_dict)
    logger.info(f"Long term memory reorganized.")


if __name__ == '__main__':
    DATA_ROOT = "../../data"
    run("""Tell me something interesting about eiffel tower""")
