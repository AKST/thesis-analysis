CREATE OR REPLACE VIEW thesis.benchmark_script_whitelist AS
  SELECT * FROM thesis.benchmark_script
    WHERE not(thesis.tags_contains(tags, 'blacklisted'));
