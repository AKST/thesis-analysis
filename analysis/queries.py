from typing import Any
from typing import Dict

import util

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
        DO UPDATE SET (name, commit_hash, repo_url, min_ghc, max_ghc) =
            (%s, %s, %s, %s::text::semver, %s::text::semver)
        RETURNING id
    """, (name, _hash, _url, _min, _max) * 2)
    return cursor.fetchone()[0]

def insert_script(cursor: Any, script: util.FileName) -> None:
    with open(script.path, 'r') as f:
        contents = f.read()
        cursor.execute("""
          INSERT INTO thesis.benchmark_script (id, repr) VALUES (decode(%s, 'hex'), %s)
            ON CONFLICT (id)
            DO UPDATE SET (repr) = (%s)
        """, (script.name, contents, contents))

def insert_batch(cursor: Any, task: util.TaskMeta, ids: Dict[str, int]) -> None:
    package_id = ids[task.package]
    cursor.execute("""
      INSERT INTO thesis.batch (id, package, start_time, checksum)
        VALUES (%s, %s, %s, decode(%s, 'hex')) ON CONFLICT (id) DO
        UPDATE SET (id, package, start_time, checksum) = (%s, %s, %s, decode(%s, 'hex'))
    """, (task.id, package_id, task.stime, task.checksum) * 2)

def insert_result(cursor: Any, result: util.PackageVersionResult, task: util.TaskMeta) -> None:
    secs = result.compile_time
    cursor.execute("""
      INSERT INTO thesis.result (version, batch, seconds)
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
          INSERT INTO thesis.file_output (result, relative_path, file_extension, file_size)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (result, relative_path)
            DO UPDATE SET (file_extension, file_size) = (%s, %s)
        """, (result_id, fsize.path, fsize.extension, fsize.size, \
                fsize.extension, fsize.size))

