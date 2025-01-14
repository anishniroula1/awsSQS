import subprocess
import os
import json

# Environment variables from your screenshot
PG_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PORT = os.environ.get('DATABASE_PORT')
DATABASE = os.environ.get('DATABASE')

DUMP_FILE_NAME = "tsp_db_data.dump"
LOCAL_PORT = os.environ.get('LOCAL_DATABASE_PORT')
local_backup = os.environ.get('DO_LOCAL_DB_BACKUP')
DO_LOCAL_DB_BACKUP = json.loads(local_backup.lower()) if local_backup else False


def run_command(command):
    """Run a shell command and handle errors."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error: {stderr.decode('utf-8')}")
    else:
        print(stdout.decode('utf-8'))


def backup_local_database():
    """Backup the local database."""
    if DO_LOCAL_DB_BACKUP:
        print("Backing up the local database...")
        backup_command = (
            f"PGPASSWORD=postgres pg_dump -h localhost -p {LOCAL_PORT} -U postgres -d postgres "
            f"--no-owner --format=c -f backup_localdb.dump"
        )
        run_command(backup_command)
    else:
        print("Skipping local database backup as per configuration.")


def drop_existing_schemas():
    """Drop all existing schemas in the local database."""
    print("Dropping existing schemas in the local database...")
    drop_all_command = (
        f"PGPASSWORD=postgres psql -h localhost -p {LOCAL_PORT} -U postgres -d postgres "
        f"-c \"DO $$ "
        f"DECLARE schema_name TEXT; "
        f"BEGIN "
        f"FOR schema_name IN "
        f"(SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema')) "
        f"LOOP "
        f"EXECUTE format('DROP SCHEMA IF EXISTS %I CASCADE', schema_name); "
        f"END LOOP; "
        f"END $$;\""
    )
    run_command(drop_all_command)


def dump_data_only(custom_schemas=None):
    """Export database data only, excluding functions and triggers."""
    print("Dumping data only from the remote database...")
    if custom_schemas:
        tables_to_dump = []
        for item in custom_schemas:
            schema = item['schema']
            for table in item.get('tables', []):
                tables_to_dump.append(f"-t {schema}.{table}")
        table_dump_flags = " ".join(tables_to_dump)
        dump_command = (
            f"PGPASSWORD={PG_PASSWORD} pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DATABASE} "
            f"{table_dump_flags} --no-owner --data-only -f {DUMP_FILE_NAME}"
        )
    else:
        dump_command = (
            f"PGPASSWORD={PG_PASSWORD} pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DATABASE} "
            f"--no-owner --data-only -f {DUMP_FILE_NAME}"
        )
    run_command(dump_command)


def clean_dump_file(dump_file):
    """Remove functions and triggers from the dump file."""
    print("Cleaning the dump file to remove functions and triggers...")
    clean_file = dump_file.replace(".dump", "_cleaned.dump")
    with open(dump_file, "r") as infile, open(clean_file, "w") as outfile:
        skip_line = False
        for line in infile:
            # Skip trigger and function definitions
            if "CREATE FUNCTION" in line or "CREATE TRIGGER" in line:
                skip_line = True
            if not skip_line:
                outfile.write(line)
            if line.strip() == ";":  # End of a function or trigger
                skip_line = False
    print(f"Cleaned dump file saved to {clean_file}")
    return clean_file


def restore_to_local_database(dump_file):
    """Restore the cleaned dump file to the local database."""
    print("Restoring the cleaned dump file into the local database...")
    restore_command = (
        f"PGPASSWORD=postgres psql -h localhost -p {LOCAL_PORT} -U postgres -d postgres "
        f"-f {dump_file}"
    )
    run_command(restore_command)


def create_schema(schema):
    """Create a schema in the local database."""
    print(f"Creating schema: {schema}...")
    create_schema_command = (
        f"PGPASSWORD=postgres psql -h localhost -p {LOCAL_PORT} -U postgres -d postgres "
        f"-c 'CREATE SCHEMA IF NOT EXISTS {schema};'"
    )
    run_command(create_schema_command)


def create_tables(schema, tables):
    """Create tables in a specific schema."""
    print(f"Creating tables in schema: {schema}...")
    for table in tables:
        create_table_command = (
            f"PGPASSWORD=postgres psql -h localhost -p {LOCAL_PORT} -U postgres -d postgres "
            f"-c 'CREATE TABLE IF NOT EXISTS {schema}.{table} (id SERIAL PRIMARY KEY);'"
        )
        run_command(create_table_command)


def process_custom_schemas(custom_schemas):
    """Process custom schemas and tables."""
    for item in custom_schemas:
        schema = item['schema']
        tables = item.get('tables', [])
        create_schema(schema)
        if tables:
            create_tables(schema, tables)


def main(custom_schemas=None):
    """Main workflow to handle database dump, clean, and restore."""
    print("Step 1: Backup local database...")
    backup_local_database()

    print("Step 2: Drop existing schemas in the local database...")
    drop_existing_schemas()

    print("Step 3: Dump data only from remote database (excluding functions and triggers)...")
    dump_data_only(custom_schemas=custom_schemas)

    print("Step 4: Clean the dump file to remove functions and triggers...")
    cleaned_dump_file = clean_dump_file(DUMP_FILE_NAME)

    print("Step 5: Restore the cleaned dump file into the local database...")
    restore_to_local_database(cleaned_dump_file)


if __name__ == "__main__":
    # Example custom schemas and tables
    custom_schemas_and_tables = [
        {"schema": "schema1", "tables": ["table1", "table2"]},
        {"schema": "schema2", "tables": ["table3"]},
    ]
    # Pass custom_schemas_and_tables to process specific schemas and tables, or None for all schemas
    main(custom_schemas=None)
