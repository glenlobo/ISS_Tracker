import json
import smtplib
import time
from datetime import datetime
import requests

LATITUDE = 12.971599
LONGITUDE = 77.594566

with open("config.json", "r")as config_file:
    config_data = json.loads(config_file.read())
    my_email = config_data["my_email"]
    password = config_data["password"]
    to_email = config_data["to_email"]


def get_iss_location():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    print(f"{iss_latitude =}")
    print(f"{iss_longitude =}")

    return iss_latitude, iss_longitude


def is_close(iss_lat, iss_lng, lat, lng):
    if lat - 5 <= iss_lat <= lat + 5 and lng - 5 <= iss_lng <= lng + 5:
        return True


def is_dark(lat, lng):
    parameters = {
        "lat": lat,
        "lng": lng,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()

    sunrise = int(data["results"]["sunrise"].split('T')[1].split(':')[0])+5.5
    sunset = int(data["results"]["sunset"].split('T')[1].split(':')[0])+5.5
    current_time = datetime.now().hour
    print(f'{sunrise =}')
    print(f'{sunset =}')
    print(f'{current_time =}')

    if sunset <= current_time or current_time <= sunrise:
        return True
    return False


def send_email():
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(
            from_addr=my_email,
            to_addrs=to_email,
            msg=f"Subject: ISS Visible \n\n {'ISS Visible at your area'}"
        )
        print('email sent')


while True:
    latitude, longitude = get_iss_location()
    if is_dark(lat=LATITUDE, lng=LONGITUDE) and is_close(iss_lat=latitude, iss_lng=longitude,
                                                         lat=LATITUDE, lng=LONGITUDE):
        send_email()
    time.sleep(60)

