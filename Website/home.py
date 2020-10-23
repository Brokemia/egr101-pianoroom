from flask import Flask, request, render_template
import json

UPLOAD_FOLDER = 'static/images/'

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
            data = {"room1":False,"room2":False,"room3":False,"room4":False}
    data[f'room{roomNo}'] = full
    with open(fname, 'w') as f:
        json.dump(data, f)
    return "Data set"

@app.route('/')
def home():
    with open(fname) as f:
        data = json.load(f)
        return render_template('index.html', room1=data['room1'], room2=data['room2'], room3=data['room3'], room4=data['room4'])

if __name__ == '__main__':
    app.run()
