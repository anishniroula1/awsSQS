# Fetch all schemas from the remote database
def get_schemas():
    fetch_schemas_command = (
        f"PGPASSWORD={os.environ.get('PASSWORD_DT')} psql -h {os.environ.get('DB_HOST')} "
        f"-p 5432 -U {os.environ.get('DB_USER')} -d postgres -c \"SELECT schema_name FROM information_schema.schemata "
        f"WHERE schema_name NOT IN ('pg_catalog', 'information_schema');\" -t"
    )
    process = subprocess.Popen(fetch_schemas_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error fetching schemas: {stderr.decode('utf-8')}")
        return []
    return [schema.strip() for schema in stdout.decode('utf-8').splitlines() if schema.strip()]

# Create schemas in the local database
def create_schemas(schemas):
    for schema in schemas:
        create_schema_command = (
            f"PGPASSWORD=postgres psql -h localhost -p 5434 -U postgres -d postgres -c 'CREATE SCHEMA IF NOT EXISTS {schema};'"
        )
        run_command(create_schema_command)



# Drop all existing schemas to clean the local database
drop_all_command = (
    f"PGPASSWORD=postgres psql -h localhost -p 5434 -U postgres -d postgres -c \"DO $$ DECLARE schema_name TEXT; "
    f"BEGIN FOR schema_name IN SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema') LOOP "
    f"EXECUTE 'DROP SCHEMA IF EXISTS ' || schema_name || ' CASCADE'; END LOOP; END $$;\""
)
run_command(drop_all_command)

# Fetch schemas from the remote database
schemas = get_schemas()
print("Schemas to be created:", schemas)

# Create schemas in the local database
create_schemas(schemas)