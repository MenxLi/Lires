from ilires.lmInterface import HFChatStreamIter
from basaran.model import load_model

# pip install sentencepiece protobuf accelerate bitsandbytes basaran

# model = load_model("lmsys/longchat-7b-16k")
# model = load_model("lmsys/vicuna-7b-v1.5-16k", load_in_8bit=True)
# for choice in model("once upon a time", max_tokens=512):
#     # print(choice)
#     print(choice["text"], end="", flush=True)

# si = HFChatStreamIter("lmsys/vicuna-7b-v1.5-16k")
si = HFChatStreamIter("stabilityai/StableBeluga-7B")
for choice in si.call("Tell me a story of about 100 words", 0.7):
    print(choice["text"], end="", flush=True)

print("\n")
print(si.getConv())