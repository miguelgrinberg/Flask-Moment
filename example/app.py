from datetime import datetime
from flask import Flask, render_template
from flask.ext.moment import Moment

app = Flask(__name__)
moment = Moment(app)

@app.route('/')
def index():
    now = datetime.utcnow()
    midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    return render_template('index.html', now = now, midnight = midnight)

if __name__ == '__main__':
    app.run(debug = True)
