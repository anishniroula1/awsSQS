class DocumentProcessor:
    def __init__(self, data_service_api, logger):
        self._data_service_api = data_service_api
        self._logger = logger

    def get_valid_documents(self, list_of_documents):
        """
        Processes a list of documents and returns a list of valid documents.

        A valid document is one that belongs to acceptable categories and does not have a delete indicator,
        or if it has a delete indicator, it is handled appropriately by checking its status via an API.

        :param list_of_documents: List of document dictionaries to process.
        :return: List of valid document dictionaries.
        """
        valid_documents = []
        
        for doc in list_of_documents:
            if self._is_acceptable_category(doc):
                if doc.get("deleteIndicator"):
                    self._handle_delete_indicator(doc, valid_documents)
                else:
                    valid_documents.append(doc)
        
        return valid_documents

    def _is_acceptable_category(self, doc):
        """
        Checks if a document belongs to an acceptable category.

        :param doc: The document dictionary to check.
        :return: True if the document is in an acceptable category, False otherwise.
        """
        document_category = doc.get("contentCategoryDescription")
        return (
            document_category in Constant.asylee_acceptable_documents or 
            document_category in Constant.lockbox_acceptable_documents
        )

    def _handle_delete_indicator(self, doc, valid_documents):
        """
        Handles a document with a delete indicator by checking its status via an API.

        If the document status is 'DELETED_DOCUMENT', it updates the document status.
        If the document does not exist (status 404), it adds the document to the valid_documents list.

        :param doc: The document dictionary to handle.
        :param valid_documents: The list of valid documents to append to, if applicable.
        """
        s3Key = doc.get("s3Key")
        try:
            response = self._data_service_api.get_document_by_content_id(s3Key)
            self._process_api_response(response, doc, valid_documents)
        except Exception as e:
            self._logger.error(f"Error processing document with contentId {s3Key}: {str(e)}")

    def _process_api_response(self, response, doc, valid_documents):
        """
        Processes the API response based on the status code and document status.

        :param response: The API response object.
        :param doc: The document dictionary associated with the API response.
        :param valid_documents: The list of valid documents to append to, if applicable.
        """
        if response.status_code == 200:
            doc_exist = response.json()
            if doc_exist["documentStatus"] == "DELETED_DOCUMENT":
                self._data_service_api.update_document(doc_exist)
                self._logger.info("Document marked as deleted")
            else:
                valid_documents.append(doc)
        elif response.status_code == 404:
            valid_documents.append(doc)
        else:
            raise Exception(f"Unexpected response from data service API: {response.status_code}")
