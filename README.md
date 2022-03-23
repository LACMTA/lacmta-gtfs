# lacmta-gtfs

View the [workflow](docs/workflow.html).

## Notes

### Express Service

The file at `/inputs/dse-sofi-express.csv` contains special Express Bus service serving Dodger Stadium and SoFi Stadium during baseball and football seasons.

### Calendar_dates.txt

A new `calendar_dates.txt` file is generated weekly Tuesday night/Wednesday morning. It contains data for only the following two weeks. Each new `calendar_dates.txt` overlaps the previous one by 1 week. As a result, the weekly `calendar_dates.txt` file cannot just be appended to the GTFS base `calendar_dates.txt` file. The GTFS base files are the ones released from the most recent shakeup.

This automation script performs the following steps:

1. Load GTFS base `calendar_dates.txt` file.
2. Load the weekly `calendar_dates.txt` file.
