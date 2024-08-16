# Aurora-ntfy

This application is for sending alerts based on the Aurora's KP Index.
It scrapes sources from the US National Oceanic and Atmospheric Administration (NOAA) for the current KP Index, the KP Index in a 3 hour Interval, the Highest KP in an evening, and the Average KP in an evening.

If any of those KP Indexes are above the Target KP, a notification is sent to the specified ntfy instance.
That notification will have a picture of the forecasted Aurora Borealis visibility Forecast.
Clicking the notification will open NOAA's Aurora Dashboard in a web browser.

## Configuration

This application's settings are stored in a JSON file.
It must be named `config.json`.

Available settings to configure:
* `ntfy_url` - The URL of the ntfy instance to send the notification to.
* `ntfy_priority` - The Priority of the ntfy notification.
* `local_timezone` - The timezone to observe the Aurora at night.
* `target_kp` - The minimum KP current or forecasted value to send the notification.