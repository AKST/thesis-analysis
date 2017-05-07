CREATE MATERIALIZED VIEW IF NOT EXISTS thesis.unique_ghc_versions AS
  SELECT
    source.version                           AS version,
    (source.id::float / source.count::float) AS rank
  FROM
    (SELECT
      row_number() OVER (ORDER BY version) AS id,
      versions.version as version,
      has_count.count as count
    FROM
      (SELECT DISTINCT version                 FROM thesis.result) AS versions,
      (SELECT count(DISTINCT version) AS count FROM thesis.result) AS has_count
    ) AS source;
