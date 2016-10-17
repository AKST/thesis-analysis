WITH

time_avg AS (
  SELECT
    package.name as name,
    result.version as ghc_version,
    avg(result.seconds) as average_time
  FROM package, batch, result
  WHERE package.id = batch.package
    AND batch.id   = result.batch
  GROUP BY name, ghc_version),

file_size AS (
  SELECT
    package.name as name,
    result.version as ghc_version,
    sum(file_output.file_size) as total_size
  FROM package, batch, result, file_output
  WHERE package.id = batch.package
    AND batch.id   = result.batch
    AND result.id  = file_output.result
    AND file_output.file_extension = 'hi'
  GROUP BY result.id, name, ghc_version)

SELECT time_avg.name,
       time_avg.ghc_version,
       time_avg.average_time,
       file_size.total_size
  FROM time_avg, file_size
  WHERE time_avg.name        = file_size.name
    AND time_avg.ghc_version = file_size.ghc_version
  ORDER BY average_time DESC;


