from flask import Flask, request, render_template
import json
import time
app = Flask(__name__)

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
    with open(fname) as f:
        try:
            data = json.load(f)
        except ValueError:
            data = {"room1":False,"room2":False,"room3":False,"room4":False}
    data[f'room{roomNo}'] = full

    rooms = ["1", "2", "3", "4"]
    for roomNum in rooms:
        if data["room" + roomNum] == True:
            data["time" + roomNum] = 'In Use'
            data["timeStamp" + roomNum] = 0.0
            print('in use' + roomNum)
        elif data["room" + roomNum] == False:
            timeSince = "00:00:00"
            print("timestamp before if statements" + roomNum, time.time())
            print(data["timeStamp" + roomNum])
            if data["timeStamp" + roomNum] > 0.0:
                recordedTime = data["timeStamp" + roomNum]
                print("if statement" + roomNum, recordedTime)
                timeDiff = int(time.time() - recordedTime)
                timeSince = str(time.strftime('%H:%M:%S', time.gmtime(
                    timeDiff)))
            else:
                timeSince = "00:00:00"
                data["timeStamp" + roomNum] = time.time()
                print("time stamp in else statement" + roomNum,
                      data["timeStamp" +
                           roomNum])
            data["time" + roomNum] = timeSince

    with open(fname, 'w') as f:
        json.dump(data, f)
    return "Data set"

@app.route('/')
def home():
    with open(fname) as f:
        data = json.load(f)
    rooms = ["1", "2", "3", "4"]
    for roomNum in rooms:
        if data["room" + roomNum] == True:
            data["time" + roomNum] = 'In Use'
            data["timeStamp" + roomNum] = 0.0
            print('in use' + roomNum)
        elif data["room" + roomNum] == False:
            timeSince = "00:00:00"
            print("timestamp before if statements" + roomNum, time.time())
            print(data["timeStamp" + roomNum])
            if data["timeStamp" + roomNum] > 0.0:
                recordedTime = data["timeStamp" + roomNum]
                print("if statement" + roomNum, recordedTime)
                timeDiff = int(time.time() - recordedTime)
                timeSince = str(time.strftime('%H:%M:%S', time.gmtime(
                    timeDiff)))
            else:
                timeSince = "00:00:00"
                data["timeStamp" + roomNum] = time.time()
                print("time stamp in else statement" + roomNum,
                      data["timeStamp" +
                           roomNum])
            data["time" + roomNum] = timeSince
    return render_template('index.html', room1=data['room1'], room2=data['room2'], room3=data['room3'], room4=data['room4'], time1=data["time1"],
                               time2=data['time2'], time3=data[
                                'time3'], time4=data['time4'])


if __name__ == '__main__':
    print(time.time())
    app.run()