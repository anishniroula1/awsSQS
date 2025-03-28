def update_a_number_in_matches(db: Session, old_a_number: int, new_a_number: int) -> int:
    query = text("""
        UPDATE sentences
        SET matches = (
            SELECT jsonb_agg(
                CASE 
                    WHEN (match->>'a_number')::integer = :old_a_number
                    THEN jsonb_set(match, '{a_number}', to_jsonb(cast(:new_a_number as text)))
                    ELSE match
                END
            )
            FROM jsonb_array_elements(matches::jsonb) AS match
        )
        WHERE EXISTS (
            SELECT 1
            FROM jsonb_array_elements(matches::jsonb) AS match
            WHERE (match->>'a_number')::integer = :old_a_number
        )
    """)
    result = db.execute(query, {
        "old_a_number": old_a_number,
        "new_a_number": new_a_number
    })
    db.commit()
    return result.rowcount