def update_a_number_in_matches_orm(db: Session, old_a_number: int, new_a_number: int, batch_size: int = 1000) -> int:
    """Update a_number in matches using pure SQLAlchemy ORM"""
    total_updated = 0
    
    # Get all sentences that need updating
    sentences = db.query(models.Sentence).filter(
        models.Sentence.matches.cast(models.Sentence.matches.type).op('?|')([f'[{{"a_number": {old_a_number}}}]'])
    ).all()
    
    print(f"Found {len(sentences)} records to update")
    
    # Process in batches
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        
        for sentence in batch:
            # Update matches in memory
            updated_matches = []
            for match in sentence.matches:
                if match['a_number'] == old_a_number:
                    match['a_number'] = new_a_number
                updated_matches.append(match)
            
            # Update the sentence
            sentence.matches = updated_matches
        
        # Commit the batch
        db.commit()
        total_updated += len(batch)
        print(f"Updated batch of {len(batch)} records. Total updated: {total_updated}")
    
    return total_updated