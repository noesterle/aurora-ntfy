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


def send_message(ntfy_url, ntfy_priority, kp_1m, kp_3hr, highest_forecast_kp, avg_forecast_kp, target_kp):
    headers = {
        'Title': ('KP Above Target: %s' % (target_kp)),
        'Click': "https://www.swpc.noaa.gov/communities/aurora-dashboard-experimental#",
        'Attach': 'https://services.swpc.noaa.gov/experimental/images/aurora_dashboard/tonights_static_viewline_forecast.png',
        'Priority': str(ntfy_priority),
    }
    data = ('KP 1m: %s\nKP 3hr %s\nHighest Night KP: %s\nAvg Night KP: %s' % (kp_1m,  kp_3hr, highest_forecast_kp, avg_forecast_kp)).encode(encoding='utf-8')
    r = requests.post(ntfy_url, data=data, headers=headers)


if __name__ == "__main__":
    config = load_config('./config.json')
    target_kp = config['target_kp']
    local_timezone = config['local_timezone']
    ntfy_url = config['ntfy_url']
    ntfy_priority = config['ntfy_priority']

    kp_3hr = noaa_kp_json_3hr()
    kp_1m = noaa_kp_json_1m()
    avg_forecast_kp, highest_forecast_kp = noaa_kp_json_forecast(local_timezone)
    if float(kp_3hr) > target_kp or float(kp_1m) > target_kp or avg_forecast_kp > target_kp or highest_forecast_kp > target_kp: # or True:
        send_message(ntfy_url, ntfy_priority, kp_1m, kp_3hr, highest_forecast_kp, avg_forecast_kp, target_kp)
