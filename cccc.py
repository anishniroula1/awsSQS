SELECT 
    c.case_id, 
    c.a_number, 
    c.receipt_number,
    d.document_category
FROM Case c
INNER JOIN (
    SELECT 
        case_id,
        document_category
    FROM Document
    GROUP BY case_id, document_category
    HAVING COUNT(document_id) = 1
) d ON c.case_id = d.case_id
