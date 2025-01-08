from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db 
from .models import teacher, service_supervisors, student_service_members
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


#this particular view has to do with authentication so its different to the rest
auth = Blueprint('auth', __name__)


#creating the URIs for the login, logout, and sign-up pages
@auth.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
       email = request.form.get('email')
       password = request.form.get('password')


       #check if this account exists as a student, teacher, or supervisor
       student = student_service_members.query.filter_by(student_email=email).first()
       supervisor = service_supervisors.query.filter_by(supervisor_email=email).first()
       Teacher = teacher.query.filter_by(teacher_email=email).first()
       if student:
           if check_password_hash(student.student_password, password):
               flash('Logged in successfully!', category='success')
               #using flasks flask_login modeule, remember=true will ensure user is logged in until they sign out, clear their web browser history, or the web server restarts
               login_user(student, remember=True)
               return redirect(url_for('views.student_home'))
           else:
               flash("incorrect password, try again", category="error")
       elif supervisor:
           if check_password_hash(supervisor.supervisor_password, password):
               flash('Logged in successfully!', category='success')
               #using flasks flask_login modeule, remember=true will ensure user is logged in until they sign out, clear their web browser history, or the web server restarts
               login_user(supervisor, remember=True)
               return redirect(url_for('views.supervisor_home'))
           else:
               flash("incorrect password, try again", category="error")
       elif Teacher:
           if check_password_hash(Teacher.teacher_password, password):
               flash('Logged in successfully!', category='success')
               print(current_user) #debugging line
               #using flasks flask_login modeule, remember=true will ensure user is logged in until they sign out, clear their web browser history, or the web server restarts
               login_user(Teacher, remember=True)
               return redirect(url_for('views.teacher_home'))
           else:
               flash("incorrect password, try again", category="error")
       else:
           flash("account email does not exist", category="error")


   return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('auth.login'))


@auth.route('/sign-up')
def sign_up():
   return render_template("sign_up.html", user=current_user)


@auth.route('/sign-up-student', methods=['GET', 'POST'])
def sign_up_student():
   #differentiating between get request and post request
   if request.method == 'POST':
       #getting all information from sign-up form with post method
       email = request.form.get('email')
       fullName = request.form.get('fullName')
       supervisor_email = request.form.get('supervisor_email')
       password1 = request.form.get('password1')
       password2 = request.form.get('password2')


       # Check if the supervisor email exists
       supervisor = service_supervisors.query.filter_by(supervisor_email=supervisor_email).first()
      
       if not supervisor:
           flash('Supervisor email not found. Please check the email.', category='error')
           return redirect(url_for('auth.sign_up'))
      
       supervisor_id = supervisor.supervisor_id  # Get the supervisor_id based on the email


       #check that user email does not already exist
       student = student_service_members.query.filter_by(student_email=email).first()
       supervisor = service_supervisors.query.filter_by(supervisor_email=email).first()
       Teacher = teacher.query.filter_by(teacher_email=email).first()
       if (student or supervisor or Teacher):
           flash("account email already exists", category="error")
       #now we want to make sure information is valid
       elif len(email)<4:
           flash('Email must be greater than 3 characters', category='error')
       elif len(fullName) <2:
           flash('full name must be at least 2 characters', category='error')
       elif password1 != password2:
           flash('Your passwords do not match', category='error')
       elif len(password1)<7:
           flash('Password must contain more than 7 characters', category='error')
       else:
           #add user to database
           # Check if supervisor_id exists
           supervisor = service_supervisors.query.filter_by(supervisor_id=supervisor_id).first()
           if not supervisor:
               flash('Supervisor ID does not exist, account not created', category='error')
           else:
               # Add student to the database
               new_student = student_service_members(
                   student_email=email,
                   student_name=fullName,
                   supervisor_id=supervisor_id,
                   student_password=generate_password_hash(password1, method='pbkdf2:sha256')
               )
              
               try:
                   db.session.add(new_student)
                   db.session.commit()
                   #login student automatically after they sign-up
                   #using flasks flask_login modeule, remember=true will ensure user is logged in until they sign out, clear their web browser history, or the web server restarts
                   login_user(new_student, remember=True)
                   flash('Account created successfully!', category='success')
                   return redirect(url_for('views.student_home'))
               except Exception as e:
                   db.session.rollback()
                   flash(f'Error creating account: {str(e)}', category='error')
          
   return render_template("sign_up_student.html", user=current_user)


@auth.route('/sign-up-supervisor', methods=['GET', 'POST'])
def sign_up_supervisor():
   #differentiating between get request and post request
   if request.method == 'POST':
       #getting all information from sign-up form with post method
       email = request.form.get('email')
       fullName = request.form.get('fullName')
       password1 = request.form.get('password1')
       password2 = request.form.get('password2')
       #check that account email doesnt already exist
       student = student_service_members.query.filter_by(student_email=email).first()
       supervisor = service_supervisors.query.filter_by(supervisor_email=email).first()
       Teacher = teacher.query.filter_by(teacher_email=email).first()
       if (student or supervisor or Teacher):
           flash("account email already exists", category="error")
       #now we want to make sure information is valid
       elif len(email)<4:
           flash('Email must be greater than 3 characters', category='error')
       elif len(fullName) <2:
           flash('full name must be at least 2 characters', category='error')
       elif password1 != password2:
           flash('Your passwords do not match', category='error')
       elif len(password1)<7:
           flash('Password must contain more than 7 characters', category='error')
       else:
           #add user to database
           new_supervisor = service_supervisors(supervisor_email=email, supervisor_name=fullName, supervisor_password=generate_password_hash(password1, method='pbkdf2:sha256'))
           # Add and commit the new teacher to the database
           try:
               db.session.add(new_supervisor)
               db.session.commit()
               #automatically login supervisor after they sign-up
               #using flasks flask_login modeule, remember=true will ensure user is logged in until they sign out, clear their web browser history, or the web server restarts
               login_user(new_supervisor, remember=True)
               flash('Account created!', category='success')
               return redirect(url_for('views.supervisor_home'))  # Redirect to the login page
           except Exception as e:
               db.session.rollback()  # Rollback the session in case of error
               flash('Error creating account: ' + str(e), category='error')
           #flash successful message
   return render_template("sign_up_supervisor.html", user=current_user)


@auth.route('/sign-up-teacher', methods=['GET', 'POST'])
def sign_up_teacher():
       #differentiating between get request and post request
   if request.method == 'POST':
       #getting all information from sign-up form with post method
       email = request.form.get('email')
       fullName = request.form.get('fullName')
       password1 = request.form.get('password1')
       password2 = request.form.get('password2')
       #check that account email doesnt already exist
       student = student_service_members.query.filter_by(student_email=email).first()
       supervisor = service_supervisors.query.filter_by(supervisor_email=email).first()
       Teacher = teacher.query.filter_by(teacher_email=email).first()
       if (student or supervisor or Teacher):
           flash("account email already exists", category="error")
       #now we want to make sure information is valid
       elif len(email)<4:
           flash('Email must be greater than 3 characters', category='error')
       elif len(fullName) <2:
           flash('full name must be at least 2 characters', category='error')
       elif password1 != password2:
           flash('Your passwords do not match', category='error')
       elif len(password1)<7:
           flash('Password must contain more than 7 characters', category='error')
       else:
           #add user to database
           #shaw256 is a hashing algorithm
           new_teacher = teacher(teacher_email=email, teacher_name=fullName, teacher_password=generate_password_hash(password1, method='pbkdf2:sha256'))
            # Add and commit the new teacher to the database
           try:
               db.session.add(new_teacher)
               db.session.commit()
               #login teacher after they sign up
               #using flasks flask_login modeule, remember=true will ensure user is logged in until they sign out, clear their web browser history, or the web server restarts
               login_user(new_teacher, remember=True)
               flash('Account created!', category='success')
               return redirect(url_for('views.teacher_home'))  # Redirect to the login page
           except Exception as e:
               db.session.rollback()  # Rollback the session in case of error
               flash('Error creating account: ' + str(e), category='error')


   return render_template("sign_up_teacher.html", user=current_user)
