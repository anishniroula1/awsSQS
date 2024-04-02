WITH filtered_sections AS (
    SELECT
        s.a_number,
        CASE
            WHEN tsi.section_name = 'supp_b' OR tsi.section_name LIKE 'supp_b_%' THEN s.match_count
            ELSE NULL
        END AS match_count_supplement_b
    FROM
        Sentences s
    JOIN Text_Similarity_Input tsi ON s.tsp_id = tsi.tsp_id
    WHERE
        s.match_count != 0
        AND tsi.is_current = TRUE
        AND tsi.analysis_group = 'ABC'
)
SELECT
    a_number,
    COUNT(match_count_supplement_b) AS match_count_supplement_b
FROM
    filtered_sections
GROUP BY
    a_number;

def filter_sections_like(patterns):
    # Handles pattern matching
    conditions = [Text_Similarity_Input.section_name.like(pattern) for pattern in patterns]
    return case([
        (or_(*conditions), Sentences.match_count)
    ], else_=0)
