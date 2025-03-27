from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:password@localhost:5432/yourdb")
Session = sessionmaker(bind=engine)
session = Session()

old_class_id = 1
new_class_id = 89

# Raw SQL to update JSON fields inside class_metadata
query = text("""
    UPDATE students
    SET class_metadata = jsonb_agg(
        jsonb_set(elem, '{class_id}', to_jsonb(:new_class_id)::jsonb)
    )
    FROM (
        SELECT id, jsonb_array_elements(class_metadata) AS elem
        FROM students
    ) sub
    WHERE students.id = sub.id
    AND (elem->>'class_id')::int = :old_class_id
""")

session.execute(query, {"old_class_id": old_class_id, "new_class_id": new_class_id})
session.commit()
