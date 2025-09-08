from flask import Flask
from routes import main_routes
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Register routes
app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
