
import os
os.environ["FASTCHAT_SERVER"] = "http://localhost:8000/v1"
from iRBM.lmInterface import streamOutput,getStreamIter

text = ""
print("generating....")

ai = getStreamIter("fs-vicuna-13b-v1.1")
streamOutput(ai("Write a story about a robot that is trying to take over the world in around 100 words."))
streamOutput(ai("Summarize the story in 50 words"))

print("------ Conversations ------")
print(str(ai.conversations))