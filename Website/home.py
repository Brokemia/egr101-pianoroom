from flask import Flask, request, render_template, redirect, url_for, Response
from validate_email import validate_email
import json
import time
import datetime as dt
import _thread, threading
import math
import secEmailsys

import queue

# https://maxhalford.github.io/blog/flask-sse-no-deps/
class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        return q

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

announcer = MessageAnnouncer()
UPLOAD_FOLDER = 'templates/images/'

app = Flask(__name__)

app.secret_key = "thissuredobeademderesecretkey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

fname = 'occupancy.json'

def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

@app.route('/listen', methods=['GET'])
def listen():

    def stream():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    return Response(stream(), mimetype='text/event-stream')

@app.route('/room<int:roomNo>')
def room(roomNo):
    with open(fname) as f:
        data = json.load(f)
        return f"Room {roomNo} is {'closed' if data[f'room{roomNo}'] else 'open'}"

#http://127.0.0.1/roomdata?r=1&f=1  Update Page Data
@app.route('/roomdata')
def get_room_data():
    roomNo = int(request.args.get('r'))
    full = bool(int(request.args.get('f')))
    with threadLock:
        try:
            with open(fname) as f:
                data = json.load(f)
        except (ValueError,FileNotFoundError):
            currTime = time.time()
            chartData = []
            for i in range(54):
                chartData.append([])
                for j in range(7):
                    chartData[i].append([0,0,0,0,0,0,0,0,0,0,0,0])
            data = {"room1":False,"room2":False,"room3":False,"room4":False,"time1":currTime,"time2":currTime,"time3":currTime,"time4":currTime,"jam1": 0,
                    "jam2": 0, "jam3": 0, "jam4": 0, "recent1": False,
                    "recent2": False, "recent3": False, "recent4": False,"chartData":chartData}
        
        update_timing(data)
                
        data[f'room{roomNo}'] = full
        
        if not(full):
            data[f'jam{roomNo}'] = 0
            data[f'recent{roomNo}'] = True
                              
        with open(fname, 'w') as f:
            json.dump(data, f)
            
        prepareDataForDisplay(data)

        msg = format_sse(data=str({'room1':data['room1'],'room2':data['room2'],'room3':data['room3'],'room4':data['room4'],
                            'time1':data['time1'],'time2':data['time2'],'time3':data['time3'],'time4':data['time4'],
                            'jam1':data['jam1'],'jam2':data['jam2'],'jam3':data['jam3'],'jam4':data['jam4']}))
        announcer.announce(msg=msg)

        return "Room Availability Data set"

#http://127.0.0.1:5000/jamdata?r=1&j=1  Update Jam Data
@app.route('/jamdata')
def get_jam_data():
    roomNo = int(request.args.get('r'))
    jam = int(request.args.get('j'))
    with open(fname) as f:
        try:
            data = json.load(f)
        except ValueError:
            currTime = time.time()
            data = {"room1": False, "room2": False, "room3": False,
                    "room4": False, "time1": currTime, "time2": currTime,
                    "time3": currTime, "time4": currTime, "jam1": 0,
                    "jam2": 0, "jam3": 0, "jam4": 0, "recent1": False,
                    "recent2": False, "recent3": False, "recent4": False}

    if data[f'room{roomNo}']:
        data[f'jam{roomNo}'] = jam

    with open(fname, 'w') as f:
        json.dump(data, f)

    prepareDataForDisplay(data)

    msg = format_sse(data=str({'room1':data['room1'],'room2':data['room2'],'room3':data['room3'],'room4':data['room4'],
                            'time1':data['time1'],'time2':data['time2'],'time3':data['time3'],'time4':data['time4'],
                            'jam1':data['jam1'],'jam2':data['jam2'],'jam3':data['jam3'],'jam4':data['jam4']}))
    announcer.announce(msg=msg)

    return "Jam Data set"

@app.route('/result', methods = ['POST', 'GET'])
def writeEmail():
    if request.method == 'POST':
        email = request.form['emails']

        if validate_email(email, verify=True):
            f = open("emailstext", "a")
            write = email + "\n"
            f.write(write)
            f.close()
    else:
        print("Error No Input Dectected")

    return redirect("/", code=301)

def prepareDataForDisplay(data):
    for roomNo in range(1,5):
        if data[f'room{roomNo}']:
            data[f'room{roomNo}'] = 'Full'
            data[f'time{roomNo}'] = 'In Use'
        else:
            data[f'room{roomNo}'] = 'Available'
            recordedTime = data[f'time{roomNo}']
            timeDiff = int(time.time() - recordedTime)
            strTime = str(time.strftime('%Y:%m:%d:%H:%M:%S',
                                                      time.gmtime(timeDiff)))
            data[f'time{roomNo}'] = ""
            strTimeList = strTime.split(":")
            days = 0
            counter = 0
            limit = 2
            if int(strTimeList[0]) > 1970:
                days += (int(strTimeList[0]) - 1970) * 365
            if int(strTimeList[1]) > 1:
                days += (int(strTimeList[1]) - 1) * 30
            if int(strTimeList[2]) > 1:
                days += (int(strTimeList[2]) - 1)
            if days > 0 and counter < limit:
                data[f'time{roomNo}'] += str(days) + "d "
                counter += 1
            if int(strTimeList[3]) > 0 and counter < limit:
                data[f'time{roomNo}'] += strTimeList[3] + "h "
                counter += 1
            if int(strTimeList[4]) > 0 and counter < limit:
                data[f'time{roomNo}'] += strTimeList[4] + "m "
                counter += 1
            if int(strTimeList[5]) > 0 and counter < limit:
                data[f'time{roomNo}'] += strTimeList[5] + "s"
                counter += 1

    averages = []
    chart = data['chartData']
    
    roomsSurveyed = 0

    for i in range(7):
        averages.append([0,0,0,0,0,0,0,0,0,0,0,0])
    for i in range(len(chart)):
        # If the week contains any non-zero values
        any = False
        for j in range(len(chart[i])):
            for k in range(len(chart[i][j])):
                if chart[i][j][k] != 0:
                    any = True
                    break
        if any:
            roomsSurveyed += 1
            for j in range(len(averages)):
                for k in range(len(averages[j])):
                    averages[j][k] += chart[i][j][k]
             
    for j in range(len(averages)):
        for k in range(len(averages[j])):
            averages[j][k] /= 288 * roomsSurveyed;
    
    data['chartData'] = averages

@app.route('/mobile')
def homeMobile():
    return home(True)
                           
@app.route('/')
def homeDefault():
    return home(False)

def home(forceMobile):
    with open(fname) as f:
        data = json.load(f)

    prepareDataForDisplay(data)

    return render_template('index.html', forceMobile=str(forceMobile).lower(), room1=data['room1'], room2=data['room2'], room3=data['room3'], room4=data['room4'],
                                time1=data["time1"], time2=data['time2'], time3=data['time3'], time4=data['time4'],jamStat1= data["jam1"], jamStat2= data["jam2"],
                           jamStat3= data["jam3"], jamStat4= data["jam4"], chartData=data['chartData'])

@app.route('/images/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='images/' + filename), code=301)
    
@app.route('/styles/<filename>')
def get_style(filename):
    return redirect(url_for('static', filename='styles/' + filename), code=301)
    
@app.route('/scripts/<filename>')
def get_script(filename):
    return redirect(url_for('static', filename='scripts/' + filename), code=301)

threadLock = threading.Lock()

def update():
    while True:
        with threadLock:
            with open(fname) as f:
                data = json.load(f)
                update_timing(data)

            for ro in range(1, 5):
                if data[f'recent{ro}'] and (int(time.time() - data[f'time{ro}'])>= 600):
                    secEmailsys.send_mail()
                    data[f'recent{ro}'] = False
                    open('emailstext', 'w').close()
                elif data[f'recent{ro}'] and (int(time.time() - data[f'time{ro}'])>= 1000):
                    data[f'recent{ro}'] = False

            with open(fname, 'w') as f:
                json.dump(data, f)
        time.sleep(60)
            
                
def update_timing(data):
    now = dt.datetime.now()
    for i in range(1, 5):
        if data[f'room{i}']:
            # Check how long since the last update
            diff = time.time() - data[f'time{i}']
            week = int(now.strftime("%W"))
            lastHour = now.replace(second=0, microsecond=0, minute=0, hour=(now.hour//2)*2)

            data["chartData"][week][now.weekday()][now.hour // 2] += min(time.time() - data[f'time{i}'], time.time() - lastHour.timestamp())

            # Reset the next week, so it doesn't add up over multiple years
            if week < len(data['chartData'])-1:
                for j in range(len(data["chartData"][week+1])):
                    data['chartData'][week+1][j] = [0,0,0,0,0,0,0,0,0,0,0,0]
            else:
                for j in range(len(data["chartData"][0])):
                    data['chartData'][0][j] = [0,0,0,0,0,0,0,0,0,0,0,0]

            data[f'time{i}'] = time.time()

if __name__ == '__main__':
    try:
        _thread.start_new_thread(update,())
    except:
        print("Error: unable to start thread")
    app.run(host='0.0.0.0', port=80)
