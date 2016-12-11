-- creates consumer role
--   - role for consuming the api
--   - password needs to be replaced
CREATE ROLE consumer WITH
   NOCREATEROLE
   NOCREATEUSER
   LOGIN
   CONNECTION LIMIT 20
   PASSWORD 'replace_me';

-- creates producer role
--   - role for populating and updating the database
--   - password needs to be replaced
CREATE ROLE producer WITH
   NOCREATEROLE
   NOCREATEUSER
   LOGIN
   CONNECTION LIMIT 5
   PASSWORD 'replace_me';

-- allows roles to utilise schema
GRANT usage ON SCHEMA thesis TO producer;
GRANT usage ON SCHEMA thesis TO consumer;

-- allows roles to utilise sequences
GRANT usage, select ON ALL SEQUENCES IN SCHEMA thesis TO producer;
GRANT usage, select, update ON ALL SEQUENCES IN SCHEMA thesis TO producer;

-- allows roles to utilise tables
GRANT
  select,
  references
ON ALL TABLES IN SCHEMA thesis TO consumer;

GRANT
  select,
  references,
  truncate,
  delete,
  insert,
  update
ON ALL TABLES IN SCHEMA thesis TO producer;

-- allows roles to functions sequences
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA thesis TO consumer;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA thesis TO producer;
