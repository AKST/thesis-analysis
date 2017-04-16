from typing import Any
from typing import Dict

from os.path import getmtime

import common.util as util

def insert_package_get_id(cursor: Any, package: util.PackagePath, meta: Dict[str, Any]) -> int:
    # TODO add package meta data
    name = package.name
    _hash = meta['commit_hash']
    _url = meta['url']
    _min = meta['min']
    _max = meta['max']
    cursor.execute("""
      INSERT
          INTO thesis.package (name, commit_hash, repo_url, min_ghc, max_ghc)
          VALUES (%s, %s, %s, %s::text::semver, %s::text::semver)
        ON CONFLICT (name)
        DO UPDATE SET (name, commit_hash, repo_url, min_ghc, max_ghc, activity_timestamp)
          = (%s, %s, %s, %s::text::semver, %s::text::semver, current_timestamp)
        RETURNING id
    """, (name, _hash, _url, _min, _max) * 2)
    return cursor.fetchone()[0]

def insert_script(cursor: Any, script: util.FileName) -> None:
    last_modified = getmtime(script.path)
    with open(script.path, 'r') as f:
        contents = f.read()
        cursor.execute("""
          INSERT
            INTO thesis.benchmark_script AS t (id, repr, last_modified)
            VALUES (decode(%s, 'hex'), %s, to_timestamp(%s))
            ON CONFLICT (id)
            DO UPDATE SET (repr, last_modified, activity_timestamp)
              = (EXCLUDED.repr, greatest(EXCLUDED.last_modified, t.last_modified), current_timestamp)
        """, (script.name, contents, str(last_modified)))

def insert_batch(cursor: Any, task: util.TaskMeta, ids: Dict[str, int]) -> None:
    package_id = ids[task.package]
    cursor.execute("""
      INSERT INTO thesis.batch (id, package, start_time, checksum)
        VALUES (%s, %s, %s, decode(%s, 'hex')) ON CONFLICT (id) DO
        UPDATE SET (id, package, start_time, checksum, activity_timestamp)
          = (%s, %s, %s, decode(%s, 'hex'), current_timestamp)
    """, (task.id, package_id, task.stime, task.checksum) * 2)

def insert_result(cursor: Any, result: util.PackageVersionResult, task: util.TaskMeta) -> None:
    secs = result.compile_time
    cursor.execute("""
      INSERT INTO thesis.result (version, batch, seconds)
        VALUES (%s::text::semver, %s, %s) ON CONFLICT (version, batch) DO
        UPDATE SET (seconds, activity_timestamp)
          = (%s, current_timestamp)
        RETURNING id
    """, (result.version, task.id, secs, secs))

    result_id = cursor.fetchone()[0];
    for fsize in result.file_sizes:
        # on conflict we'll update the file extension in the event
        # that we change the means of determining that. Like wise
        # we may modify the means of determining file size.
        cursor.execute("""
          INSERT INTO thesis.file_output (result, relative_path, file_extension, file_size)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (result, relative_path)
            DO UPDATE SET (file_extension, file_size, activity_timestamp)
              = (%s, %s, current_timestamp)
        """, (result_id, fsize.path, fsize.extension, fsize.size, \
                fsize.extension, fsize.size))

