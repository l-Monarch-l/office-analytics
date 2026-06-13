from flask import Flask, render_template
from web.routes import api
from web.models import engine
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.routes import api
app = Flask(__name__)
app.register_blueprint(api)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)