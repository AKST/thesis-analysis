CREATE MATERIALIZED VIEW IF NOT EXISTS thesis.unique_filetypes AS
  SELECT DISTINCT file_extension as file_type FROM thesis.file_output;
