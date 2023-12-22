from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class DBConnection:
    def __init__(self, db_url):
        # Create the engine
        self.engine = create_engine(db_url)

        # Create a configured "Session" class
        Session = sessionmaker(bind=self.engine)

        # Create a session
        self.session = Session()

        # Connect to the database
        self.connection = self.engine.connect()

        # Create a cursor object
        self.cursor = self.connection.connection.cursor()

    def insert_single_record(self, record: dict, table, return_result: bool = False):
        """
        Insert a single record into the given table and optionally return the result.

        :param record: Record to insert (as a dictionary).
        :param table: SQLAlchemy Table object where the record will be inserted.
        :param return_result: If True, return the inserted record.
        :return: The inserted record if return_result is True, else None.
        """
        try:
            obj = table(**record)
            self.session.add(obj)
            self.session.commit()

            if return_result:
                return self.session.query(table).get(obj.id)
        except Exception as e:
            self.session.rollback()
            raise e

    def bulk_insert_records(self, records: list, table, return_result: bool = False):
        """
        Bulk insert records into the given table.

        :param records: List of records to insert.
        :param table: SQLAlchemy Table object where records will be inserted.
        :param return_result: If True, return the result of the bulk insert.
        :return: Result of the insert operation if return_result is True, else None.
        """
        try:
            self.session.bulk_insert_mappings(table, records, return_defaults=return_result)
            self.session.commit()
            if return_result:
                return records
        except Exception as e:
            self.session.rollback()
            raise e

    def bulk_update_records(self, records: list, table, return_result: bool = False):
        """
        Bulk update records in the given table.

        :param records: List of records to update.
        :param table: SQLAlchemy Table object where records will be updated.
        :param return_result: If True, return the result of the bulk update.
        :return: Result of the update operation if return_result is True, else None.
        """
        try:
            self.session.bulk_update_mappings(table, records)
            self.session.commit()
            if return_result:
                return self.session.query(table).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def update_columns_record(self, columns: list, table, record: dict):
        """
        Update specific columns of a record in a table.

        :param columns: List of column names to update.
        :param table: SQLAlchemy Table object where records will be updated.
        :param record: Dictionary representing the record to update.
        """
        try:
            # Extract primary key and its value from the record
            primary_key = inspect(table).primary_key[0].name
            primary_key_value = record.pop(primary_key, None)

            if primary_key_value is None:
                raise ValueError("Primary key value is required for an update.")

            # Filter the record dictionary to include only the specified columns
            update_dict = {key: record[key] for key in columns if key in record}

            # Update the record
            self.session.query(table).filter(getattr(table, primary_key) == primary_key_value).update(update_dict)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def close(self):
        # Close the session, connection, and cursor
        self.session.close()
        self.connection.close()
        self.cursor.close()

# You can then create a Base class for your models
Base = declarative_base()
