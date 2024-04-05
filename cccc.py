SELECT 
    c.case_id, 
    c.a_number, 
    c.receipt_number,
    d.document_category
FROM 
    Case c
INNER JOIN 
    Document d ON c.case_id = d.case_id
INNER JOIN (
    SELECT 
        case_id
    FROM 
        Document
    GROUP BY 
        case_id
    HAVING 
        COUNT(*) = 1
) unique_cases ON d.case_id = unique_cases.case_id