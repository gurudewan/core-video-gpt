import json
from langchain.docstore.document import Document


class DocumentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Document):
            return {
                "page_content": obj.page_content,
                "metadata": obj.metadata,
                # include other attributes as needed...
            }
        return super().default(obj)
