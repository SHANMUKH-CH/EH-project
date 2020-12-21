import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
app= Flask(__name__)

##db connection
basedir = os.path.dirname(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
#Migrate(app,db)

#login configurations
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='users.login'



from SOCIAL_BLOG.core.views import core
from SOCIAL_BLOG.users.views import users
from SOCIAL_BLOG.error_pages.handlers import error_pages

app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(error_pages)