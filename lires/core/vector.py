"""
Build and query text features of each document.
AI method shoud go through IServerConn interface.
"""
from __future__ import annotations
import os, hashlib, re
import asyncio, tqdm
from typing import TypedDict, Optional, Callable, Literal, TYPE_CHECKING
from lires.core.dataClass import DataBase, DataPoint
from lires.core.pdfTools import getPDFText
from lires.vector.database import VectorDatabase, VectorCollection, VectorEntry
if TYPE_CHECKING:
    from lires.api import IServerConn

async def createSummaryWithLLM(iconn: IServerConn, text: str, verbose: bool = False) -> str:
    summary = ""
    res = iconn.chat(
        conv_dict={
            "system": "A conversation between a human and an AI research assistant. "\
                "The AI gives short and conscise response in academic literature style. ",
            "conversations": []
        },
        prompt = "Summarize the following paper in about 100 words, "\
            "your summary should focus on the motivation and contribution. "\
            "Don't mention title."
            f"Here is the paper: {text}",
        model_name = "DEFAULT"
    )
    async for t in res:
        summary += t
        if verbose:
            print(summary)
    return summary

FeatureQueryResult = TypedDict("FeatureQueryResult", {"uids": list[str], "scores": list[float]})
FeatureQueryResult2 = list[TypedDict("FeatureQueryResult_", {"score": float, "entry": VectorEntry})]

FeatureTextSource = TypedDict("FeatureTextSource", {
            "text": str, 
            "hash": str,
            "type": Literal["abstract", "summary", "fulltext", "title"]},
            )
async def getOverallFeatureTextSource(
        iconn: Optional[IServerConn], 
        dp: DataPoint, 
        max_words_per_doc: Optional[int] = None, 
        print_fn: Callable[[str], None] = lambda x: None,
        )-> FeatureTextSource:
    """
    Extract text source from a document for feature extraction.
    Priority: abstract > ai summary > fulltext > title
    - iconn: IServerConn, if set to None, will not use LLM to create summary
    - dp: DataPoint
    - max_words_per_doc: int, if set to None, will not truncate the text
    - print_fn: Callable[[str], None], a function to print the progress
    """
    abstract = await dp.fm.readAbstract()
    uid = dp.uuid
    doc_summary_dir = dp.parent.path.summary_dir
    title_text: str = "Title: " + dp.title + "\n"
    if abstract:
        # if abstract is available, use it as the text source
        print_fn(f"- use abstract")
        return {
            "text": (_text := title_text + abstract),
            "hash": hashlib.md5(_text.encode()).hexdigest(),
            "type": "abstract"
        }
    elif await dp.fm.hasFile() and dp.summary.file_type == ".pdf":
        # if has pdf, try to create a summary
        pdf_path = await dp.fm.filePath(); assert pdf_path
        pdf_text = await getPDFText(pdf_path, max_words_per_doc)

        _summary_cache_path = os.path.join(doc_summary_dir, uid + ".txt")
        if os.path.exists(_summary_cache_path):
            # check if summary is already created
            summary = open(_summary_cache_path, "r").read()
            print_fn(f"- use cached summary")
        else:
            if iconn:
                # if LLM is available, use it to create summary
                summary = await createSummaryWithLLM(iconn, pdf_text)
                with open(_summary_cache_path, "w") as f:
                    f.write(summary)
                if summary:
                    print_fn(f"- use LLM summary")
            else:
                summary = ""

        if summary:
            # if summary is created, use it as the text source
            return {
                "text": (_text := title_text + summary),
                "hash": hashlib.md5(_text.encode()).hexdigest(),
                "type": "summary"
            }
        else:
            # otherwise, use the full text
            print_fn(f"- use full text")
            return {
                "text": (_text := pdf_text),
                "hash": hashlib.md5(_text.encode()).hexdigest(),
                "type": "fulltext"
            }
    else:
        # otherwise, use title
        print_fn(f"- use title")
        return {
            "text": (_text := title_text.strip()),
            "hash": hashlib.md5(_text.encode()).hexdigest(),
            "type": "title"
        }

async def updateFeture(
    vector_db: VectorDatabase, 
    iconn: IServerConn, 
    dp: DataPoint,
    max_words_per_doc: int = 2048
    ):
    async def _updateDocFeature():
        vector_collection = await vector_db.getCollection("doc_feature")
        _ret = await getOverallFeatureTextSource(None, dp, max_words_per_doc)
        new_content = f'{_ret["type"]}:{_ret["hash"]}'
        uid = dp.uuid
        try:
            entry = await vector_collection.get(uid)
            if entry["content"] != new_content:
                await vector_collection.update({
                    "uid": uid,
                    "group": uid,
                    "vector": await iconn.featurize(_ret["text"]),
                    "content": new_content
                })
        except vector_collection.Error.LiresEntryNotFoundError:
            await vector_collection.insert({
                "uid": uid,
                "group": uid,
                "vector": await iconn.featurize(_ret["text"]),
                "content": new_content
            })
    async with asyncio.Lock():
        # in case of rapid update, 
        # which may case the un-ordered try-catch block to fail
        await _updateDocFeature()

async def deleteFeature(
        vector_db: VectorDatabase, 
        dp: DataPoint,
        ) -> None:
    vector_collection = await vector_db.getCollection("doc_feature")
    await vector_collection.deleteGroup(dp.uuid)

async def buildFeatureStorage(
        iconn: IServerConn,
        db: DataBase, 
        vector_db: VectorDatabase,
        max_words_per_doc: int = 2048, 
        force = False,
        operation_interval: float = 0.,
        ):
    """
    - operation_interval: float, the interval between two operations, in seconds, 
        set this to a positive value to avoid blocking the main event loop
    """
    vector_collection = await vector_db.getCollection("doc_feature")

    # check if ai server is running
    assert iconn.status is not None, "iServer is not running, please connect to the AI server fist"

    if force:
        await vector_collection.clearAll()
    
    # extract text source
    for dp in tqdm.tqdm(await db.getAll(), desc="Building feature storage"):
        await updateFeture(
            dp = dp,
            iconn = iconn, 
            vector_db = vector_db, 
            max_words_per_doc = max_words_per_doc
            )
        await asyncio.sleep(operation_interval)
    await vector_db.commit()

async def queryFeatureIndex(
        iconn: IServerConn,
        vector_collection: VectorCollection,
        query: str, n_return: int = 16, 
        ) -> FeatureQueryResult2:
    query_vec = await iconn.featurize(query) # [d_feature]
    assert query_vec is not None

    uids, scores = await vector_collection.search(query_vec, n_return)
    entries = await vector_collection.getMany(uids)
    return [{"score": score, "entry": entry} for score, entry in zip(scores, entries)]

async def queryFeatureIndexByUID(
    db: DataBase, 
    iconn: IServerConn,
    vector_collection: VectorCollection,
    query_uid: str, 
    n_return: int = 16
    ) -> FeatureQueryResult:
    """
    query the related documents of the given uid
    """
    raise NotImplementedError("To be modified")
    # read the document with the given uid
    pdf_path = await (dp:=await db.get(query_uid)).fm.filePath()
    if pdf_path is None:
        query_string: str = dp.title
        print("Warning: no pdf file found, use title only: {}".format(query_string))
    else:
        query_string = await getPDFText(pdf_path, 4096)
    return await queryFeatureIndex(
        iconn=iconn,
        vector_collection=vector_collection,
        query=query_string, 
        n_return=n_return
        )


async def retrieveRelevantSections(
        iconn: IServerConn,
        query_text: str, 
        src_text: str, 
        n_max_return = 5,
        min_split_words: int = 128,
        min_score = 0.2,
        verbose = False
        ) -> list[tuple[str, float]]:
    raise NotImplementedError("To be modified")
    assert iconn.status is not None, "iServer is not running, please connect to the AI server fist"

    if verbose: print("Querying relevent sections...")

    sentences = src_text.replace("\n", " ").split(". ")

    for i in range(len(sentences)):
        sentences[i] = sentences[i].strip()

        # merge the sentences if the length is too short
        if len(sentences[i].split(" ")) < min_split_words:
            if i == len(sentences) - 1:
                break
            sentences[i+1] = sentences[i] + ". " + sentences[i+1]
            sentences[i] = ""

    if verbose: print(f"Found {len(sentences)} sentences")
    sentences = [s for s in sentences if s != ""]

    # featurize the sentences
    # split the text into sections
    if verbose: print(f"Query: {query_text}")
    query_text = query_text.replace("\n", " ")
    query_vec = await iconn.featurize(query_text)

    __non_english_regex = re.compile(r'[^a-zA-Z0-9\s\.\,\;\:\!\?\-\'\"\(\)\[\]\{\}\&\%\$\#\@\!\~\`\+\=\_\\\/\*\^]+')
    def __containsNoneEnglish(sentence):
        return bool(__non_english_regex.findall(sentence))

    src_vec_dict: dict[str, list[float]] = {}
    for sentence in sentences:
        await asyncio.sleep(0)
        # TODO: replace this
        # ignore sentences with none english words
        if __containsNoneEnglish(sentence):
            continue

        sentence_feat = await iconn.featurize(sentence)
        src_vec_dict[sentence] = sentence_feat
    
    # compute the similarity
    vec_col = tiny_vectordb.VectorCollection(None, "_feature", 768)
    vec_col.addBlock(
        list(src_vec_dict.keys()), 
        list(src_vec_dict.values())
        )     # requires python > 3.7
    search_res = vec_col.search(query_vec, n_max_return)

    ret = [(sentence, score) for sentence, score in zip(search_res[0], search_res[1]) if score > min_score]
    ret.sort(key=lambda x: x[1], reverse=True) # sort by score, descending
    return ret

