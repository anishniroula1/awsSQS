from sqlalchemy import create_engine, text

# Connect to your DB
engine = create_engine("postgresql://user:password@localhost:5432/your_db_name")

old_id = 123456
new_id = 789999

update_sql = """
UPDATE your_table
SET matches = jsonb_agg(
    CASE
        WHEN (elem->>'global_id')::int = :old_id
        THEN jsonb_set(elem, '{global_id}', to_jsonb(CAST(:new_id AS int)))
        ELSE elem
    END
)
FROM (
    SELECT id, jsonb_array_elements(matches) AS elem
    FROM your_table
) AS expanded
WHERE your_table.id = expanded.id
  AND (elem->>'global_id')::int = :old_id;
"""

with engine.begin() as conn:
    result = conn.execute(text(update_sql), {"old_id": old_id, "new_id": new_id})
