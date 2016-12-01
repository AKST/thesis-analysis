CREATE FUNCTION timestamp_trigger() RETURNS TRIGGER LANGUAGE 'plpgsql' AS $$ BEGIN
  NEW.activity_timestamp := now();
  RETURN NEW
END $$;
