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

## Decisions

### Combined vs Separate Repos for Bus and Rail?

Bus GTFS processing and Rail GTFS processing looks different.

Options: 
1. Combined Bus & Rail + Validation Code
    - One single repository that includes bus GTFS, rail GTFS, separate processing code for each, common code for automating validation and email notifications.
2. Separate Bus & Rail + Validation Repo
    - Separate repositories for bus GTFS + processing and rail GTFS + processing.
    - Automated validation and email notifications would live in a separate place and would just be triggered by the bus/rail rep os as needed.  This could be a third repository or a GH Action.

Concerns:

- Code redundancy
- Repo size

Workflow:

- Rail GTFS
  - Runs nightly 
  - File is picked up from FTP location
  - File is run through validation
  - If validation is successful:
    - Update repository files
    - Send email notification of update to data consumers
  - If validation is not successful:
    - Do not update repository files
    - Send email notification to administrators

- Bus GTFS
  - 3 active branches: `main`, `future-service`, `current-base`
  - Multiple triggers for runs:
    - Bus Shakeups multiple times a year, cannot be scheduled
    - Dodger Stadium & SoFi Stadium Express service, cannot be scheduled
    - Weekly `calendar_dates.txt` files.
  - Weekly `calendar_dates.txt` file
    - Weekly basis, Wednesday early AM
    - File is picked up from FTP location
    - Add this file to `main` branch under a sub-folder: `current/calendar_dates.txt`
    - Merge this new file into the existing `calendar_dates.txt` within `main`, removing the existing 2-week span.
    - Re-zip all the files into a new GTFS
    - Run new file through validation
    - If validation is successful:
      - Update `main` branch files
      - Send email notification of update to data consumers
    - If validation is not successful:
      - Do not update `main` branch files
      - Send email notification to administrators
  - Stadium Express Service
    - A few times a year, not predictable and cannot be scheduled.
    - The `dse-sofi-express.csv` file is updated in the `main` branch.
    - This triggers processing:
      - The `dse-sofi-express.csv` file is merged into `calendar_dates.txt` in the `main` branch.
    - Re-zip all the files into a new GTFS
    - Run new file through validation
    - If validation is successful:
      - Update `main` branch files
      - Send email notification of update to data consumers
    - If validation is not successful:
      - Do not update `main` branch files
      - Send email notification to administrators
  - Bus Shakeup
    - Upload file to `future-service` branch and we set a publish date in a config file
    - This triggers processing (GH-Action #1):
      - Checkout the `current/calendar_dates.txt` file from the `main` branch and commit it to the `future-service` branch
      - Merge the `current/calendar_dates.txt` file into the `calendar_dates.txt` file in the `future-service` branch
      - Checkout the `dse-sofi-express.csv` from the `main` branch and commit it to the `future-service` branch
      - Merge the `dse-sofi-express.csv` file into the `calendar_dates.txt` file in the `future-service` branch
    - Re-zip all the files into a new GTFS
    - Run new file through validation
    - If the validation is successful:
      - Update `future-service` branch files
      - On the configured publish date (GH-Action #2):
        - `future-service` branch will be merged into `main` branch and the GTFS zip file to `current-base`
        - Send email notification of update to data consumers
    - If the validation is not successful:
      - Do not update `future-service` branch files
      - Send email notification to administrators
