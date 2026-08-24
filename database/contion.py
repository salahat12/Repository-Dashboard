import os
import psycopg2

connection = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password=os.getenv("PG_PASSWORD", "Sama@9875123"),
    port="5432",
)

cur = connection.cursor()

# execute() needs the actual SQL text, not the filename string
with open("database/schema.sql", "r", encoding="utf-8") as f:    schema_sql = f.read()

cur.execute(schema_sql)

connection.commit()

cur.close()
connection.close()

print("Schema created successfully.")