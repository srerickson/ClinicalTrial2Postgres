# Scripts for Clinical Trial Data Wrangling

The scripts in this repo are used to load clinical trial data from [clinicaltrials.gov](https://clinicaltrials.gov/ct2/home) into a Postgres database for easier querying and manipulation.


## Words of Warning

  * These scripts were written for a project and I have no plans to maintain them.
  * They have only been used on Mac OS 10.13, Python 2.7.
  * The procedure below will require about 15GB of disk space. After ingest, you can delete `AllPublicXML` to free up some of that.

## Step-by-Step

  * Setup your PostgreSQL database (`setup_postgres.sh` can help with this if you have Docker installed).
  * Download clinical trial records using instructions [here](https://clinicaltrials.gov/ct2/resources/download#DownloadAllData). This will give you a ~1.4GB file, `AllPublicXML.zip`.
  * Unzip the file and place the resulting folder (`AllPublicXML`) alongside the scripts in this repo.
  * Edit the database connection settings at the top of `ingest.py` as needed. The database named with `db_name` should exist but you don't need to create any tables.
  * run `$ python ingest.py AllPublicXML`. This will take a while--about an hour or more depending on the speed of your computer.

## Example Query

```sql
-- temp tables used to expand json arrays of objects
CREATE TEMP TABLE location_struct(facility jsonb, investigator jsonb);
CREATE TEMP TABLE investigator_struct(first_name text, last_name text);

SELECT
  cs.id_info->'nct_id' nct_id,
  locs.facility->'address'->'zip' zip,
  invs.last_name as name
  FROM cs,
    jsonb_populate_recordset(NULL::location_struct, cs.location) locs,
    jsonb_populate_recordset(NULL::investigator_struct, locs.investigator) invs;
```
