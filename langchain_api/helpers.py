from langchain.docstore.document import Document


def convert_to_documents(data_list, doc_type):
    documents = []

    for data in data_list:
        if "page_content" in data:
            content = data["page_content"]
            metadata = {key: data[key] for key in data if key != "page_content"}
            metadata["type"] = doc_type
            document = Document(page_content=content, metadata=metadata)
            documents.append(document)
    return documents


def convert_captions_to_documents(captions_data, video_id):
    caption_docs = []

    for item in captions_data:
        if item["caption"] is not None:
            doc = Document(
                page_content=item["caption"],
                metadata={
                    "video_id": video_id,
                    "group_id": item["group_id"],
                    "image_url": item["image_url"],
                    "periods": [list(period) for period in item["periods"]],
                    "type": "gpt-4V-captions",
                },
            )
            caption_docs.append(doc)

    return caption_docs


def convert_tags_to_document(tags, video_id):
    return Document(
        page_content=",".join(tags),
        metadata={"video_id": video_id, "type": "tags"},
    )
