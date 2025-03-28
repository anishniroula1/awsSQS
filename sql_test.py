def update_a_number_in_matches_orm(db: Session, old_a_number: int, new_a_number: int, batch_size: int = 1000) -> int:
    """Update a_number in matches using pure SQLAlchemy ORM"""
    total_updated = 0

    while True:
        # Get batch of sentences that need updating using ORM
        sentences = db.query(models.Sentence).filter(
            models.Sentence.matches.cast(JSONB).op('@>')(
                json.dumps([{"a_number": old_a_number}])
            )
        ).limit(batch_size).all()


        if not sentences:
            break

        update_mappings = []
        for sentence in sentences:
            updated = False
            for match in sentence.matches:
                if match['a_number'] == old_a_number:
                    match['a_number'] = new_a_number
                    updated = True

            if updated:
                update_mappings.append({
                    'global_id': sentence.global_id,
                    'matches': sentence.matches
                })

        if update_mappings:
            db.bulk_update_mappings(models.Sentence, update_mappings)
            db.commit()

        batch_updated = len(update_mappings)
        total_updated += batch_updated
        print(f"Updated batch of {batch_updated} records. Total updated: {total_updated}")