from sqlalchemy import create_engine, text

# Replace with your actual DB URL
engine = create_engine("postgresql://user:password@localhost:5432/your_db_name")

old_id = 123456
new_id = 789999

update_sql = """
UPDATE your_table
SET matches = (
    SELECT jsonb_agg(
        CASE
            WHEN (elem->>'global_id')::int = :old_id
            THEN jsonb_set(elem, '{global_id}', to_jsonb(:new_id::int))
            ELSE elem
        END
    )
    FROM jsonb_array_elements(matches) AS elem
)
WHERE EXISTS (
    SELECT 1
    FROM jsonb_array_elements(matches) AS elem
    WHERE (elem->>'global_id')::int = :old_id
);
"""

with engine.begin() as conn:
    conn.execute(text(update_sql), {"old_id": old_id, "new_id": new_id})
