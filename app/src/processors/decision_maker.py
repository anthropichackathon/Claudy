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

def run(processed_input: str):
    decision_response = claude.claude_call(
        llm_setup,
        prompts.decision_prompt(processed_input),
        max_tokens=10_000
    )

    db_instance = SingletonDataFrame()

    # Create store query
    try:
        store_query = tags.get_tag_content(decision_response, "store")
    except:
        store_query = None

    # Create retrieve query
    try:
        retrieve_query = tags.get_tag_content(decision_response, "retrieve")
        print(f"{retrieve_query=}")
    except:
        retrieve_query = None

    if store_query:
        print(f"{store_query=}")
        update_stm(store_query)
        needs_clean_up = stm_cleanup(db_instance)
        if needs_clean_up:
            update_mtm()
            db_count = len(db_instance.get_df())
            if db_count > 1_000:
                ltm_reorganization(db_instance)

    if retrieve_query:
        final_user_response = retrieve_all_memory(db_instance, retrieve_query)
    else:
        final_user_response = ""

    return final_user_response


def update_stm(store_query: str) -> None:
    stm_current = open(f"{DATA_ROOT}/short_term_memory/STM_current.xml", "r").read()
    print(f"{stm_current=}")

    stm_update_response = claude.claude_call(
        llm_setup,
        prompts.stm_update_prompt(stm_current, store_query),
        max_tokens=10_000)

    # Update the short term memory
    print(f"{stm_update_response=}")
    update.stm_update(stm_update_response)


def stm_cleanup(db_instance) -> bool:
    stm_current = open(f"{DATA_ROOT}/short_term_memory/STM_current.xml", "r").read()
    print(f"{stm_current=}")

    # Check if <slot_7> is filled
    if tags.get_tag_content(stm_current, "slot_7") == "":
        clean_up = False
    else:
        clean_up = True

    if clean_up:
        response = claude.claude_call(
            llm_setup,
            prompts.stm_cleanup_prompt(stm_current),
            max_tokens=10_000
        )
        print(f"stm_cleanup {response=}")

        # Get the list of chunks for ltm update
        ltm_update = tags.extract_chunks(response)
        ltm_update_dict = [{"content": chunk} for chunk in ltm_update]
        # Medium term memory update
        update.mtm_temporary(response)

        print(f"stm {ltm_update_dict=}")
        # overwrite STM_current with STM_template
        stm_template = open(f"{DATA_ROOT}/short_term_memory/STM_template.xml", "r").read()
        with open(f"{DATA_ROOT}/short_term_memory/STM_current.xml", "w") as f:
            f.write(stm_template)
        db_instance.insert_embeddings(ltm_update_dict)

    return clean_up


def update_mtm() -> None:
    mtm_template = open(f"{DATA_ROOT}/medium_term_memory/MTM_template.xml", "r").read()
    # Check if the mtm_update.xml file exists in the directory
    # If it does, load it
    if os.path.isfile(f"{DATA_ROOT}/medium_term_memory/MTM_current.xml"):
        mtm_current = open(f"{DATA_ROOT}/medium_term_memory/MTM_current.xml", "r").read()
    else:
        mtm_current = mtm_template
    print(f"{mtm_current=}")

    # Check if the mtm_update.xml file exists in the directory "../data/short_term_memory/"
    # If it does, load it
    if os.path.isfile(f"{DATA_ROOT}/medium_term_memory/MTM_update.xml"):
        mtm_update = open(f"{DATA_ROOT}/medium_term_memory/MTM_update.xml", "r").read()
    else:
        mtm_update = None
    print(f"{mtm_update=}")

    if mtm_update is not None:
        # If the mtm_update.xml file exists, load it into the LLM
        mtm_response = claude.claude_call(
            llm_setup,
            prompts.mtm_update_promt(mtm_current, mtm_update),
            max_tokens=10_000
        )
        print(f"{mtm_response=}")
        # Update the medium term memory
        update.mtm_update(mtm_response)
        # Delete the mtm_update.xml file
        os.remove(f"{DATA_ROOT}/medium_term_memory/MTM_update.xml")


def retrieve_all_memory(db_instance, retrieve_query: str) -> str:
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
    print(f"{ltm_query=}")

    # Get the optimized query
    optimized_query = tags.get_tag_content(ltm_query, "optimized_query")
    print(f"{optimized_query=}")

    # Get the search result
    search_result = db_instance.semantic_search(optimized_query, top_k=20)
    content_results = [el[0] for el in search_result]
    print(f"{content_results=}")

    # Connect all memories into one string
    all_memories = stm_current + mtm_current + f"\n<long_term_memory>{content_results}</long_term_memory>"

    bio = open(f"{DATA_ROOT}/bio/BIO.xml", "r").read()

    final_user_response = claude.claude_call(
        llm_setup,
        prompts.output_processing_prompt(bio, all_memories, retrieve_query),
        max_tokens=10_000
    )
    print(f"{final_user_response=}")

    return final_user_response

def ltm_reorganization(db_instance) -> None:
    latest_results = db_instance.get_latest_data()
    latest_content = [f"{idx + 1}. {el[0]}" for idx, el in enumerate(latest_results)]
    latest_content = "\n".join(latest_content)
    latest_ids = [el[1] for el in latest_results]
    print(f"{latest_content=}")

    response = claude.claude_call(
        llm_setup,
        prompts.ltm_cleanup_prompt(latest_content),
        max_tokens=10_000
    )
    print(f"ltm {response=}")
    # Get the list of chunks for ltm update
    ltm_update = tags.extract_chunks(response)
    ltm_update_dict = [{"content": chunk} for chunk in ltm_update]

    db_instance.delete_data(latest_ids)
    db_instance.insert_embeddings(ltm_update_dict)


if __name__ == '__main__':
    DATA_ROOT = "../../data"
    run("""Tell me something interesting about eiffel tower""")
