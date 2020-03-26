from flask import g
import sqlite3

def connect_db():
    sql = sqlite3.connect("./questions.db")
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def extract_dbs(db_result):
    result = []

    if len(db_result) == 0:
        return result
        
    for d in db_result:
        d = dict(d)
        result.append(d)

    return result

def extract_db(db_result):

    if len(db_result) == 0:
        return {}

    return dict(db_result)