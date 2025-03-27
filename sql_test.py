from sqlalchemy import text

sql_script = text("""
UPDATE x.table
SET matchers = (
    SELECT jsonb_agg(
        CASE
            WHEN (matcher ->> 'global_id')::int = :old_global_id THEN
                jsonb_set(matcher, '{global_id}', to_jsonb(:new_global_id))
            ELSE matcher
        END
    )
    FROM jsonb_array_elements(matchers) AS matcher
)
WHERE matchers @> :json_query
""")

# Parameters
old_global_id = 123  # Replace with your old global_id
new_global_id = 456  # Replace with your new global_id

# This ensures you only update rows actually containing the old_global_id
json_query = f'[{{"global_id": {old_global_id}}}]'

# Execute query
session.execute(sql_script, {
    'old_global_id': old_global_id,
    'new_global_id': new_global_id,
    'json_query': json_query
})
session.commit()
