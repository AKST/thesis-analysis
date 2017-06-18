CREATE OR REPLACE VIEW thesis.package_whitelist AS
  SELECT * FROM thesis.package
    WHERE not (name = 'array' OR name = 'lens' OR name = 'hpqtypes');
