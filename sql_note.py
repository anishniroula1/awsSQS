SELECT * FROM sentences 
WHERE EXISTS (
    SELECT 1 
    FROM jsonb_array_elements(matches::jsonb) AS match 
    WHERE (match->>'a_number')::integer = 94
);

UPDATE sentences
SET matches = (
    SELECT jsonb_agg(
        CASE 
            WHEN (match->>'a_number')::integer = 94
            THEN jsonb_set(match, '{a_number}', '456'::jsonb)
            ELSE match
        END
    )
    FROM jsonb_array_elements(matches::jsonb) AS match
)
WHERE EXISTS (
    SELECT 1
    FROM jsonb_array_elements(matches::jsonb) AS match
    WHERE (match->>'a_number')::integer = 94
);

SELECT global_id, matches
            FROM sentences
            WHERE EXISTS (
                SELECT 1
                FROM jsonb_array_elements(matches::jsonb) AS match
                WHERE (match->>'a_number')::integer = 2030000
            )
            LIMIT 300