CREATE TYPE average AS (
  name TEXT,
  version SEMVER,
  time TIMESTAMP,
  file_size BIGINT,
  file_extension text
);
