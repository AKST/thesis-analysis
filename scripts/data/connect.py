from psycopg2 import connect as db_connect

from typing import Any

def pg_connection(conf: Any) -> Any:
    dbname = conf.db_name
    host = conf.db_host
    user = conf.db_user
    pswd = conf.db_pass
    return db_connect(host=host, dbname=dbname, user=user, password=pswd)
