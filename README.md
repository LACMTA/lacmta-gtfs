# lacmta-gtfs

## Behavior

`update_gtfs.py` is automatically run on a weekly basis, Wednesdays at 11am UTC/3am PTC (via `.github/workflows/python-publish.yml`).

1. Download the weekly calendar_dates.txt file from FTP.
2. Convert the weekly calendar_dates.txt file into List format.
3. Calculate from the weekly calendar_dates.txt file, the 2-week date range we are in.
4. Convert the dse-sofi-express.csv data into List format.
5. Filter the express data by the 2-week date range.
6. Combine the weekly calendar_dates.txt with the filtered express data.
7. Pull the starting/current calendar_dates.txt file and conver it into List format.
8. Filter the starting/current calendar_dates.txt to remove entries in the 2-week date range.
9. Combine the filtered starting/current calendar_dates.txt with the combined weekly calendar_dates/express data and write the results to a file.
10. Push the new file to the GitLab `gtfs_bus` repository.
11. Update the RSS feed in order to trigger an automated ActiveCampaign email.

## Notes

### Express Service

The file at `/inputs/dse-sofi-express.csv` contains special Express Bus service serving Dodger Stadium and SoFi Stadium during baseball and football seasons.

### Calendar_dates.txt

A new `calendar_dates.txt` file is generated weekly Tuesday night/Wednesday morning. It contains data for only the following two weeks. Each new `calendar_dates.txt` overlaps the previous one by 1 week. As a result, the weekly `calendar_dates.txt` file cannot just be appended to the GTFS base `calendar_dates.txt` file. The GTFS base files are the ones released from the most recent shakeup.

This automation script performs the following steps:

1. Load GTFS base `calendar_dates.txt` file.
2. Load the weekly `calendar_dates.txt` file.
