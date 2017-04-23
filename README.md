# Thesis benchmark analysis

The code in this repository serves two purposes.

  1. Recording the data in a database
  2. Analysising the data stored in said database.
  3. Ensures when populating the database that it does
     push duplicate information into the database using
     `CONFLICT` clauses on unique indexes

## Different Analysis utlities

- `scripts/populate.py` The data base population script
- `scripts/format.py` Outputs data from the database in different formats
- `scripts/server.py` Provides a read only JSON API for reading the data

> It's worth noting that scripts/format is just a cli interface to
> the same application as scripts/server, scripts/server just uses
> http as the main means of input instead of command line arguements

## Help on arguments

If you want some help on the figuring out the required
arguments, just run the following.

```
python3 scripts/populate.py --help
python3 scripts/format.py --help
python3 scripts/server.py --help
```
