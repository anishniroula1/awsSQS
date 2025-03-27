from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://user:password@localhost:5432/yourdb")  # Update with your real DB URI
Session = sessionmaker(bind=engine)
session = Session()

old_a_number = 1
new_a_number = 89

query = text("""
WITH updated_matches AS (
    SELECT
        m.global_id,
        jsonb_agg(
            CASE
                WHEN (elem->>'a_number')::int = :old_a_number
                THEN jsonb_set(elem, '{a_number}', to_jsonb(:new_a_number)::jsonb)
                ELSE elem
            END
        ) AS new_matches
    FROM tsp.matches m,
         LATERAL jsonb_array_elements(m.matches) AS elem
    WHERE jsonb_typeof(m.matches) = 'array'
    GROUP BY m.global_id
)
UPDATE tsp.matches
SET matches = u.new_matches
FROM updated_matches u
WHERE tsp.matches.global_id = u.global_id;
""")

session.execute(query, {"old_a_number": old_a_number, "new_a_number": new_a_number})
session.commit()
