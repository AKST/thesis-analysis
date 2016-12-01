\i sql/types/semver.sql

CREATE TABLE IF NOT EXISTS package (
  id                 SERIAL UNIQUE NOT NULL,
  name               TEXT   UNIQUE NOT NULL,
  commit_hash        TEXT          NOT NULL,
  repo_url           TEXT          NOT NULL,
  min_ghc            SEMVER        NOT NULL,
  max_ghc            SEMVER        NOT NULL,
  activity_timestamp TIMESTAMP default current_timestamp
);

CREATE TABLE IF NOT EXISTS benchmark_script (
  id                 bytea  UNIQUE NOT NULL,
  repr               text UNIQUE NOT NULL,
  activity_timestamp TIMESTAMP default current_timestamp
);

CREATE TABLE IF NOT EXISTS batch (
  id                 UUID   UNIQUE                          NOT NULL,
  package            SERIAL REFERENCES package(id)          NOT NULL,
  start_time         TIMESTAMP                              NOT NULL,
  checksum           bytea  REFERENCES benchmark_script(id) NOT NULL,
  activity_timestamp TIMESTAMP default current_timestamp
);

CREATE TABLE IF NOT EXISTS result (
  id                 SERIAL UNIQUE               NOT NULL,
  batch              UUID   REFERENCES batch(id) NOT NULL,
  version            SEMVER                      NOT NULL,
  seconds            DECIMAL                     NOT NULL,
  activity_timestamp TIMESTAMP default current_timestamp
);

CREATE TABLE IF NOT EXISTS file_output (
  id                 SERIAL UNIQUE                NOT NULL,
  result             SERIAL REFERENCES result(id) NOT NULL,
  relative_path      TEXT                         NOT NULL,

  -- some files don't have extensions so it
  -- makes sense that file_extension is nullable
  file_extension     TEXT                             NULL,
  file_size          BIGINT                       NOT NULL,
  activity_timestamp TIMESTAMP default current_timestamp
);

-- we know that only one row can have a
-- unique combination of batch and version
CREATE UNIQUE INDEX IF NOT EXISTS unique_result_batch_version
  ON result (batch, version);

-- we know that only one row can have a
-- unique combination of result and relative_path
CREATE UNIQUE INDEX IF NOT EXISTS unique_fileoutput_relativepath_result
  ON file_output (result, relative_path);

CREATE TRIGGER
