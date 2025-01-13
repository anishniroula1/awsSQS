import subprocess
import os

def run_command(command):
    """Run a shell command and handle errors."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error: {stderr.decode('utf-8')}")
    else:
        print(stdout.decode('utf-8'))

def get_schemas():
    """Fetch all schemas from the remote database."""
    fetch_schemas_command = (
        f"PGPASSWORD={os.environ.get('PASSWORD_DT')} psql -h {os.environ.get('DB_HOST')} "
        f"-p 5432 -U {os.environ.get('DB_USER')} -d postgres "
        f"-c \"SELECT schema_name FROM information_schema.schemata "
        f"WHERE schema_name NOT IN ('pg_catalog', 'information_schema');\" -t"
    )
    process = subprocess.Popen(fetch_schemas_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error fetching schemas: {stderr.decode('utf-8')}")
        return []
    return [schema.strip() for schema in stdout.decode('utf-8').splitlines() if schema.strip()]

def create_schema(schema):
    """Create a single schema in the local database."""
    create_schema_command = (
        f"PGPASSWORD=postgres psql -h localhost -p 5434 -U postgres -d postgres "
        f"-c 'CREATE SCHEMA IF NOT EXISTS {schema};'"
    )
    run_command(create_schema_command)

def create_tables(schema, tables):
    """Create tables in a specific schema."""
    for table in tables:
        create_table_command = (
            f"PGPASSWORD=postgres psql -h localhost -p 5434 -U postgres -d postgres "
            f"-c 'CREATE TABLE IF NOT EXISTS {schema}.{table} (id SERIAL PRIMARY KEY);'"
        )
        run_command(create_table_command)

def process_custom_schemas(custom_schemas):
    """Handle creation of custom schemas and tables."""
    for item in custom_schemas:
        schema = item['schema']
        tables = item.get('tables', [])
        create_schema(schema)
        if tables:
            create_tables(schema, tables)

# Main function
def main(custom_schemas=None):
    # Step 1: Backup local database
    backup_command = (
        f"PGPASSWORD=postgres pg_dump -h localhost -p 5434 -U postgres -d postgres "
        f"--no-owner --format=c -f backup_localdb.dump"
    )
    run_command(backup_command)

    # Step 2: Drop all existing schemas in the local database
    drop_all_command = (
        f"PGPASSWORD=postgres psql -h localhost -p 5434 -U postgres -d postgres "
        f"-c \"DO $$ DECLARE schema_name TEXT; "
        f"BEGIN FOR schema_name IN SELECT schema_name FROM information_schema.schemata "
        f"WHERE schema_name NOT IN ('pg_catalog', 'information_schema') LOOP "
        f"EXECUTE 'DROP SCHEMA IF EXISTS ' || schema_name || ' CASCADE'; END LOOP; END $$;\""
    )
    run_command(drop_all_command)

    # Step 3: Create schemas and tables
    if custom_schemas:
        print("Processing custom schemas and tables...")
        process_custom_schemas(custom_schemas)
    else:
        print("Fetching all schemas from the remote database...")
        schemas = get_schemas()
        print("Schemas to be created:", schemas)
        for schema in schemas:
            create_schema(schema)

    # Step 4: Export data from remote database
    if custom_schemas:
        tables_to_dump = []
        for item in custom_schemas:
            schema = item['schema']
            for table in item.get('tables', []):
                tables_to_dump.append(f"-t {schema}.{table}")
        table_dump_flags = " ".join(tables_to_dump)
        dump_command = (
            f"PGPASSWORD={os.environ.get('PASSWORD_DT')} pg_dump -h {os.environ.get('DB_HOST')} "
            f"-p 5432 -U {os.environ.get('DB_USER')} -d postgres "
            f"{table_dump_flags} --no-owner --format=c -f ds_dt_data.dump"
        )
    else:
        dump_command = (
            f"PGPASSWORD={os.environ.get('PASSWORD_DT')} pg_dump -h {os.environ.get('DB_HOST')} "
            f"-p 5432 -U {os.environ.get('DB_USER')} -d postgres "
            f"--no-owner --format=c -f ds_dt_data.dump"
        )
    run_command(dump_command)

    # Step 5: Restore the exported dump into the local database
    restore_command = (
        f"PGPASSWORD=postgres pg_restore -h localhost -p 5434 -U postgres -d postgres "
        f"--no-owner --clean --if-exists ds_dt_data.dump"
    )
    run_command(restore_command)

# Example usage
if __name__ == "__main__":
    # Example custom schemas and tables
    custom_schemas_and_tables = [
        {"schema": "schema1", "tables": ["table1", "table2"]},
        {"schema": "schema2", "tables": ["table3"]},
    ]
    # Pass None for all schemas and tables
    main(custom_schemas=custom_schemas_and_tables)
