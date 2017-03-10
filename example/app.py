from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)


@app.route('/')
def index():
    now = datetime.utcnow()
    midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    epoch = datetime(1970, 1, 1, 0, 0, 0)
    return render_template('index.html', now=now, midnight=midnight,
                           epoch=epoch)


@app.route('/ajax')
def ajax():
    return jsonify({'timestamp': moment.create(datetime.utcnow()).format(
        'LLLL')})


if __name__ == '__main__':
    app.run(debug=True)
