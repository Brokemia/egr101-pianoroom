from flask import Flask, request
import json
app = Flask(__name__)

fname = 'test.json'

@app.route('/room<int:roomNo>')
def home(roomNo):
    with open(fname) as f:
        data = json.load(f)
        return f"Room {roomNo} is {'closed' if data[f'room{roomNo}'] else 'open'}"

@app.route('/data')
def get_data():
    roomNo = int(request.args.get('r'))
    full = bool(request.args.get('f'))
    with open(fname, 'w+') as f:
        try:
            data = json.load(f)
        except ValueError:
            data = {"room1":False,"room2":False,"room3":False,"room4":False}
        data[f'room{roomNo}'] = full
        json.dump(data, f)
    return "Data set"
