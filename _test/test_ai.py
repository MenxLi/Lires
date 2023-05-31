from iRBM.LMInterface import OpenAIStreamIter


text = ""
print("generating....")

ai = OpenAIStreamIter()
for _ in ai("Write a story about a robot that is trying to take over the world in around 100 words."):
    ...
for _ in ai("Summarize the story in 50 words"):
    ...

print(str(ai.conversations))