
CREATE TYPE semver AS (
  major int,
  minor int,
  patch int
);


-- transforms text into a semver
CREATE OR REPLACE FUNCTION semver_read(input text) RETURNS semver AS $$
  DECLARE
    es int[];
  BEGIN
    es := string_to_array(input, '.');
    IF array_length(es, 1) = 3 THEN
      RETURN row(es[1], es[2], es[3])::semver;
    ELSE
      RAISE EXCEPTION 'incorrect index size';
    END IF;
  END
$$ LANGUAGE 'plpgsql';


-- '>' than operator implementation
CREATE OR REPLACE FUNCTION semver_comp(l semver, r semver) RETURNS int AS $$
  BEGIN
    IF l.major > r.major THEN
      RETURN 1;
    ELSIF l.major < r.major THEN
      RETURN -1;
    ELSE
      IF l.minor > r.minor THEN
        RETURN 1;
      ELSIF l.minor < r.minor THEN
        RETURN -1;
      ELSE
        IF l.patch > r.patch THEN
          RETURN 1;
        ELSIF l.patch < r.patch THEN
          RETURN -1;
        ELSE
          RETURN 0;
        END IF;
      END IF;
    END IF;
  END
$$ LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION semver_lt(l semver, r semver) RETURNS bool AS $$
  BEGIN RETURN semver_comp(l, r) = -1; END
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION semver_gt(l semver, r semver) RETURNS bool AS $$
  BEGIN RETURN semver_comp(l, r) = 1; END
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION semver_eq(l semver, r semver) RETURNS bool AS $$
  BEGIN RETURN semver_comp(l, r) = 0; END
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION semver_lteq(l semver, r semver) RETURNS bool AS $$
  BEGIN RETURN semver_comp(l, r) <> 1; END
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION semver_gteq(l semver, r semver) RETURNS bool AS $$
  BEGIN RETURN semver_comp(l, r) <> -1; END
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION semver_neq(l semver, r semver) RETURNS bool AS $$
  BEGIN RETURN semver_comp(l, r) <> 0; END
$$ LANGUAGE 'plpgsql';


CREATE CAST (text as semver)
  WITH FUNCTION semver_read(text)
  AS IMPLICIT;


CREATE OPERATOR = (
  LEFTARG    = semver,
  RIGHTARG   = semver,
  procedure  = semver_eq,
  commutator = =);

CREATE OPERATOR < (
  LEFTARG    = semver,
  RIGHTARG   = semver,
  procedure  = semver_lt,
  commutator = <);

CREATE OPERATOR > (
  LEFTARG    = semver,
  RIGHTARG   = semver,
  procedure  = semver_gt,
  commutator = >);

CREATE OPERATOR >= (
  LEFTARG    = semver,
  RIGHTARG   = semver,
  procedure  = semver_gteq,
  commutator = >=);

CREATE OPERATOR <= (
  LEFTARG    = semver,
  RIGHTARG   = semver,
  procedure  = semver_lteq,
  commutator = <=);

CREATE OPERATOR <> (
  LEFTARG    = semver,
  RIGHTARG   = semver,
  procedure  = semver_neq,
  commutator = <>);

CREATE OPERATOR CLASS semver_ops
  DEFAULT FOR TYPE semver USING btree AS
    OPERATOR 1 <,
    OPERATOR 2 <=,
    OPERATOR 3 =,
    OPERATOR 4 >=,
    OPERATOR 5 >,
    function 1 semver_comp(semver, semver);
