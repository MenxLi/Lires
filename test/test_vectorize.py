
# random text
import random, string, asyncio
from lires_ai.lmTools import vectorize, featurize, EncoderT

def random_text(words: int):
    def random_word():
        return "".join([random.choice(string.ascii_letters) for _ in range(random.randint(1, 10))])
    
    return " ".join([random_word() for _ in range(words)])


import sys
text = random_text(int(sys.argv[1]))

model_name: EncoderT = "sentence-transformers/all-mpnet-base-v2"

vec = asyncio.run(vectorize(text, model_name=model_name, verbose=True))
print(vec.shape)

feat = asyncio.run(featurize(text, model_name=model_name, verbose=True))
print(feat.shape)

feat2 = asyncio.run(featurize(text, model_name=model_name, verbose=True, dim_reduce=True))
print(feat2.shape)


