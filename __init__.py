from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from flask_login import LoginManager
from flask_mail import Mail


db = SQLAlchemy()
# Initialize Mail
mail = Mail() 


#function which will be called in create_app() to check for the existence of the database and create one if it does not exist
def check_and_create_db(app):
   database_uri = app.config['SQLALCHEMY_DATABASE_URI']
   # Extract database name from the URI
   db_name = database_uri.rsplit('/', 1)[-1]
   # URI to connect to the MySQL server without specifying a database
   base_uri = database_uri.rsplit('/', 1)[0]


   # Connect to the MySQL server
   engine = create_engine(base_uri)


   # Check if the database exists
   try:
       conn = engine.connect()
       conn.execute(text(f"USE {db_name}"))
       conn.close()
   except OperationalError:
       # Database does not exist, create it
       conn = engine.connect()
       conn.execute(text(f"CREATE DATABASE {db_name}"))
       conn.close()




#function which runs the app
def create_app():
   app=Flask(__name__)


   app.config['SECRET_KEY']='rbgoitg sirsgb'


   #the mysql database is located at the given URI location
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/rainforest_restoration'
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




   # Email configurations for Flask-Mail
   app.config['MAIL_SERVER'] = 'smtp.gmail.com'
   app.config['MAIL_PORT'] = 587
   app.config['MAIL_USE_TLS'] = True
   app.config['MAIL_USERNAME'] = 'restorationrainforest@gmail.com'
   app.config['MAIL_PASSWORD'] = 'password'
   app.config['MAIL_DEFAULT_SENDER'] = 'rainforestrestoration@gmail.com'


   # Initialize Flask-Mail
   mail.init_app(app)


   # Check and create the database if necessary
   check_and_create_db(app)


   db.init_app(app)


   from .models import student_service_members, service_supervisors, teacher
   login_manager = LoginManager()
   login_manager.login_view = 'auth.login'
   login_manager.init_app(app)


   @login_manager.user_loader
   def load_user(email):


       # Try to load the user from student_service_members
       user = student_service_members.query.filter_by(student_email=email).first()
       if user:
           return user
      
       # Try to load the user from service_supervisors
       user = service_supervisors.query.filter_by(supervisor_email=email).first()
       if user:
           return user
      
       # Try to load the user from teacher
       user = teacher.query.filter_by(teacher_email=email).first()
       if user:
           return user
      
       # If no user is found, return None
       return None
#import blueprints
   from .views import views
   from .auth import auth


   #register the blueprints with our flask application
   app.register_blueprint(views, url_prefix='/')
   app.register_blueprint(auth, url_prefix='/')




   return app
