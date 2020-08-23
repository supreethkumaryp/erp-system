from datetime import timedelta
from flask import Flask, render_template, send_from_directory, url_for, redirect, session
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, login_required
from flask_dropzone import Dropzone
from config import BASE_DIR
import os
from .gst import GST


# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Applying Bootstrap to App
Bootstrap(app)

# Creating Mongo Client
db = MongoEngine(app)

# Creating Bcrypt var
bcrypt = Bcrypt(app)

# Create JWT Manager
jwt = JWTManager(app)

# Creating LoginManager
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = '/auth/sign-in/'

# Applying CORS to APP
CORS(app)

# Creating GST Object
gst = GST()

# Creating Dropzone Object
dropzone = Dropzone(app)

# app.config.update(
#     UPLOADED_PATH=os.path.join(BASE_DIR, 'app/static/assets/images/products'),
#     # Flask-Dropzone config:
#     DROPZONE_ALLOWED_FILE_TYPE='image',
#     DROPZONE_MAX_FILE_SIZE=3,
#     DROPZONE_MAX_FILES=30,
#     DROPZONE_IN_FORM=True,
#     DROPZONE_UPLOAD_ON_CLICK=True,
#     DROPZONE_UPLOAD_ACTION='/',  # URL or endpoint
#     DROPZONE_UPLOAD_BTN_ID='submit'
# )

# @app.template_filter()
# def check_rights(val1, val2):
#     return (True if val1 & val2 else False)

# Session Timeout
# @app.before_request
# def make_session_permanent():
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(minutes=60)

# # Sample HTTP error handling
# @app.errorhandler(400)
# def error_400(error):
#     return render_template('error/error-400.html'), 400

# @app.errorhandler(401)
# def error_401(error):
#     return render_template('error/error-401.html'), 401

# @app.errorhandler(403)
# def error_403(error):
#     return render_template('error/error-403.html'), 403

# @app.errorhandler(404)
# def error_404(error):
#     return render_template('error/error-404.html'), 404

# @app.errorhandler(500)
# def error_500(error):
#     return render_template('error/error-500.html'), 500

# Adding favicon to webpage
# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static/assets/images'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

# @app.route("/")
# @login_required
# def index():
#     return redirect(url_for("dashboard.index"))
    
# Import a module / component using its blueprint handler variable
# from app.api.controllers import api as api
# from app.auth.controllers import auth as auth
# from app.dashboard.controllers import dashboard as dashboard
# from app.dashboard.general.controllers import general as general
# from app.dashboard.masters.controllers import masters as masters

# # Register blueprint(s)
# app.register_blueprint(api)
# app.register_blueprint(auth)
# app.register_blueprint(dashboard)
# app.register_blueprint(general)
# app.register_blueprint(masters)


# # Init Application
# from app import initapp