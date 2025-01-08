from . import db
from flask_login import UserMixin
from sqlalchemy import Numeric
#later on func will allow us to automatically set datetime for anything if we need it with default=func.now() as one of the parameters in db.Column()
#from sqlalchemy.sql import func




#we are defining an object to store in the database model
class service_supervisors(db.Model, UserMixin):
   __tablename__ = 'service_supervisors'
   supervisor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   supervisor_email = db.Column(db.String(200), unique = True, nullable = False)
   supervisor_name = db.Column(db.String(200), nullable=False)
   supervisor_password = db.Column(db.String(200), nullable=False)
   #allow supervisor to see all child student objects with the same supervisor_id
   #this tells sqlalchemy everytime a student service member is created, at their id to this supervisor_students relationship (its basically like a list)
   supervisor_students = db.relationship('student_service_members')
   supervisor_inventory = db.relationship('inventory')
   supervisor_bookings = db.relationship('bookings')
   #overwriting the get_id() function since flask_login only interprets id but I had to name it supervisor_id
   def get_id(self):
       return self.supervisor_email  # Return the primary key value as a string
   #adding functions so that in views.py students, teachers, and supervisors can view different home pages


class student_service_members(db.Model, UserMixin):
   __tablename__ = 'student_service_members'
   #defining schema using python
   student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   student_email = db.Column(db.String(200), unique=True, nullable=False)
   student_name = db.Column(db.String(200), nullable=False)
   student_password = db.Column(db.String(200), nullable=False)
   #supervisor_id is a foreign key (already set up on workbench), so we are setting a foreign key on the child object that references the parent object
   supervisor_id = db.Column(db.Integer, db.ForeignKey('service_supervisors.supervisor_id'), nullable=False)
   group_status = db.Column(db.String(1), nullable=False, default='p')
   #overwriting the get_id() function since flask_login only interprets id but I had to name it student_id
   def get_id(self):
       return self.student_email  # Return the primary key value as a string
   #adding properties so that on views.py students can view the student home page
   
  
class teacher(db.Model, UserMixin):
   __tablename__ = 'teacher'
   teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   teacher_email = db.Column(db.String(200), unique = True, nullable = False)
   teacher_name = db.Column(db.String(200), nullable=False)
   teacher_password = db.Column(db.String(200), nullable=False)
   teacher_bookings = db.relationship('bookings')
   #overwriting the get_id() function since flask_login only interprets id but I had to name it teacher_id
   def get_id(self):
       return self.teacher_email  # Return the primary key value as a string
   #defining functions to use in views.py to allow for students, teachers, and supervisors to view different home pages




class inventory(db.Model):
   __tablename__ = 'inventory'
   item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   item_name = db.Column(db.String(200), nullable=False)
   min_amount = db.Column(db.Integer, nullable=False)
   actual_amount = db.Column(db.Integer, nullable=False)
   supervisor_id = db.Column(db.Integer, db.ForeignKey('service_supervisors.supervisor_id'), nullable=False)
   price_per_unit = db.Column(Numeric(7, 2), nullable=False)


class bookings(db.Model):
   __tablename__ = 'bookings'
   booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   no_of_people = db.Column(db.Integer, nullable=False)
   booking_status = db.Column(db.String(1), nullable=False, default='p')
   supervisor_id = db.Column(db.Integer, db.ForeignKey('service_supervisors.supervisor_id'), nullable=False)
   teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'), nullable=False)
   start_time = db.Column(db.DateTime, nullable=False)
   end_time = db.Column(db.DateTime, nullable=False)
