def update_a_number_in_matches_orm(db: Session, old_a_number: int, new_a_number: int, batch_size: int = 1000) -> int:
    """Update a_number in matches using SQLAlchemy bulk update mapping"""
    total_updated = 0
    
    while True:
        # Get batch of sentences that need updating
        sentences = db.query(models.Sentence).filter(
            models.Sentence.matches.cast(models.Sentence.matches.type).op('?|')([f'[{{"a_number": {old_a_number}}}]'])
        ).limit(batch_size).all()
        
        if not sentences:
            break
            
        # Prepare bulk update data using list comprehension for better performance
        update_data = [
            {
                'global_id': sentence.global_id,
                'matches': [
                    {**match, 'a_number': new_a_number} if match['a_number'] == old_a_number else match
                    for match in sentence.matches
                ]
            }
            for sentence in sentences
        ]
        
        # Perform bulk update
        if update_data:
            db.bulk_update_mappings(
                models.Sentence,
                update_data
            )
            db.commit()
            
            total_updated += len(update_data)
            print(f"Updated batch of {len(update_data)} records. Total updated: {total_updated}")
    
    return total_updated