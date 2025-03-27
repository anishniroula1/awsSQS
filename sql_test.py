from sqlalchemy import text
import json

class MatchUpdater:
    def __init__(self, session):
        self._session = session

    def update_a_number(self, old_a_number: int, new_a_number: int):
        # Step 1: Select rows with a_number == old_a_number inside matches array
        select_query = text("""
            SELECT global_id, matches
            FROM tsp.matches
            WHERE jsonb_typeof(matches) = 'array'
              AND EXISTS (
                SELECT 1
                FROM jsonb_array_elements(matches) AS elem
                WHERE (elem->>'a_number')::int = :old_a_number
              )
        """)

        results = self._session.execute(select_query, {"old_a_number": old_a_number}).fetchall()

        # Step 2: Modify in Python
        records_to_update = []

        for global_id, matches in results:
            updated = False
            for item in matches:
                if item.get("a_number") == old_a_number:
                    item["a_number"] = new_a_number
                    updated = True
            if updated:
                records_to_update.append({
                    "global_id": global_id,
                    "matches": json.dumps(matches)
                })

        # Step 3: Bulk update
        if records_to_update:
            self._session.bulk_update_mappings(
                type("Match", (object,), {"__tablename__": "tsp.matches"}),
                records_to_update
            )
            self._session.commit()
            print(f"✅ Updated {len(records_to_update)} rows with a_number = {old_a_number}")
        else:
            print("⚠️ No rows matched the a_number condition.")
