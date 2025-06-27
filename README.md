# Aurora-ntfy

This application is for sending alerts based on the Aurora's KP Index.
It scrapes sources from the US National Oceanic and Atmospheric Administration (NOAA) that power the [NOAA Aurora Dashboard](https://www.swpc.noaa.gov/communities/aurora-dashboard-experimental) for the current KP Index, the KP Index in a 3 hour Interval, the Highest KP in an evening, and the Average KP in an evening.
It also scrapes sources for [NOAAs 30 Minute forecast](https://www.swpc.noaa.gov/products/aurora-30-minute-forecast) for the probability of seeing an Aurora at a given location.

If any of those KP Indexes are above the Target KP or the probability is above a target threshold, a notification is sent to the specified ntfy instance.
That notification will have a picture of the forecasted Aurora Borealis visibility Forecast for the day.
Clicking the notification will open NOAA's Aurora Dashboard in a web browser.

## Installation and Updating

Aurora-ntfy requires Python 3.11 to be installed.

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/) to manage dependencies.
To install Pipenv using Pip, run `pip install --user pipenv`.
To install dependencies as they are in `Pipfile.lock`, run `pipenv sync`.
To install dependencies that match the `Pipfile`, run `pipenv install`.

This will create a virtual environment specific to this project if none exists, keeping dependencies from conflicting with other Python projects.

## Configuration

This application's settings are stored in a JSON file.
It must be named `config.json`.

Available settings to configure:
* `ntfy_url` - The URL of the ntfy instance to send the notification to.
* `ntfy_priority` - The Priority of the ntfy notification.
* `local_timezone` - The timezone to observe the Aurora at night.
* `target_kp` - The minimum KP current or forecasted value to send the notification.
* `lat` - Latitude to check the Aurora forecast of. Valid values are -90 to 90.
* `long` - Longitude to check the Aurora forecast of. Valid values are -180 to 360.
* `thirty_min_forcast_min` - Minimum threshold of chance to see Aurora at `lat`,`long`.

The configured `long` valid values are -180 to 360.
-180 to 0 is equivalent to 180E to 360E.
NOAA data uses 0E to 360E longitude values, this script does a best-effort to convert `lat` and `long` to equivalent NOAA longitudes.
Any coodinates that are not found are printed to console with the configured and converted values, and a negative value will be used in the notifications "Local 30 min Chance:" value.

Latitude and Longitude values can be converted and displayed at [the NGS Coordinate Conversion and Transformation Tool (NCAT)](https://www.ngs.noaa.gov/NCAT/).

## Running

To run Aurora-ntfy within Pipenv, run `pipenv run python3 aurora.py`.
If the dependencies are installed and managed using the system's Pip then the Pipenv isn't necessary, run the application using `python3 aurora.py`.

## Contributions

This project is open to contributions, ideas in Issues, bugfixes or suggested new features submitted through Pull Requests.

## Development

### Python

This is currently developed using Python 3.11.
To change the Python version used, run `pipenv --rm` to remove the relevant virtual environment, then change the python version in Pipfile, run `pipenv install`, and run the script as described in the "Running" section.

### Testing

So far, testing is done manually.
The notification is only sent when current NASA data is above target levels in the config file.
To have the notification sent consistantly, either set target levels to a low number or uncomment the `# or True:` in the script where `__main__` decides whether or not to `send_message(...)`.
