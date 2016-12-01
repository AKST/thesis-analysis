# Thesis benchmark analysis

The code in this repository serves two purposes.

  1. Recording the data in a database
  2. Analysising the data stored in said database.
  3. Ensures when populating the database that it does
     push duplicate information into the database using
     `CONFLICT` clauses on unique indexes

## help on arguments

If you want some help on the figuring out the required
arguments, just run the following.

```
python3 analysis --help
```
