from flask import g
import sqlite3
import os
import psycopg2
from psycopg2.extras import DictCursor

# def connect_db():
#     sql = sqlite3.connect("./questions.db")
#     sql.row_factory = sqlite3.Row
#     return sql

# def get_db():
#     if not hasattr(g, 'sqlite_db'):
#         g.sqlite_db = connect_db()
#     return g.sqlite_db

# def extract_dbs(db_result):
#     result = []

#     if len(db_result) == 0:
#         return result
        
#     for d in db_result:
#         d = dict(d)
#         result.append(d)

#     return result

# def extract_db(db_result):

#     if len(db_result) == 0:
#         return {}

#     return dict(db_result)


def connect_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=DictCursor)
    conn.autocommit = True
    sql = conn.cursor()
    return conn, sql

def get_db():
    db = connect_db()

    if not hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn = connect_db()[0]
    if not hasattr(g, 'postgres_db_cur'):
        g.postgres_db_cur = connect_db()[1]

    return g.postgres_db_cur

# def init_db():
#     db = connect_db()
#     db[1].execute(open('schema.sql', 'r').read())
#     db[1].close()
#     db[0].close()

# How to run this function
# docker-compose exec web_app python -c "import dbcon; dbcon.init_admin()"
def init_admin():
    db = connect_db()
    db[1].execute("update users set admin=True where name=%s", ('admin',))
    db[1].close()
    db[0].close()