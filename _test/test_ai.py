from iRBM.lmInterface import OpenAIStreamIter, streamOutput


text = ""
print("generating....")

ai = OpenAIStreamIter()
streamOutput(ai("Write a story about a robot that is trying to take over the world in around 100 words."))
streamOutput(ai("Summarize the story in 50 words"))

print("------ Conversations ------")
print(str(ai.conversations))