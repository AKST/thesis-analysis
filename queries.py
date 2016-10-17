from typing import Any
from typing import Dict

import util

def insert_package_get_id(cursor: Any, package: util.PackagePath) -> int:
    name = package.name
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

def insert_batch(cursor: Any, task: util.TaskMeta, ids: Dict[str, int]) -> None:
    package_id = ids[task.package]
    cursor.execute("""
        INSERT INTO batch (id, package, start_time)
            SELECT %s, %s, %s
            WHERE NOT EXISTS
                (SELECT id FROM batch WHERE id = %s)
    """, (task.id, package_id, task.stime, task.id))

def insert_result(cursor: Any, result: util.PackageVersionResult, task: util.TaskMeta) -> None:
    pass

