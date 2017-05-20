
CREATE OR REPLACE FUNCTION thesis.tags_contains (text[], text) RETURNS boolean
  AS 'select ($1 @> array[$2])'
  LANGUAGE SQL;


-- add tag column if not added
DO $$
  -- let's add
  BEGIN
    BEGIN
      ALTER TABLE thesis.benchmark_script
        ADD COLUMN tags text[] NOT NULL DEFAULT '{}';
    EXCEPTION WHEN duplicate_column THEN
      RAISE NOTICE 'column "tags" already exists in "thesis.benchmark_script".';
    END;
  END;
$$;

-- reset the tags column
UPDATE thesis.benchmark_script SET tags = '{}';

-- unspecifed optmizations
UPDATE thesis.benchmark_script
  SET tags = tags || array['optimization:?']
  WHERE not(repr ~ '-O')
    AND not(thesis.tags_contains(tags, 'optimization:?'));

-- tag optimization level 0
UPDATE thesis.benchmark_script
  SET tags = tags || array['optimization:*']
  WHERE repr ~ '-O\*'
    AND not(thesis.tags_contains(tags, 'optimization:*'));

-- tag optimization level 0
UPDATE thesis.benchmark_script
  SET tags = tags || array['optimization:0']
  WHERE repr ~ '-O0'
    AND not(thesis.tags_contains(tags, 'optimization:0'));

-- tag optimization level 1
UPDATE thesis.benchmark_script
  SET tags = tags || array['optimization:1']
  WHERE repr ~ '-O1'
    AND not(thesis.tags_contains(tags, 'optimization:1'));

-- tag optimization level 2
UPDATE thesis.benchmark_script
  SET tags = tags || array['optimization:2']
  WHERE repr ~ '-O2'
    AND not(thesis.tags_contains(tags, 'optimization:2'));

-- tags shared builds disabled
UPDATE thesis.benchmark_script
  SET tags = tags || array['shared:disabled']
  WHERE repr SIMILAR TO '%\n\s+(cabal)\s+(configure)\s+(--disable-shared)\s*\n%'
    AND not(thesis.tags_contains(tags, 'shared:disabled'));

-- tags shared builds enabled
UPDATE thesis.benchmark_script
  SET tags = tags || array['shared:enabled']
  WHERE not(repr SIMILAR TO '%\n\s+(cabal)\s+(configure)\s+(--disable-shared)\s*\n%')
    AND not(thesis.tags_contains(tags, 'shared:enabled'));


-- for scripts where both the output size and compile time
-- benchmarks use consistent optimization flags, there are
-- some cases where does not happen, it happens during cases
-- where the representation matches the similarity checks
UPDATE thesis.benchmark_script
  SET tags = tags || array['consistent_optimization']
  WHERE ((repr ~ 'local target_optimization="-O[0-2\*]"') OR not(repr ~ '-O'))
    AND not(thesis.tags_contains(tags, 'consistent_optimization'));

