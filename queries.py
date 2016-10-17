from typing import Any
from typing import Dict

import util

def insert_package_get_id(cursor: Any, package: util.PackagePath) -> int:
    name = package.name
    cursor.execute("""
      INSERT INTO package (name) VALUES (%s)
        ON CONFLICT (name)
        DO UPDATE SET (name) = (%s)
        RETURNING id
    """, (name, name))
    return cursor.fetchone()[0]

def insert_batch(cursor: Any, task: util.TaskMeta, ids: Dict[str, int]) -> None:
    package_id = ids[task.package]
    cursor.execute("""
      INSERT INTO batch (id, package, start_time)
        VALUES (%s, %s, %s) ON CONFLICT (id) DO
        UPDATE SET (id, package, start_time) = (%s, %s, %s)
    """, (task.id, package_id, task.stime) * 2)

def insert_result(cursor: Any, result: util.PackageVersionResult, task: util.TaskMeta) -> None:
    secs = result.compile_time
    cursor.execute("""
      INSERT INTO result (version, batch, seconds)
        VALUES (%s::text::semver, %s, %s) ON CONFLICT (version, batch) DO
        UPDATE SET (seconds) = (%s)
        RETURNING id
    """, (result.version, task.id, secs, secs))

    result_id = cursor.fetchone()[0];
    for fsize in result.file_sizes:
        # on conflict we'll update the file extension in the event
        # that we change the means of determining that. Like wise
        # we may modify the means of determining file size.
        cursor.execute("""
          INSERT INTO file_output (result, relative_path, file_extension, file_size)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (result, relative_path)
            DO UPDATE SET (file_extension, file_size) = (%s, %s)
        """, (result_id, fsize.path, fsize.extension, fsize.size, \
                fsize.extension, fsize.size))

