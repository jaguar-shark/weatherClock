#!/usr/bin/python3

from __future__ import print_function
import os
import json
import requests
from flask import jsonify
from tkinter import *
import time
import datetime
import PIL
from PIL import Image
from PIL import ImageTk
import board

# import adafruit_dotstar as dotstar
# import RPi.GPIO as GPIO

NUM_PIXELS = 60
YELLOW = (255, 150, 0)
WEATHER_API_TOKEN = "a35abf413dc7eaa8ed68670297040e50"
WEATHER_API_URL = "https://api.darksky.net/forecast/"
GEOLOCATOR_URL = "https://freegeoip.app/json/"

icon_lookup = {
    "clear-day": "assets/Sun.png",
    "wind": "assets/Wind.png",
    "cloudy": "assets/Cloud.png",
    "partly-cloudy-day": "assets/PartlySunny.png",
    "rain": "assets/Rain.png",
    "snow": "assets/Snow.png",
    "snow-thin": "assets/Snow.png",
    "fog": "assets/Haze.png",
    "clear-night": "assets/Moon.png",
    "partly-cloudy-night": "assets/PartlyMoon.png",
    "thunderstorm": "assets/Storm.png",
    "tornado": "assests/Tornado.png",
    "hail": "assests/Hail.png",
}


class Window:
    def __init__(self):
        self.tk = Tk()
        self.tk.title("Gleen")
        self.tk.configure(background="black")
        # self.tk.attributes('-fullscreen', True)
        self.state = False
        self.tk.config(cursor="none")
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.topFrame = Frame(self.tk, background="black")
        self.topFrame.pack(fill=BOTH, expand=YES)
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor="center", padx=20, fill=X, expand=True)
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor="center", padx=20, fill=X, expand=True)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"


class Weather(Frame):
    def __init__(self, parent={}, *args, **kwargs):
        Frame.__init__(self, parent, bg="black")
        self.icon = ""
        self.forecast = ""
        self.temp = ""
        self.cloud_condition = ""
        self.minutely = ""
        self.wind_avg = ""
        self.callTotal = 0
        # Degree frame for left side of screen
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=LEFT, anchor=W, pady=100)
        # Icon fram for center of the screen
        self.iconFrm = Frame(self, bg="black")
        self.iconFrm.pack(side=LEFT, anchor=E, padx=20)
        # temperature:
        self.temperatureLbl = Label(
            self.degreeFrm, font=("Helvetica", 65), fg="white", bg="black"
        )
        self.temperatureLbl.pack(side=TOP, anchor=N + W)
        # currently:
        self.currentlyLbl = Label(
            self.degreeFrm, font=("Helvetica", 35), fg="white", bg="black"
        )
        self.currentlyLbl.pack(side=BOTTOM, pady=20, anchor=W)
        # weather icon:
        self.iconLbl = Label(self.iconFrm, bg="black")
        self.iconLbl.pack(side=RIGHT, anchor=E, ipadx=20)
        # call get_weather method:
        self.get_weather()

    def get_weather(self):
        self.callTotal = self.callTotal + 1
        print("API call #" + str(self.callTotal))

        lat, lon = self.get_location()
        request_url = WEATHER_API_URL + WEATHER_API_TOKEN + "/" + lat + "," + lon
        resp = requests.get(request_url)
        data = json.loads(resp.text)
        print(json.dumps(data["currently"], indent=4, sort_keys=True))
        curr_temp = (
            str(int(data["currently"]["apparentTemperature"])) + "\N{DEGREE SIGN}"
        )
        curr_cloud_condition = data["currently"]["summary"]

        wind_list = []
        running_sum = 0
        for d in data["hourly"]["data"]:
            wind_list.append(d["windSpeed"])
            running_sum = running_sum + d["windSpeed"]

        curr_wind_avg = running_sum / len(wind_list)
        curr_forecast = data["hourly"]["summary"]
        curr_minutely = data["minutely"]["summary"]
        curr_icon = data["currently"]["icon"]

        if curr_temp != self.temp:
            self.temp = curr_temp
            self.temperatureLbl.config(text=curr_temp)
        if curr_cloud_condition != self.cloud_condition:
            self.cloud_condition = curr_cloud_condition
            self.currentlyLbl.config(text=curr_cloud_condition)
        if curr_forecast != self.forecast:
            self.forecast = curr_forecast
        if curr_minutely != self.minutely:
            self.minutely = curr_minutely
        # if curr_wind_avg != self.wind_avg:
        #     self.wind_avg = curr_wind_avg

        weather_icon = None
        if curr_icon in icon_lookup:
            weather_icon = icon_lookup[curr_icon]

        if weather_icon is not None:
            self.icon = weather_icon
            image = Image.open(weather_icon)
            image = image.resize((200, 200), Image.ANTIALIAS)
            image = image.convert("RGB")
            photo = ImageTk.PhotoImage(image)
            self.iconLbl.config(image=photo)
            self.iconLbl.image = photo
        else:
            self.iconLbl.config(image="")

        self.after(60000, self.get_weather)

    def get_location(self):
        headers = {"accept": "application/json", "content-type": "application/json"}
        r = requests.request("GET", GEOLOCATOR_URL, headers=headers)
        j = json.loads(r.text)
        latitude = str(j["latitude"])
        longitude = str(j["longitude"])

        return latitude, longitude


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg="black")
        self.time = ""
        self.time_label = Label(self, font=("Helvetica", 55), fg="white", bg="black")
        self.time_label.pack(side=TOP, anchor=E)

        self.day_of_week = ""
        self.day_label = Label(
            self, text=self.day_of_week, font=("Helvetica", 25), fg="white", bg="black"
        )
        self.day_label.pack(side=TOP, anchor=E)

        self.date = ""
        self.date_label = Label(
            self, text=self.date, font=("Helvetica", 25), fg="white", bg="black"
        )
        self.date_label.pack(side=TOP, anchor=E)
        self.update()

    def update(self):
        curr_time = time.strftime("%I:%M %p")
        curr_day_of_week = time.strftime("%A")
        curr_date = time.strftime("%b %d, %Y")

        if curr_time != self.time:
            self.time = curr_time
        if curr_day_of_week != self.day_of_week:
            self.day_of_week = curr_day_of_week
        if curr_date != self.date:
            self.date = curr_date

        self.time_label.config(text=self.time)
        self.day_label.config(text=self.day_of_week)
        self.date_label.config(text=self.date)
        self.time_label.after(200, self.update)


def titlePrint():
    print("\n\n")
    print("*********************************************")
    print("\n")
    print("                Gleen Clock                  ")
    print("      By Dalton Ryan and James Schulman      ")
    print("                   2019                      ")
    print("            Powered by Dark Sky              ")
    print("\n")
    print("*********************************************")
    print("\n\n")


def main():
    titlePrint()
    w = Window()
    # we = Weather()
    # we.get_weather()
    w.tk.mainloop()


if __name__ == "__main__":
    main()
