from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

from langchain.docstore.document import Document

from helpers.gcs_helper import gcs
from helpers.srt_fixer import fix_subs

from langchain_api import loaders, helpers, chunker

import helpers.tokenizer as tokenizer
import filer

from pprint import pprint


def embed(video_id, info):
    subs_file_path = f"tmp/youtube/{video_id}/subs.srt"

    fix_subs(subs_file_path)

    subtitle_raw_data = loaders.load_video_subtitles(video_id)

    subtitle_sentences_raw = chunker.chunkize(subtitle_raw_data)
    subtitle_sentence_documents = helpers.convert_to_documents(
        subtitle_sentences_raw, "transcript"
    )

    caption_docs = helpers.convert_captions_to_documents(info["view"], video_id)

    title_doc = Document(
        page_content=info["title"], metadata={"video_id": video_id, "type": "title"}
    )

    transcript_summary_doc = Document(
        page_content=info["transcript_summary"],
        metadata={"video_id": video_id, "type": "summary"},
    )

    key_frames_summary = Document(
        page_content=info["key_frames_summary"],
        metadata={"video_id": video_id, "type": "summary"},
    )

    summary_doc = Document(
        page_content=info["summary"], metadata={"video_id": video_id, "type": "summary"}
    )
    description_doc = Document(
        page_content=info["description"],
        metadata={"video_id": video_id, "type": "description"},
    )

    tags_doc = helpers.convert_tags_to_document(info["tags"], video_id)

    documents = (
        [
            title_doc,
            transcript_summary_doc,
            key_frames_summary,
            summary_doc,
            description_doc,
            tags_doc,
        ]
        + subtitle_sentence_documents
        + caption_docs
    )

    filer.stream_var_into_gcs(
        documents, f"/tmp/youtube/{video_id}/all_documents_raw.json"
    )

    db = FAISS.from_documents(documents, OpenAIEmbeddings())

    faiss_index_path = f"tmp/youtube/{video_id}/faiss_index"

    db.save_local(faiss_index_path)

    return


def do_vector_search(query, video_id):
    embeddings = OpenAIEmbeddings()

    faiss_index_path = f"/tmp/youtube/{video_id}/faiss_index"

    gcs.download_folder_from_gcs(faiss_index_path, faiss_index_path)

    db = FAISS.load_local(faiss_index_path, embeddings)

    docs = db.similarity_search(query, filter=dict(video_id=video_id))

    pprint(len(docs))
    print("====================================")
    pprint([f"Token length of doc: {len(doc.page_content.split())}" for doc in docs])

    return docs


if __name__ == "__main__":
    query = "What is the key message of this video?"
    do_vector_search(query)
