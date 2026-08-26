import os

import psycopg2


def get_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password=os.getenv("PG_PASSWORD"),
        port="5432",
    )
