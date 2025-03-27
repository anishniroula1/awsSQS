from sqlalchemy import text

sql_script = text("""
WITH updated AS (
    SELECT
        id, -- replace with your actual primary key column
        jsonb_agg(
            CASE
                WHEN (matcher ->> 'global_id')::int = :old_global_id THEN
                    jsonb_set(matcher, '{global_id}', to_jsonb(:new_global_id))
                ELSE matcher
            END
        ) AS new_matchers
    FROM x.table, jsonb_array_elements(matchers) AS matcher
    GROUP BY id -- replace with your actual primary key column
)
UPDATE x.table AS orig
SET matchers = updated.new_matchers
FROM updated
WHERE orig.id = updated.id
AND orig.matchers @> :json_query
""")

# Parameters
old_global_id = 123
new_global_id = 456
json_query = f'[{{"global_id": {old_global_id}}}]'

session.execute(sql_script, {
    'old_global_id': old_global_id,
    'new_global_id': new_global_id,
    'json_query': json_query
})
session.commit()
