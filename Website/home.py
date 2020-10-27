from flask import Flask, request, render_template, redirect, url_for
import json
import time

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
    with open(fname) as f:
        try:
            data = json.load(f)
        except ValueError:
            currTime = time.time()
            data = {"room1":False,"room2":False,"room3":False,"room4":False,"time1":currTime,"time2":currTime,"time3":currTime,"time4":currTime}
            
    if data[f'room{roomNo}'] and not(full):
        data[f'time{roomNo}'] = time.time()
            
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
    return render_template('index.html', room1=data['room1'], room2=data['room2'], room3=data['room3'], room4=data['room4'],
                                time1=data["time1"], time2=data['time2'], time3=data['time3'], time4=data['time4'])

@app.route('/images/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='images/' + filename), code=301)
    
@app.route('/styles/<filename>')
def get_style(filename):
    return redirect(url_for('static', filename='styles/' + filename), code=301)
    
@app.route('/scripts/<filename>')
def get_script(filename):
    return redirect(url_for('static', filename='scripts/' + filename), code=301)

if __name__ == '__main__':
    print(time.time())
    app.run()
