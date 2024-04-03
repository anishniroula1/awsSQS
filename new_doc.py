from typing import List, Dict

class Document:
    # Assuming Document class structure
    def __init__(self, section_name, content):
        self.section_name = section_name
        self.content = content
        self.is_current = True

def is_document_to_update(exist_doc, content) -> bool:
    """Check if the existing document needs to be updated."""
    return exist_doc.section_name.lower() == DefaultValues.AFFIDAVIT.value or (
        content.sectionName == exist_doc.section_name and content.content != exist_doc.content
    )

def should_add_as_new_document(content, existing_section_names) -> bool:
    """Check if the content should be added as a new document."""
    return content.sectionName not in existing_section_names

def update_existing_documents(existing_documents: List[Document], content_list: List) -> List[Dict]:
    """Identify existing documents to update."""
    documents_to_update = [
        {**doc.__dict__, "is_current": False}
        for doc in existing_documents
        for content in content_list
        if is_document_to_update(doc, content)
    ]
    return documents_to_update

def find_new_documents(existing_documents: List[Document], content_list: List, existing_section_names: List) -> List:
    """Identify new documents to add."""
    new_documents = [
        content
        for content in content_list
        if any(is_document_to_update(doc, content) for doc in existing_documents) or
           should_add_as_new_document(content, existing_section_names)
    ]
    return new_documents

def get_list_of_new_and_existing_documents(
    existing_documents: List[Document] = [],
    content_list: List = [],
    existing_section_names: List = [],
) -> (List[Dict], List):
    """Refactored function to get list of new and existing documents with reduced complexity."""
    if not existing_documents:
        return [], content_list
    
    exist_documents_to_update = update_existing_documents(existing_documents, content_list)
    new_documents = find_new_documents(existing_documents, content_list, existing_section_names)
    
    return exist_documents_to_update, new_documents
