
import os
os.environ["FASTCHAT_SERVER"] = "http://localhost:8000/v1"
from iRBM.lmInterface import streamOutput,getStreamIter

text = ""
print("generating....")

ai = getStreamIter("vicuna-13b")
streamOutput(ai("Write a story about a robot that is trying to take over the world in around 100 words."), print_callback=print)
streamOutput(ai("Summarize the story in 50 words"), print_callback=print)

print("------ Conversations ------")
print(str(ai.conversations))
