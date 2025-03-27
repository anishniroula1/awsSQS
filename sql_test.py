select_query = text("""
    SELECT global_id, matches
    FROM tsp.matches
    WHERE jsonb_typeof(matches) = 'array'
      AND EXISTS (
        SELECT 1
        FROM jsonb_array_elements(matches) AS elem
        WHERE elem ? 'a_number'
      )
""")