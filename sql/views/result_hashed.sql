CREATE MATERIALIZED VIEW IF NOT EXISTS thesis.results_hashed AS
  WITH
    -- aggregate the average compilation times
    time_avg AS (
      SELECT
        package.id AS package_id,
        result.version AS ghc_version,
        avg(result.seconds) AS average_time,
        batch.checksum AS checksum
      FROM thesis.package_whitelist AS package,
           thesis.batch AS batch,
           thesis.result AS result
      WHERE package.id = batch.package
        AND batch.id   = result.batch
      GROUP BY package_id, ghc_version, checksum),

    -- aggregate the total size of hi file type
    file_size AS (
      SELECT
        package.id AS package_id,
        result.version AS ghc_version,
        sum(file_output.file_size) AS total_size,
        file_output.file_extension AS extension,
        batch.checksum AS checksum
      FROM thesis.package_whitelist AS package,
           thesis.batch AS batch,
           thesis.result AS result,
           thesis.file_output AS file_output
      WHERE package.id = batch.package
        AND batch.id   = result.batch
        AND result.id  = file_output.result
      GROUP BY package_id, ghc_version, extension, checksum)

  SELECT time_avg.package_id AS package_id,
         time_avg.ghc_version AS ghc_version,
         time_avg.average_time AS average_time,
         file_size.total_size AS file_size,
         file_size.extension AS file_extension,
         scripts.id as script_hash
    FROM file_size
      INNER JOIN thesis.benchmark_script_whitelist
        AS scripts ON scripts.id = file_size.checksum
      INNER JOIN time_avg
        ON time_avg.package_id = file_size.package_id
        AND time_avg.checksum = file_size.checksum
        AND time_avg.ghc_version = file_size.ghc_version
    ORDER BY
      time_avg.package_id ASC,
      time_avg.ghc_version DESC,
      extension ASC,
      scripts.id ASC;
