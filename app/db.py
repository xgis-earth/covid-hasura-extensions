from os import environ as env
import psycopg2


def get_conn():
    host = env.get("COVID_DB_HOST")
    dbname = env.get("COVID_DB_NAME")
    user = env.get("COVID_DB_USER")
    password = env.get("COVID_DB_PASS")
    return psycopg2.connect(host=host, dbname=dbname, user=user, password=password, sslmode="require")
