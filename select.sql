


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
