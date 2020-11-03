from flask import Flask, request, render_template, redirect, url_for
import json
import time
import datetime as dt
import _thread, threading
import math

UPLOAD_FOLDER = 'templates/images/'

app = Flask(__name__)

app.secret_key = "thissuredobeademderesecretkey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

fname = 'occupancy.json'

@app.route('/room<int:roomNo>')
def room(roomNo):
    with open(fname) as f:
        data = json.load(f)
        return f"Room {roomNo} is {'closed' if data[f'room{roomNo}'] else 'open'}"

@app.route('/data')
def get_data():
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
            data = {"room1":False,"room2":False,"room3":False,"room4":False,"time1":currTime,"time2":currTime,"time3":currTime,"time4":currTime,"chartData":chartData}
        
        update_timing(data)
                
        data[f'room{roomNo}'] = full
                              
        with open(fname, 'w') as f:
            json.dump(data, f)
    return "Data set"

@app.route('/')
def home():
    with open(fname) as f:
        data = json.load(f)
    for roomNo in range(1,5):
        if data[f'room{roomNo}']:
            data[f'time{roomNo}'] = 'In Use'
        else:
            recordedTime = data[f'time{roomNo}']
            timeDiff = int(time.time() - recordedTime)
            data[f'time{roomNo}'] = str(time.strftime('%H:%M:%S', time.gmtime(timeDiff)))
        averages = []
        chart = data['chartData']
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
                for j in range(len(averages)):
                    for k in range(len(averages[j])):
                        averages[j][k] += chart[i][j][k]
    return render_template('index.html', room1=data['room1'], room2=data['room2'], room3=data['room3'], room4=data['room4'],
                                time1=data["time1"], time2=data['time2'], time3=data['time3'], time4=data['time4'], chartData=averages)

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
            
            data["chartData"][week][now.weekday()][now.hour // 2] += min(time.time() - data[f'time{i}'], 3600)

            data[f'time{i}'] = time.time()

if __name__ == '__main__':
    try:
        _thread.start_new_thread(update,())
    except:
        print("Error: unable to start thread")
    app.run(host='0.0.0.0', port=80)
