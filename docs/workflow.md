# Workflow

## Schedule

`update_gtfs.py` is automatically run on a weekly basis, Wednesdays at 11am UTC/3am PTC (via `.github/workflows/python-publish.yml`).

## Components

### `gtfs_bus`

The `gtfs_bus` repository is hosted [on GitLab](https://gitlab.com/LACMTA/gtfs_bus) and contains Metro's official GTFS for bus service.

Branches:

- `master` - This branch reflects currently active service.  We avoid making changes to this branch as much as possible because this represents the "base" service defined at the start of the shakeup.
- `future-service` - Future service.  An updated GTFS will be pushed to this branch roughly 1-2 weeks before a new shakeup goes into effect.  This branch does not contain current service merged with future service; the service dates in this branch will not overlap with the `master` branch.  This branch will be merged into the `master` branch the night before the new service goes into effect.  At that point, this branch will effectively reflect "current" service until the GTFS files for the next shakeup become available.
- `weekly-updated-service` - This branch will be updated weekly and will contain the accumulation of weekly updates to the `master` branch following the most recent shakeup.  Updates will include the integration of a weekly generated `calendar_dates.txt` file that updates service for the two following weeks, as well as the addition of temporary express bus service (such as the Dodger Stadium Express and the SoFi Stadium Express).

## Behavior

Diagram for the automation running in this repository:

![GTFS Bus auto-update workflow](gtfs-bus-auto-update-workflow.png)

Download the weekly calendar_dates.txt file from the FTP server and convert it into a List-type.

Check if a new shakeup has occured within the last week:

- Get the date range for the most recently created weekly updates by calculating the date range from the `calendar.txt` file in the `weekly-updated-service` branch.
- Get the date range for currently active service by calculating the date range from the `calendar.txt` file in the `master` branch.
- Compare to see if the date range from `weekly-updated-service` falls within the date range from `master`.  If NOT, a shakeup has occured.

If a shakeup has occured, clear out the contents of the `calendar_dates.txt`




3. Calculate from the weekly calendar_dates.txt file, the 2-week date range we are in.
4. Convert the dse-sofi-express.csv data into List format.
5. Filter the express data by the 2-week date range.
6. Combine the weekly calendar_dates.txt with the filtered express data.
7. Pull the starting/current calendar_dates.txt file and conver it into List format.
8. Filter the starting/current calendar_dates.txt to remove entries in the 2-week date range.
9. Combine the filtered starting/current calendar_dates.txt with the combined weekly calendar_dates/express data and write the results to a file.
10. Push the new file to the GitLab `gtfs_bus` repository.
11. Update the RSS feed in order to trigger an automated ActiveCampaign email.
