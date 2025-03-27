from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:password@localhost:5432/yourdb")
Session = sessionmaker(bind=engine)
session = Session()

old_a_number = 1
new_a_number = 89

query = text("""
WITH updated_matches AS (
    SELECT
        s.global_id,
        jsonb_agg(
            CASE
                WHEN (elem->>'a_number')::int = :old_a_number
                THEN jsonb_set(elem, '{a_number}', to_jsonb(:new_a_number)::jsonb)
                ELSE elem
            END
        ) AS new_matches
    FROM students s,
         jsonb_array_elements(s.matches) AS elem
    GROUP BY s.global_id
)
UPDATE students
SET matches = u.new_matches
FROM updated_matches u
WHERE students.global_id = u.global_id;
""")

session.execute(query, {"old_a_number": old_a_number, "new_a_number": new_a_number})
session.commit()
