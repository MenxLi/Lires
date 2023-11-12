import sys
import asyncio
from lires.confReader import DATABASE_DIR, VECTOR_DB_PATH
from lires.core.textUtils import retrieveRelevantSections
from lires.core.pdfTools import getPDFText
from lires.core.utils import BCOLORS
from lires.core.serverConn import IServerConn
from lires.core.dataClass import DataBase
from tiny_vectordb import VectorDatabase
from lires_ai.lmInterface import ChatStreamIterType

class AI:
    def __init__(self, iconn: IServerConn):
        self.iconn = iconn
        self.conv_dict = {
            "system": "A conversation between an AI assistant and a human. ",
            "conversations": []
        }
    
    def __call__(self, input_str: str, verbose: bool = True):
        global MODEL
        res = self.iconn.chat(
            input_str,
            conv_dict=self.conv_dict,
            model_name=MODEL
            # model_name="stabilityai/StableBeluga-7B"
        )
        ans = ""
        for t in res:
            if verbose: print(t, end = "", flush=True)
            ans += t
        self.conv_dict["conversations"].append((
            "user", input_str
        ))
        self.conv_dict["conversations"].append((
            "assistant", ans
        ))
        return ans

def extractAction(ans: str):
    """
    Ask LLM to summarize the action into JSON format.
    """
    global MODEL

    system = "You are an AI that is responsible for summarizing some words into JSON format. "

    conv_dict = {
        "system": system,
        "conversations": []
    }
    res = iconn.chat(
        "Please summarize a speaking into JSON object format with two entries: action and action_input. "
        "The action can be seaching for information, or answering questions. "
        'The action name must be one of "search" or "answer". \n'+
        "i.e. {'action': 'search', 'action_input': 'The largest city in China'} or {'action': 'answer', 'action_input': 'The largest city in China is Beijing, It has a population of 21.54 million and is the second largest city proper by population in the world.'}. \n"+
        'The other entry must be named as "action_input", which is the input of the action. \n'+
        "If you determine the action to be answer, please provide a thorough and detailed answer. \n"+
        "(Note: The above is an example, please fill in the action and action_input with your own words.) \n"
        "-----\n"
        "Here is the speaking, please summarize it in the above mentioned json format: {}".format(ans),
        conv_dict=conv_dict,
        model_name=MODEL
        # model_name="stabilityai/StableBeluga-7B"
        )
    ret = ""
    for t in res:
        print(t, end = "", flush=True)
        ret += t
    return ret.replace('"', "'").replace('\_', '_')

def searchForInfo(query: str):
    print("\nSearching for information: {}{}".format(BCOLORS.GREEN, query), end=BCOLORS.ENDC + "\n")
    database = DataBase(DATABASE_DIR)
    vector_collection = VectorDatabase(VECTOR_DB_PATH, [{"name": "doc_feature", "dimension": 768}])["doc_feature"]

    query_vec = iconn.featurize(query)

    related_article_uids, _ = vector_collection.search(query_vec, 8)

    related_articles = [database[uid] for uid in related_article_uids]

    print("Related articles: ")
    for article in related_articles:
        print(article)
    
    text_src = ""
    for dp in related_articles:
        if dp.has_file and dp.file_path.endswith(".pdf"):
            text_src += "\n" 
            text_src += getPDFText(dp.file_path, 3200, 100)
        elif dp.fm.readAbstract():
            text_src += "\n" 
            text_src += dp.fm.readAbstract()
        else:
            continue
    
    ret = asyncio.run(retrieveRelevantSections(query, src_text=text_src, n_max_return=8, min_split_words=196))

    related_sections = [r[0] for r in ret]

    print("Related sections: ")
    print(BCOLORS.OKGRAY)
    for section in related_sections:
        print(section[:100] + "...")
    print(BCOLORS.ENDC)

    return related_sections

def refineSelectedSections(question: str, related_sections: str) -> str:

    system = "You are an AI assistant that helps people find information. User will you give you a instruction. " \
    "Your task is to distill information and answer as faithfully as you can."
    history = [
        ("user", "I'm searching for the answer for a question from a literature database, you should help me pick the most relavent search result from the searched sections."), 
        ("assistant", "Sure! Please provide me with the sections you have searched so that I can assist you in selecting the most relevant ones.")
        ]
    prompt = "I'm searching for the answer for a question from a literature database, you should help me pick the most relavent search result from the searched sections.\n" \
    "For your reference, here is the question that I'm searching: {} \n".format(question) + "\n" \
    "Please help me pick at most 5 of the most relevant sections from the following searched sections: \n"\
    "---\n"\
    "\n".join(['- ' + r for r in related_sections]) + \
    "---\n"\
    "You can slightly refine each section by adding or removing some words to make it better answer the question, but you shouldn't change the meaning of the section. \n" \
    "You answer should not contain anything else other than explicitly listing the selected informations. \n"

    ai = AI(iconn)
    ai.conv_dict = {
        "system": system,
        "conversations": history
    }
    print(BCOLORS.YELLOW)
    res = ai(prompt)
    ret = ""
    for t in res:
        ret += t
    print(BCOLORS.ENDC)

    # breakpoint()
    return ret

if __name__ == "__main__":
    iconn = IServerConn()
    # MODEL: ChatStreamIterType = "stabilityai/StableBeluga-7B"
    # MODEL: ChatStreamIterType = "Open-Orca/LlongOrca-7B-16k"
    # MODEL: ChatStreamIterType = "gpt-3.5-turbo-16k"
    MODEL: ChatStreamIterType = "DEFAULT"
    # MODEL: ChatStreamIterType = "LOCAL"

    question = sys.argv[1]

    # system = "A conversation between an AI assistant and a human, "
    # "The AI is designed to answer questions in a 'Observation'->'Think'->'Action'->'Observation'->... manner. "
    # "The action can be seaching for information, or answering questions. ",
    # "The AI will speak out his action."
    system = "You are an AI assistant that helps people find information. "\
        "User will give you questions. Your task is to answer as faithfully as you can. " \
        "While answering think step-bystep and justify your answer."

    main_conv_dict = {
        "system": system,
        "conversations": []
    }
    ai = AI(iconn)
    ai.conv_dict = main_conv_dict
    raw_ans = ai(
                "You are asked a question, you don't have to answer it directly. " \
                "Instead, you should tell me what is your observation and what you are thinking about this question. " \
                "Then provide your action, your action can only be seaching for information, or answering questions. \n" \
                "- Please use search when necessary. And answer the question if you think you've gathered enough information "\
                    # "or if you think you already know the answer. \n" \
                "- If you choose to search, I will provide you with the search results, you cannot search by yourself. \n" \
                "- Our conversation may continue for several rounds, but please try to give out your answer within 3 time search. \n" \
                "- DON'T SEARCH FOR REPETITIVE INFORMATION. \n" \
                "---\n"+
                "Here is my question: {}".format(question),
    )


    print(raw_ans)
    print("------ Conversations ------")
    action = extractAction(raw_ans)

    counter = 0
    while (True):
        counter += 1
        try:
            # action_json = json.loads(action)
            action_dict = eval(action)
            assert isinstance(action_dict, dict)
            assert "action" in action_dict
            assert "action_input" in action_dict

        except Exception as e:
            print("\nFailed to parse the action into json format.")
            print("Get the following action: {}".format(action))
            print(e)
            exit(1)

        if action_dict["action"] == "search":
            se = searchForInfo(action_dict["action_input"])
            ref_se = refineSelectedSections(action_dict["action_input"], se)
            input_str = \
                "Here are some related sections from research articles: \n" + ref_se + "\n"\
                "You can take them as a referece, and not necessarily to use them. \n" + \
                "Please tell me what you are going to do next. \n" + \
                "This is our {} round of conversation. Try to give out your answer within 3 rounds. \n".format(counter) +\
                "(Don't search for repetitive information.)\n"
            if counter > 3:
                input_str = "Here are some related sections from research articles: \n" + "\n".join(se) + "\n"\
                    "You've searched for more than 3 times. Please answer the question directly. \n"
            raw_ans = ai(input_str)
            action = extractAction(raw_ans)

        elif action_dict["action"] == "answer":
            print(BCOLORS.CYAN)
            print("\n------------------------------\n")
            print("Answer: {}".format(action_dict["action_input"]))
            exit(0)

        else:
            print("Unknown action: {}".format(action_dict["action"]))
            exit(1)
