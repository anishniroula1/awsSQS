def update_a_number_in_matches_orm(db: Session, old_a_number: int, new_a_number: int) -> int:
    """Update a_number in matches using SQLAlchemy with optimized query"""
    # First get the list of global_ids that need updating
    find_global_ids_query = text("""
    WITH match_elements AS (
        SELECT jsonb_array_elements(matches::jsonb) as match, global_id
        FROM sentences
        WHERE a_number = :a_number
    ),
    global_id_matches AS (
        SELECT (match ->> 'global_id')::bigint as global_id
        FROM match_elements
    )
    SELECT global_id 
    FROM global_id_matches
    """)
    
    # Get all global_ids to update
    result = db.execute(find_global_ids_query, {
        'a_number': old_a_number
    })
    
    global_ids = [row[0] for row in result]
    
    if not global_ids:
        return 0
    
    total_updated = 0
    batch_size = 1000
    
    # Process in batches of 1000
    for i in range(0, len(global_ids), batch_size):
        batch_global_ids = global_ids[i:i + batch_size]
        
        # Find records using ORM
        records = db.query(models.Sentence).filter(
            models.Sentence.global_id.in_(batch_global_ids)
        ).all()
        
        # Update each record
        for record in records:
            updated_matches = []
            for match in record.matches:
                if match.get('a_number') == old_a_number:
                    match['a_number'] = new_a_number
                updated_matches.append(match)
            
            record.matches = updated_matches
            record.count = len(updated_matches)
        
        # Commit the batch
        db.commit()
        total_updated += len(records)
        print(f"Updated batch of {len(records)} records. Total updated: {total_updated}")
    
    return total_updated