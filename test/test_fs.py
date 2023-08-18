
import ilires.globalConfig as config
import openai
openai.api_key = "EMPTY"
config.fastchat_api_base = "http://localhost:16862/v1"
from ilires.lmInterface import streamOutput,getStreamIter

text = ""
print("generating....")

ai = getStreamIter("vicuna-33b-v1.3-gptq-4bit")
streamOutput(ai("Write a story about a robot that is trying to take over the world in around 100 words."), print_callback=print)
streamOutput(ai("Summarize the story in 50 words"), print_callback=print)

print("------ Conversations ------")
print(str(ai.conversations))
