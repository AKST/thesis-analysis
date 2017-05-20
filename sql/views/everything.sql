-- the main purpose is to search for outliers
CREATE OR REPLACE VIEW thesis.everything_linked AS
  SELECT package.id                 as package_id
       , package.name               as package_name
       , package.min_ghc            as package_min_ghc
       , package.max_ghc            as package_max_ghc
       , batch.id                   as batch_id
       , batch.start_time           as batch_start_time
       , script.id                  as script_hash
       , script.tags                as script_tags
       , result.id                  as result_id
       , result.version             as result_version
       , result.seconds             as result_seconds
       , file_output.relative_path  as file_output_relative_path
       , file_output.file_extension as file_output_file_extension
       , file_output.file_size      as file_output_file_size
    FROM thesis.package_whitelist         as package
       RIGHT JOIN thesis.batch            as batch       ON batch.package      = package.id
       RIGHT JOIN thesis.benchmark_script as script      ON script.id          = batch.checksum
       RIGHT JOIN thesis.result           as result      ON result.batch       = batch.id
       RIGHT JOIN thesis.file_output      as file_output ON file_output.result = result.id;
