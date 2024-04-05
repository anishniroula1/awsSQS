SELECT c.case_id, c.a_number, c.receipt_number
FROM Case c
INNER JOIN (
    SELECT d.case_id
    FROM Document d
    GROUP BY d.case_id
    HAVING COUNT(d.document_id) = 1
) unique_cases ON c.case_id = unique_cases.case_id

