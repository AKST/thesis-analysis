CREATE MATERIALIZED VIEW IF NOT EXISTS thesis.package_whitelist AS
  SELECT * FROM thesis.package WHERE name <> 'array';
