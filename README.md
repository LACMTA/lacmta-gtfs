# lacmta-gtfs

Automation works!

## Details

Run weekly, Wednesdays in the AM:

1. Pull weekly generated file `CALENDAR_DATES_WEEKLY` from the FTP server. ✅
2. Generate the 2-week date range.✅
3. Pull the most recent file `CALENDAR_DATES_CURRENT` from GitLab.✅
4. Remove lines from `CALENDAR_DATES_CURRENT` that fall within the date range.✅
5. Append the `CALENDAR_DATES_WEEKLY` file to the `CALENDAR_DATES_CURRENT` file. 😭
6. Pull the DSE & SOFI Express `CALENDAR_DATES_EXPRESS` data from GitHub.✅
7. Filter `CALENDAR_DATES_EXPRESS` data for the date range.✅
8. Append the filtered `CALENDAR_DATES_EXPRESS` data to `CALENDAR_DATES_CURRENT` to generate a `NEW_CALENDAR_DATES_CURRENT`.
9. Push `NEW_CALENDAR_DATES_CURRENT` to GitLab. 🤷
