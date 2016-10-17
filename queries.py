from typing import Any

import util

def insert_package_get_id(cursor: Any, name: str) -> int:
    cursor.execute("""
      WITH
        s_rel AS (SELECT id FROM package WHERE name = %s),
        i_rel AS (
          INSERT INTO package (name) SELECT %s
            WHERE NOT EXISTS (SELECT id FROM package WHERE name = %s)
            RETURNING id)
      SELECT id FROM i_rel UNION ALL
      SELECT id FROM s_rel
    """, (name, name, name))
    return cursor.fetchone()[0]

def insert_batch_get_id(cursor: Any, package: util.TaskMeta) -> Any:
    return None
