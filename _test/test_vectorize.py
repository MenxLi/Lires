
# random text
import random, string, asyncio
from iRBM.lmTools import featurize, vectorize

def random_text(words: int):
    def random_word():
        return "".join([random.choice(string.ascii_letters) for _ in range(random.randint(1, 10))])
    
    return " ".join([random_word() for _ in range(words)])



text = random_text(1000)

vec = asyncio.run(vectorize(text, model_name="allenai/longformer-base-4096"))
print(vec.shape)


