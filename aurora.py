import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def load_config(filepath):
    config = None
    with open(filepath) as file:
        config = json.load(file)
    return config

def noaa_kp_json_3hr():
    kp_data_url = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
    r = requests.get(kp_data_url)
    kps = r.json()
    return kps[-1][1]


def noaa_kp_json_1m():
    kp_data_url = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
    r = requests.get(kp_data_url)
    kps = r.json()
    return kps[-1]['kp_index']


def noaa_kp_json_forecast(local_timezone):
    DATETIME = 0
    KP = 1
    OBSERVED = 2
    NOAA_SCALE = 3

    highest_kp = 0
    avg_kp = 0
    kps_to_avg = []
    kp_data_url = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
    r = requests.get(kp_data_url)
    kp_forecast = r.json()
    
    dt_now = datetime.now()
    dt_now = dt_now.replace(tzinfo=ZoneInfo(local_timezone))
    dt_evening = dt_now.replace(hour=16, minute=59, second=00, microsecond=00)
    td = timedelta(hours=15)
    dt_next_morning = dt_evening + td

    for data in kp_forecast:
        if data[DATETIME] == 'time_tag':
            continue
        dt_forecast = datetime.strptime(data[DATETIME],'%Y-%m-%d %H:%M:%S')
        dt_forecast = dt_forecast.replace(tzinfo=timezone.utc)
        kp_forecasted = float(data[KP])
        if dt_evening <= dt_forecast and dt_forecast <= dt_next_morning:
            highest_kp = kp_forecasted if kp_forecasted > highest_kp else highest_kp
            kps_to_avg.append(kp_forecasted)

    avg_kp = sum(kps_to_avg) / len(kps_to_avg)

    return avg_kp, highest_kp


def send_message(ntfy_url, ntfy_priority, kp_1m, kp_3hr, highest_forecast_kp, avg_forecast_kp, target_kp, thirty_min_chance):
    date_time_utc = datetime.now(timezone.utc)
    headers = {
        'Title': ('KP Above Target: %s' % (target_kp)),
        'Click': "https://www.swpc.noaa.gov/communities/aurora-dashboard-experimental#",
        'Attach': 'https://services.swpc.noaa.gov/experimental/images/aurora_dashboard/tonights_static_viewline_forecast.png',
        'Priority': str(ntfy_priority),
    }
    data = ('Time: %s UTC\nKP 1m: %s, Local 30min Chance: %s\nKP 3hr %s\nHighest Night KP: %s\nAvg Night KP: %s' %
            (date_time_utc.strftime("%Y-%m-%d %H:%M:%S"), kp_1m, thirty_min_chance, kp_3hr, highest_forecast_kp, avg_forecast_kp)).encode(encoding='utf-8')
    r = requests.post(ntfy_url, data=data, headers=headers)


def convert_coordinates(latitude, longitude):
    """
    Convert Coordinate System to valid numbers.
    """
    # Converts a Negative/West Longitude to East longitude to match NOAA data.
    longitude = int(longitude)
    while longitude < 0:
        longitude = 360 + longitude
    while longitude >= 360:
        longitude -= 360
    # Ensure Latitude is -90 to 90, which is 90S to 90N.
    latitude = int(latitude)
    while latitude > 90:
        latitude -= 90
    while latitude < -90:
        latitude += 90

    return latitude, longitude

def find_local_forecast(latitude, longitude, forecast_list):
    converted_latitude, converted_longitude = convert_coordinates(latitude, longitude)
    forecast_aurora = -1
    local_found = False
    for forecast in forecast_list:
        forecast_long = forecast[0]
        forecast_lat = forecast[1]
        if forecast_lat == converted_latitude and forecast_long == converted_longitude:
            forecast_aurora = forecast[2]
            local_found = True
    if not local_found:
        print(("Location %s, %s not found when converted to %s, %s.") % (latitude, longitude, converted_latitude, converted_longitude) )
    return forecast_aurora


def is_in_northern_hemisphere(forecast):
    return forecast[1] > 0


def is_in_southern_hemisphere(forecast):
    return forecast[1] < 0


def find_highest_forecast(forecast_list):
    highest = forecast_list[0]
    for forecast in forecast_list:
        if forecast[2] > highest[2] and is_in_northern_hemisphere(forecast):
            print(forecast)
            highest = forecast
    print(highest)


def get_30min_forecast(latitude, longitude):
    forecast_url = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
    r = requests.get(forecast_url)
    response_json = r.json()
    obs_time = response_json['Observation Time']
    forecast_time = response_json['Forecast Time']
    forecast_list = response_json['coordinates']

    percent_chance = find_local_forecast(latitude, longitude, forecast_list)
    #find_highest_forecast(forecast_list)
    return percent_chance


if __name__ == "__main__":
    config = load_config('./config.json')
    target_kp = config['target_kp']
    local_timezone = config['local_timezone']
    ntfy_url = config['ntfy_url']
    ntfy_priority = config['ntfy_priority']
    lat = config['lat']
    long = config['long']
    local_forecast_min =  config['thirty_min_forcast_min']

    thirty_min_chance = get_30min_forecast(lat, long)

    kp_3hr = noaa_kp_json_3hr()
    kp_1m = noaa_kp_json_1m()
    avg_forecast_kp, highest_forecast_kp = noaa_kp_json_forecast(local_timezone)
    if float(kp_3hr) > target_kp or float(kp_1m) > target_kp or avg_forecast_kp > target_kp or highest_forecast_kp > target_kp or int(thirty_min_chance) > int(local_forecast_min): # or True:
        send_message(ntfy_url, ntfy_priority, kp_1m, kp_3hr, highest_forecast_kp, avg_forecast_kp, target_kp, thirty_min_chance)

