SELECT
    d.document_id,
    d.case_id,
    c.a_number,
    c.receipt_number
FROM
    document d
INNER JOIN
    (SELECT
        document_id,
        case_id
    FROM
        document
    GROUP BY
        document_id
    HAVING
        COUNT(DISTINCT case_id) = 1) AS filtered_docs ON d.document_id = filtered_docs.document_id
INNER JOIN
    case c ON d.case_id = c.case_id;
