def save_case_details_and_documents(self, receipt_number: str, case_details: dict) -> bool:
    """
    Saves case details and documents in the data service database.
    Checks if the case is new or existing and processes documents accordingly.
    Args:
        receipt_number (str): The case receipt number.
        case_details (dict): The case details including documents.

    Raises:
        TAException: If an error occurs while saving case details or documents.

    Returns:
        bool: True if case details and documents are saved successfully.
    """
    try:
        # Update case details first
        case_obj = self._data_service_api.update_case_details(receipt_number, case_details)
        if not case_obj:
            raise TAException(receipt_number, Reason.API_NON200, "Failed to update case details")
        
        # Retrieve and normalize case status
        case_status = case_obj.get("case_status", "").upper()
        
        # Process documents only if case is new
        if case_status == "NEW":
            doc_records = filter_doc_list(case_details.get("documents", []), caseId=case_obj.get("case_id"))
            if not doc_records:
                raise TAException(receipt_number, Reason.NO_DOCUMENTS, "No documents to save")
            
            saved_document = self._data_service_api.save_document_records(receipt_number, doc_records)
            if not saved_document:
                raise TAException(receipt_number, Reason.API_NON200, "Failed to save document records")
            
            saved_doc_status = saved_document.get("doc_status", "").upper()
            if saved_doc_status in {"NEW", "EXIST"}:
                return True
        
        # For existing cases, just return True
        elif case_status == "EXIST":
            return True

    except TAException as e:
        # Raise TAException so that SQS message is reprocessed in such cases
        raise e
    except Exception as e:
        # Log unexpected errors
        err = f"Unexpected case status or failure when trying to save to DataService API: {e}"
        raise Exception(err)

    return False
