from iRBM.lmInterface import OpenAIChatStreamIter, streamOutput
from iRBM import globalConfig as config


text = ""
print("generating....")

config.openai_api_base = "https://api.aiproxy.io/v1"
# config.fastchat_api_base = ""
# ai = OpenAIStreamIter(model="vicuna-13b")
ai = OpenAIChatStreamIter(model="gpt-4-32k")
streamOutput(ai("Write a story about a robot that is trying to take over the world in around 100 words."), print_callback=print)
streamOutput(ai("Summarize the story in 50 words"), print_callback=print)

print("------ Conversations ------")
print(str(ai.conversations))