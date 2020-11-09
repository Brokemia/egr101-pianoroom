from requests.api import request
from gpiozero import RGBLED, Button, DistanceSensor, LED
from colorzero import Color
from time import sleep
import requests, os, sys

ROOM_NUM = 1

SENSE_DELAY_SECS = 120 #Seconds to delay after sensing before going inactive
DISTANCE_RESET_SECS = 1 * 3600 #Seconds of no pir activity that will reset distance sensor
DEFAULT_MAXIMUM_METERS = 1 #Distance in meters
PROGRAM_HZ = 30 #update speed of program

# PINS
JAM_BUTTON_PIN = 16
JAM_LED_PIN = 18
PIR_PIN = 20
DISTANCE_ECHO_PIN = 25
DISTANCE_TRIGGER_PIN = 8
RED_PIN = 2
BLUE_PIN = 3
GREEN_PIN = 4

#URLs for data
ROOT_URL = 'http://54.147.192.125'
if "-local" in sys.argv:
    ROOT_URL = 'http://localhost:5000'
FALSE_ROOM_URL = "/roomdata?r={}&f=0".format(ROOM_NUM)
TRUE_ROOM_URL  = "/roomdata?r={}&f=1".format(ROOM_NUM)
FALSE_JAM_URL  = "/jamdata?r={}&j=0".format(ROOM_NUM)
TRUE_JAM_URL   = "/jamdata?r={}&j=1".format(ROOM_NUM)

# Sensor and output setup
pir_sensor = Button(PIR_PIN, True)
distance_sensor = DistanceSensor(echo=DISTANCE_ECHO_PIN, trigger=DISTANCE_TRIGGER_PIN, max_distance=3)
rgb_led = RGBLED(RED_PIN, BLUE_PIN, GREEN_PIN)
rgb_led.off()
jam_led = LED(JAM_LED_PIN)
jam_led.off()
jam_button = Button(JAM_BUTTON_PIN, True)

# Waits for network connection and valid http requests from the ROOT_URL
def network_wait():
    print("network error!")
    while True:
        # Check if pinging google works
        ping_result = requests.get("http://google.com")
        # If it worked, test http request
        if ping_result.status_code < 300:
            # Try the request, and if it works and has a good status code, exit the function
            try:
                r = requests.get(ROOT_URL)
                if r.status_code < 300:
                    print("\nnetwork online!")
                    return
                else:
                    # If status code is bad print and continue
                    print("bad status code...")
            except:
                # If request errors print and continue
                print("request not received...")
        # If it didn't, print and check again
        else:
            print("ping to google not working, likely no internet connection...")
        
        # Set LED to yellow and wait to match PROGRAM_HZ
        rgb_led.color = Color('yellow')
        sleep(PROGRAM_HZ/1000)

# Sent a http request to the given url, checking for any network errors
def send_http(url):
    # Check pinging google, if any issues go to network_wait
    ping_result = requests.get("http://google.com")
    if ping_result.status_code >= 300: network_wait()
    # perform http request using requests, if any errors go to network wait and try again once it exits
    print("sending url: " + url)
    try:
        r = requests.get(url)
        if r.status_code >= 300: 
            network_wait()
            r = requests.get(url)
    except:
        network_wait()
        r = requests.get(url)
    print("url sent!\n")
    

# VARIABLE BOUNDING
time_total = 0
person_detected = False
person_present = False
person_was_present = False
jam_pressed = False
jam_was_pressed = False
jam_on = False
jam_was_on = False
pir_not_detected_time = 0
max_meters = DEFAULT_MAXIMUM_METERS

def main_work():
    # set vars global
    global time_total
    global person_detected
    global person_present
    global person_was_present
    global jam_pressed
    global jam_was_pressed
    global jam_on
    global jam_was_on
    global pir_not_detected_time
    global max_meters

    # -----------------PERSON DETECTION-----------------
    # If pir or distance sensor tripped, person_detected is True
    person_detected = False
    if pir_sensor.is_pressed:
        person_detected = True
        pir_not_detected_time = 0
    else:
        # If pir off for more than DISTANCE_RESET_SECS, reset the maximum distance for the distance sensor
        if pir_not_detected_time > DISTANCE_RESET_SECS*1000:
            # max_meters = distance_sensor.distance()
            pir_not_detected_time = 0
        else:
            pir_not_detected_time += PROGRAM_HZ

    # if distance_sensor.distance() <= max_meters:
        # person_detected = True

    # If a person is detected, set person_present to True
    if person_detected:
        person_present = True
        time_total = 0
    # If a person is not detected, wait until SENSE_DELAY_SECS and then set person_present to False
    else:
        if time_total > SENSE_DELAY_SECS * 1000:
            person_present = False
        else:
            time_total += PROGRAM_HZ

    # If person_present is different than person_was_present, the status has changed
    # Send a HTTP request in this case
    if person_present != person_was_present:
        print("person change detected!")
        request_url = ROOT_URL
        if person_present:
            print("person on now")
            request_url += TRUE_ROOM_URL
        else:
            print("person off now")
            request_url += FALSE_ROOM_URL
        
        send_http(request_url)

    person_was_present = person_present

    # -----------------JAM BUTTON-----------------
    # If there is not a person present, set jam_on to False
    if not person_present:
        jam_on = False
    else:
        # If the button state is True and was not True, set jam_on to whatever it is not
        jam_pressed = jam_button.is_pressed
        if jam_pressed and not jam_was_pressed:
            jam_on = not jam_on
        jam_was_pressed = jam_pressed

    # If jam_on state has changed, send HTTP request
    if jam_on != jam_was_on:
        print("jam change detected!")
        jam_led.toggle()
        request_url = ROOT_URL
        if jam_on:
            print("jam on now")
            request_url += TRUE_JAM_URL
        else:
            print("jam off now")
            request_url += FALSE_JAM_URL
        
        send_http(request_url)

    jam_was_on = jam_on

    # Set LED to green and sleep for PROGRAM_HZ time
    rgb_led.color = Color('green')
    sleep(PROGRAM_HZ/1000)

def testing():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(str(pir_sensor.value))
    # print(str(distance_sensor.distance))
    if distance_sensor.distance <= DEFAULT_MAXIMUM_METERS:
        print("Distance!")
    else:
        print("no distance")
    print(str(jam_button.value))
    rgb_led.color = Color('green')
    rgb_led.on()
    jam_led.on()
    sleep(PROGRAM_HZ/1000)


# Runs the code in normal mode if testing flag is present, otherwise sets led to red if any errors
if sys.argv[1] == "-testing":
    while True: testing()
# network_wait()
if sys.argv[1] == "-v":
    print("starting")
    while True: main_work()
else:
    while True:
        try:
            main_work()
        except:
            rgb_led.color = Color('red')
            print("Error has ocurred in main loop!")
