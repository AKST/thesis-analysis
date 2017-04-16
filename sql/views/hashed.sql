CREATE MATERIALIZED VIEW IF NOT EXISTS thesis.hashed_results AS
  WITH
    -- aggregate the average compilation times
    time_avg AS (
      SELECT
        package.name AS name,
        result.version AS ghc_version,
        avg(result.seconds) AS average_time,
        batch.checksum AS checksum
      FROM thesis.package AS package,
           thesis.batch AS batch,
           thesis.result AS result
      WHERE package.id = batch.package
        AND batch.id   = result.batch
      GROUP BY name, ghc_version, checksum),

    -- aggregate the total size of hi file type
    file_size AS (
      SELECT
        package.name AS name,
        result.version AS ghc_version,
        sum(file_output.file_size) AS total_size,
        file_output.file_extension AS extension,
        batch.checksum AS checksum
      FROM thesis.package AS package,
           thesis.batch AS batch,
           thesis.result AS result,
           thesis.file_output AS file_output
      WHERE package.id = batch.package
        AND batch.id   = result.batch
        AND result.id  = file_output.result
      GROUP BY name, ghc_version, extension, checksum)

  SELECT time_avg.name AS package_name,
         time_avg.ghc_version AS ghc_version,
         time_avg.average_time AS average_time,
         file_size.total_size AS file_size,
         file_size.extension AS file_extension,
         thesis.benchmark_script.id as script_hash,
         thesis.benchmark_script.tags as script_tags,
         thesis.benchmark_script.last_modified as script_age
    FROM file_size
      INNER JOIN thesis.benchmark_script
        ON thesis.benchmark_script.id = file_size.checksum
      INNER JOIN time_avg
        ON time_avg.name = file_size.name
        AND time_avg.checksum = file_size.checksum
        AND time_avg.ghc_version = file_size.ghc_version
    ORDER BY
      time_avg.name ASC,
      time_avg.ghc_version DESC,
      extension ASC;
