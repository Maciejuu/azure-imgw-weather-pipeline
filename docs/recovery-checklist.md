# Recovery checklist

## Original files still needed

- Actual App Service startup configuration; Flask source, templates, static assets and dependencies have now been recovered.
- Script or commands used to upload maps to Blob Storage.
- Original cron configuration and shell environment setup.
- Azure resource/deployment configuration, if available.

## Before executing the recovered scripts

- Review container throughput settings and network access.
- Configure Cosmos environment variables without committing credentials.
- Verify package compatibility and create the `mapy/` directory.
- Fix `plt.show(bbox_inches='tight')` in the mapping script and configure headless plotting.
- Add the missing `redirect` import in Flask before using the image redirect route.
- Configure both Cosmos database variable names and the Blob Storage settings.
- Verify browser access to blob images and the template wind-speed unit label.
- Validate missing data handling and timestamp conversion.
- Review geocoder accuracy, caching and usage requirements.

## Before publishing the original report

- Review screenshots for credentials, account/subscription details and unnecessary infrastructure identifiers.
- Credit Jakub Maciejak for the complete implementation. The original academic report lists two authors; preserve that document attribution when including the report.

## Not included

The recovered Flask application and original deployment workflow are included. The workflow is stored as an inactive example under `docs/deployment/`. No replacement upload script, cron job or infrastructure deployment was invented.
