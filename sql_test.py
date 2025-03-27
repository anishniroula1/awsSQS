from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# Setup DB connection (update with your actual credentials)
engine = create_engine("postgresql://user:password@localhost:5432/yourdb")
Session = sessionmaker(bind=engine)
session = Session()

# Parameters
old_a_number = 1
new_a_number = 89

# Step 1: Select only rows where matches is an array AND has a_number key
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

results = session.execute(select_query).fetchall()

# Step 2: Check and modify a_number in Python
records_to_update = []

for global_id, matches in results:
    updated = False
    for item in matches:
        if item.get("a_number") == old_a_number:
            item["a_number"] = new_a_number
            updated = True
    if updated:
        records_to_update.append((global_id, matches))

# Step 3: Update modified rows in the DB
update_query = text("""
    UPDATE tsp.matches
    SET matches = :matches
    WHERE global_id = :global_id
""")

for global_id, updated_matches in records_to_update:
    session.execute(update_query, {
        "global_id": global_id,
        "matches": json.dumps(updated_matches)
    })

session.commit()
print(f"✅ Updated {len(records_to_update)} rows where a_number = {old_a_number}")
