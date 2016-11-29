SELECT time_avg.name,
       time_avg.ghc_version,
       time_avg.average_time,
       file_size.total_size
  FROM (SELECT
          package.name AS name,
          result.version AS ghc_version,
          avg(result.seconds) AS average_time
        FROM package, batch, result
        WHERE package.id = batch.package
          AND batch.id   = result.batch
        GROUP BY name, ghc_version) AS time_avg
  LEFT OUTER JOIN
       (SELECT
          package.name AS name,
          result.version AS ghc_version,
          sum(file_output.file_size) AS total_size
        FROM package, batch, result, file_output
        WHERE package.id = batch.package
          AND batch.id   = result.batch
          AND result.id  = file_output.result
          AND file_output.file_extension = 'hi'
        GROUP BY name, ghc_version) AS file_size
     ON time_avg.name = file_size.name
    AND time_avg.ghc_version  = file_size.ghc_version
  ORDER BY time_avg.name, time_avg.ghc_version DESC;
