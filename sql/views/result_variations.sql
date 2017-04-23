-- a view for producing human readable results
CREATE OR REPLACE VIEW thesis.results_readable AS
  SELECT package.name AS package_name
       , results.ghc_version AS ghc_version
       , results.file_extension AS file_extension
       , results.average_time
       , results.file_size
       , results.script_hash AS script_hash
       , benchmark_script.tags AS script_tags
       , benchmark_script.last_modified as script_age
    FROM thesis.results_hashed as results
       , thesis.package as package
       , thesis.benchmark_script as benchmark_script
    WHERE results.package_id = package.id
      AND benchmark_script.id = results.script_hash
    ORDER BY package_name ASC
           , ghc_version DESC
           , file_extension ASC
           , last_modified DESC
           ;

-- a view for producing human readable results
CREATE OR REPLACE VIEW thesis.results_api_latest_O2 AS
  SELECT results.*
    FROM thesis.results_hashed as results
      INNER JOIN (SELECT script.id AS id
        FROM thesis.benchmark_script AS script
        WHERE thesis.tags_contains(script.tags, 'shared_optimization')
          AND thesis.tags_contains(script.tags, 'optimization:2')
        ORDER BY script.activity_timestamp DESC LIMIT 1) as script
      ON script.id = results.script_hash;

-- view of latest results
CREATE OR REPLACE VIEW thesis.results_latest AS
  SELECT results.*
    FROM thesis.results_readable as results
      INNER JOIN (SELECT script.id AS id
        FROM thesis.benchmark_script AS script
        ORDER BY script.activity_timestamp DESC LIMIT 1) as script
      ON script.id = results.script_hash;

-- view latest -O2 results
CREATE OR REPLACE VIEW thesis.results_latest_O2 AS
  SELECT results.*
    FROM thesis.results_readable as results
      INNER JOIN (SELECT script.id AS id
        FROM thesis.benchmark_script AS script
        WHERE thesis.tags_contains(script.tags, 'shared_optimization')
          AND thesis.tags_contains(script.tags, 'optimization:2')
        ORDER BY script.activity_timestamp DESC LIMIT 1) as script
      ON script.id = results.script_hash;

