CREATE TABLE IF NOT EXISTS package (
  id   SERIAL UNIQUE NOT NULL,
  name TEXT          NOT NULL
);

CREATE TABLE IF NOT EXISTS batch (
  id         UUID   UNIQUE                 NOT NULL,
  package    SERIAL REFERENCES package(id) NOT NULL,
  start_time TIMESTAMP                     NOT NULL
);

CREATE TABLE IF NOT EXISTS result (
  id      SERIAL UNIQUE               NOT NULL,
  batch   UUID   REFERENCES batch(id) NOT NULL,
  version TEXT                        NOT NULL,
  seconds DECIMAL                     NOT NULL
);

CREATE TABLE IF NOT EXISTS file_output (
  id             SERIAL UNIQUE                NOT NULL,
  result         SERIAL REFERENCES result(id) NOT NULL,
  relative_path  TEXT                         NOT NULL,

  -- some files don't have extensions so it
  -- makes sense that file_extension is nullable
  file_extension TEXT                             NULL,
  file_size      BIGINT                       NOT NULL
);
