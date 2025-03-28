def update_a_number_in_matches_batch(db: Session, old_a_number: int, new_a_number: int, batch_size: int = 10000) -> int:
    total_updated = 0
    while True:
        query = text("""
            WITH updated AS (
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
                AND global_id IN (
                    SELECT global_id 
                    FROM sentences 
                    WHERE EXISTS (
                        SELECT 1
                        FROM jsonb_array_elements(matches::jsonb) AS match
                        WHERE (match->>'a_number')::integer = :old_a_number
                    )
                    LIMIT :batch_size
                )
                RETURNING global_id
            )
            SELECT COUNT(*) FROM updated
        """)
        
        result = db.execute(query, {
            "old_a_number": old_a_number,
            "new_a_number": new_a_number,
            "batch_size": batch_size
        })
        
        batch_count = result.scalar()
        total_updated += batch_count
        db.commit()
        
        if batch_count == 0:
            break
            
        print(f"Updated batch of {batch_count} records. Total updated: {total_updated}")
    
    return total_updated