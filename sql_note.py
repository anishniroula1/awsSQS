SELECT * FROM sentences 
WHERE EXISTS (
    SELECT 1 
    FROM jsonb_array_elements(matches::jsonb) AS match 
    WHERE (match->>'a_number')::integer = 94
);

