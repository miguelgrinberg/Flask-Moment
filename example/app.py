from datetime import datetime
from flask import Flask, render_template, jsonify
from flask.ext.moment import Moment

app = Flask(__name__)
moment = Moment(app)

@app.route('/')
def index():
    now = datetime.utcnow()
    midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    return render_template('index.html', now = now, midnight = midnight)

@app.route('/ajax')
def ajax():
    return jsonify({ 'timestamp': moment.create(datetime.utcnow()).format('LLLL') });
 
if __name__ == '__main__':
    app.run(debug = True)
