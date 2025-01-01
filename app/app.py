import os

from flask import Flask
#from dotenv import load_dotenv
#load_dotenv()

from utils import s3helper
from blueprints.api import bl_api
from blueprints.front import bl_front

# build storage
s3helper.build()

# app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

# blueprints
app.register_blueprint(bl_front, url_prefix="/")
app.register_blueprint(bl_api, url_prefix="/api/")

# run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=False)
