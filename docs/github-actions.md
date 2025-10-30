# GitHub Actions Workflow Documentation

## Update GTFS Data Workflow

The `update-gtfs.yml` workflow automates the process of updating GTFS data by downloading the latest `calendar_dates.txt` file from an FTP server and updating the repository.

### Manual Execution

To run the workflow manually:

1. Go to the **Actions** tab in your GitHub repository
2. Select **Update GTFS Data** from the workflow list
3. Click **Run workflow**
4. Optionally provide a reason for the manual run
5. Click **Run workflow** to execute

### Required Secrets

The workflow requires the following GitHub Secrets to be configured:

- `FTP_USERNAME`: Username for FTP server access
- `FTP_PASS`: Password for FTP server access
- `SERVER`: FTP server hostname/IP address
- `GITLAB_TOKEN`: Token for accessing the GitLab repository

### Monitoring

- Check the **Actions** tab for workflow execution history
- Review workflow summaries for execution details
- Monitor commit history for automated updates
