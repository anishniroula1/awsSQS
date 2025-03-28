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


Updating JSONB fields in a PostgreSQL table containing approximately 200 million records presents performance and scalability challenges, primarily due to the overhead associated with in-place updates and row-level rewrites. Attempting updates using traditional ORM methods or row-by-row processing is highly inefficient at this scale and leads to significant database bloat and slower performance.

The optimal approach involves creating and populating a new table that incorporates all required JSONB modifications in a single bulk insert operation. This strategy leverages PostgreSQL's efficiency in performing sequential writes rather than scattered row-level updates, significantly reducing operation time and avoiding table bloat. Once the new table is fully prepared with updated JSONB data and appropriate indexes are created, the tables can be swapped during a brief maintenance window. This approach ensures minimal downtime, better performance, and results in a compact, optimized table.