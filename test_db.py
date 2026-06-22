import psycopg2

try:
    # These are the universal default settings for a local Postgres install
    connection = psycopg2.connect(
        user="postgres",
        password="Saiko@8586",  # <-- Put your actual install password here
        host="127.0.0.1",
        port="5432",
        database="postgres"
    )
    
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    
    print(f"🟢 SUCCESS! Connected to Native Database:")
    print(f"Version Info: {db_version[0]}")
    
    cursor.close()
    connection.close()

except Exception as error:
    print(f"🔴 CONNECTION FAILED: {error}")
    print("Check your password, or check if the PostgreSQL service is actually running in your OS background.")