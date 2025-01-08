from flask import Blueprint, render_template, redirect, url_for, abort, request, flash, jsonify
from flask_login import login_required, current_user
from .models import student_service_members, teacher, service_supervisors, bookings, inventory
from datetime import datetime, timedelta
from . import db
import json
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive environments
import matplotlib.pyplot as plt
import pandas as pd
import base64
from io import BytesIO
from flask import jsonify
from sklearn.cluster import KMeans
from matplotlib import cm
from flask_mail import Message
from . import mail  # Import mail from __init__.py


#define that this file is the blueprint of our application
#we put all URIs and roots here so that we dont have to define all our views in one file, but in many
views = Blueprint('views', __name__)


def send_notification_email(to, subject, body):
   msg = Message(subject, recipients=[to])
   msg.body = body
   mail.send(msg)


#defining our first view
#this is the home view, hence why the URI is '/'
@views.route('/')
@login_required
#everytime the you're on the home view this function will run
def home():
   #user=current_user means that in the home template we can now use information from the current_user
   # Check the role of the logged-in user
   if isinstance(current_user, student_service_members):
       return redirect(url_for('views.student_home'))
   elif isinstance(current_user, teacher):
       return redirect(url_for('views.teacher_home'))
   else:
       return redirect(url_for('views.supervisor_home'))
  


@views.route('/supervisor/home', methods=['GET', 'POST'])
@login_required
def supervisor_home():
   if isinstance(current_user, service_supervisors):


       if request.method == 'POST':
           item_name = request.form.get('item_name')
           min_amount = request.form.get('min_amount', type=int)
           actual_amount = request.form.get('actual_amount', type=int)
           price_per_unit = request.form.get('price_per_unit', type=float)


           if not item_name or item_name.strip() == '':
               flash("Item name cannot be blank.", 'danger')
           elif min_amount <= 0:
               flash("Minimum amount must be greater than 0.", 'danger')
           elif actual_amount < 0:
               flash("Actual amount cannot be negative.", 'danger')
           elif price_per_unit < 0:
               flash("Price per unit cannot be negative.", 'danger')
           else:
               # Create the new inventory item
               new_item = inventory(
                   item_name=item_name,
                   min_amount=min_amount,
                   actual_amount=actual_amount,
                   price_per_unit=price_per_unit,
                   supervisor_id=current_user.supervisor_id
               )
               db.session.add(new_item)
               db.session.commit()
               flash(f'Item "{item_name}" has been added successfully!', 'success')


               # Redirect to avoid form resubmission on page reload
               return redirect(url_for('views.supervisor_home'))


       return render_template('supervisor_home.html', user=current_user)
   else:
       abort(403)


@views.route('/student/home')
@login_required
def student_home():
   if isinstance(current_user, student_service_members):
       matching_inventory = []
       if current_user.group_status == 'a':
           matching_inventory = inventory.query.filter_by(supervisor_id=current_user.supervisor_id).all()


       return render_template('student_home.html', user=current_user, matching_inventory=matching_inventory)
   else:
       abort(403)


@views.route('/request-supervisor', methods=['POST'])
@login_required
def request_supervisor():
   if isinstance(current_user, student_service_members):
       supervisor_email = request.form.get('supervisor_email')
       supervisor = service_supervisors.query.filter_by(supervisor_email=supervisor_email).first()


       if supervisor:
           current_user.supervisor_id = supervisor.supervisor_id
           current_user.group_status = 'p'  # pending approval
           db.session.commit()
           flash("Request sent to supervisor", category='success')
       else:
           flash("Supervisor not found", category='error')


   return redirect(url_for('views.student_home'))




@views.route('/student-update-amount', methods=['POST'])
@login_required
def student_update_amount():
   if isinstance(current_user, student_service_members):
       data = json.loads(request.data)
       item_id = data.get('item_id')
       actual_amount = data.get('actual_amount')


       item = inventory.query.get(item_id)
       if item and item.supervisor_id == current_user.supervisor_id:
           try:
               item.actual_amount = actual_amount
               db.session.commit()
               flash('Amount updated successfully!', category='success')
           except Exception as e:
               db.session.rollback()
               flash(f'Error: {str(e)}', category='error')


   return jsonify({})


@views.route('/student-delete-item', methods=['POST'])
@login_required
def student_delete_item():
   if isinstance(current_user, student_service_members):
       data = json.loads(request.data)
       item_id = data.get('item_id')


       item = inventory.query.get(item_id)
       if item and item.supervisor_id == current_user.supervisor_id:
           try:
               db.session.delete(item)
               db.session.commit()
               flash('Item deleted successfully!', category='success')
           except Exception as e:
               db.session.rollback()
               flash(f'Error: {str(e)}', category='error')


   return jsonify({})






#in order to allow users to submit form with bookings post method must be allowed
@views.route('/teacher/home', methods=['GET', 'POST'])
@login_required
def teacher_home():
   # Check if the current user is a teacher
   if isinstance(current_user, teacher):
       current_time = datetime.now()
       inventory_items = []
       supervisors = service_supervisors.query.all()  # Query all supervisors
       supervisor_email = None
       start_time = None
       end_time = None
       no_of_people = None


       action = request.form.get("action", "get_inventory")  # Default to "get_inventory"


       if request.method == 'POST':
           start_time = request.form.get('start_time')
           end_time = request.form.get('end_time')
           no_of_people = request.form.get('no_of_people')
           supervisor_email = request.form.get('supervisor_email')
           supervisor = service_supervisors.query.filter_by(supervisor_email=supervisor_email).first()


           if action == "get_inventory":


               # Convert start_time and end_time to datetime objects
               start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
               end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')


               # Check if supervisor has inventory
               inventory_items = inventory.query.filter_by(supervisor_id=supervisor.supervisor_id).all()
               if (not inventory_items) or int(no_of_people)<1 or (start_time.date() != end_time.date()):
                   flash('Booking cannot be created because the supervisor either has no inventory, your group size is less than 1, or your booking spans more than 1 day', 'error')
                   return render_template(
                       'teacher_home.html',
                       user=current_user,
                       current_time=current_time,
                       supervisors=supervisors,
                       start_time=start_time,
                       end_time=end_time,
                       no_of_people=no_of_people,
                       supervisor_email=supervisor_email,
                       inventory_items=inventory_items,
                       action=action
                   )


               # Check for overlapping bookings
               overlapping_bookings = bookings.query.filter(
                   (bookings.supervisor_id == supervisor.supervisor_id) &
                   (
                       ((bookings.start_time < start_time) & (bookings.end_time > end_time)) |
                       ((bookings.end_time > start_time) & (bookings.end_time <= end_time)) |
                       ((bookings.start_time >= start_time) & (bookings.start_time < end_time))
                   )
               ).all()




               if start_time.date() != end_time.date():
                   flash('Start and end times must be on the same date.', 'error')
               elif overlapping_bookings:
                   flash('Booking time overlaps with existing bookings. Please choose a different time range.', 'error')
               elif start_time>=end_time:
                   flash('Start time must be earlier than end time.', 'error')
               else:
                   inventory_items = inventory.query.filter_by(supervisor_id=supervisor.supervisor_id).all()
                   return render_template(
                       'teacher_home.html',
                       user=current_user,
                       current_time=current_time,
                       inventory_items=inventory_items,
                       supervisors=supervisors,
                       start_time=start_time,
                       end_time=end_time,
                       no_of_people=no_of_people,
                       supervisor_email=supervisor_email,
                       action="create_booking",
                   )


           elif action == "create_booking":
               new_booking = bookings(no_of_people=no_of_people, booking_status="p", supervisor_id = supervisor.supervisor_id, teacher_id = current_user.teacher_id,
                                      start_time=start_time, end_time=end_time)
               try:


                   db.session.add(new_booking)


                   db.session.commit()


                   send_notification_email(supervisor_email, "New booking created", f"A booking has been created for {no_of_people} people")


                   flash('Booking created successfully!', 'success')
               except Exception as e:
                   db.session.rollback()
                   flash('Error creating booking: {}'.format(str(e)), 'error')


               return redirect(url_for('views.teacher_home'))


       return render_template(
           'teacher_home.html',
           user=current_user,
           current_time=current_time,
           supervisors=supervisors,
           start_time=start_time,
           end_time=end_time,
           no_of_people=no_of_people,
           supervisor_email=supervisor_email,
           inventory_items=inventory_items,
           action=action
       )
   else:
       abort(403)


@views.route('/students', methods=['POST', 'GET'])
@login_required
def students():
   if isinstance(current_user, service_supervisors):
       # Fetch students with supervisor_id = current_user.supervisor_id and group_status = 'a'
       student_members = student_service_members.query.filter_by(supervisor_id=current_user.supervisor_id, group_status='a').all()


       # Fetch pending students with supervisor_id = current_user.supervisor_id and group_status = 'p'
       pending_members = student_service_members.query.filter_by(supervisor_id=current_user.supervisor_id, group_status='p').all()


       # If a form was submitted (accept/reject/delete actions)
       if request.method == 'POST':
           student_id = request.form.get('student_id')
           action = request.form.get('action')
           student = student_service_members.query.get(student_id)


           if student and student.supervisor_id == current_user.supervisor_id:
               if action == 'accept':
                   student.group_status = 'a'
               elif action == 'reject' or action == 'delete':
                   student.group_status = 'r'
               db.session.commit()
               flash(f'Student {action}ed successfully.', category='success')
           else:
               flash('Invalid action or student.', category='error')


           # Redirect back to the students page to reflect the changes
           return redirect(url_for('views.students'))


       return render_template('students.html', user=current_user, student_members=student_members, pending_members=pending_members)
   else:
       abort(403)


@views.route('/update-amount', methods=['POST'])
@login_required
def update_amount():
   if isinstance(current_user, service_supervisors):
       # Get the data from the request
       data = json.loads(request.data)
       item_id = data.get('item_id')
       actual_amount = data.get('actual_amount')


       # Find the item in the database
       item = inventory.query.get(item_id)


       # Check if the item exists and belongs to the current supervisor
       if item and item.supervisor_id == current_user.supervisor_id:
           try:
               # Update the actual amount in the database
               item.actual_amount = actual_amount
               db.session.commit()
               flash('Actual amount updated successfully!', category='success')
           except Exception as e:
               db.session.rollback()
               flash(f'Error updating amount: {str(e)}', category='error')


   return jsonify({})




@views.route('/delete-item', methods=['POST'])
def delete_item():
   item_data = json.loads(request.data)
   item_id = item_data.get('itemId')
   item = inventory.query.get(item_id)
  
   if item:
       if item.supervisor_id == current_user.supervisor_id:  # Ensure the supervisor owns the item
           try:
               db.session.delete(item)
               db.session.commit()
               flash('Item deleted successfully!', category='success')
           except Exception as e:
               db.session.rollback()
               flash(f'Error deleting item: {str(e)}', category='error')
       else:
           flash('You do not have permission to delete this item.', category='error')
  
   return jsonify({})  # Return an empty response


@views.route('/generate-heatmap', methods=['POST'])
def generate_heatmap():
   # Query the inventory data from the database
   items = inventory.query.filter_by(supervisor_id=current_user.supervisor_id).all()
  
   # Create a DataFrame from the inventory items
   df = pd.DataFrame([(item.item_name, item.price_per_unit) for item in items], columns=['Item', 'Price'])


   # Calculate the total cost of all items
   total_cost = df['Price'].sum()
   # Ensure total_cost is numeric
   total_cost = float(total_cost)  # Convert to float to ensure it's a number
  
   # Check if there are enough items to cluster
   num_items = df.shape[0]
   num_clusters = min(3, num_items)  # Set the number of clusters to at most 3, or the number of items if fewer
  
   if num_items < 2:
       return jsonify({'error': 'Not enough data to generate heatmap.'})
  
   # Apply K-means clustering
   kmeans = KMeans(n_clusters=num_clusters)
   df['Category'] = kmeans.fit_predict(df[['Price']])
  
   # Create meaningful category labels based on cluster centers
   category_labels = {i: f'Category {i+1}' for i in range(num_clusters)}
   df['Category Label'] = df['Category'].map(category_labels)
  
   # Group by category and calculate the sum of prices
   category_price = df.groupby('Category Label')['Price'].sum().reset_index()
  
   # Generate the heatmap
   plt.figure(figsize=(8, 4))  # Adjusted figure size to fit within the modal
  
   # Apply a colormap to the bars using viridis
   colors = cm.viridis(category_price.index / max(category_price.index))
   plt.bar(category_price['Category Label'], category_price['Price'], color=colors)
  
   plt.xlabel('Category')
   plt.ylabel('Total Price')
   plt.title('Value Distribution by Category')
  
   # Save the plot to a BytesIO object and encode it in base64
   img = BytesIO()
   plt.savefig(img, format='png', bbox_inches='tight')  # Added bbox_inches to fit the plot within the figure
   img.seek(0)
   plot_url = base64.b64encode(img.getvalue()).decode()
  
   # Create a detailed list of items by category
   category_items = df.groupby('Category Label')['Item'].apply(list).to_dict()
  
   # Return the heatmap image URL and the detailed category information
   return jsonify({
       'plot_url': plot_url,
       'category_items': category_items,
       'total_cost': total_cost
   })




      
@views.route('/bookings')
@login_required
def bookings_page():
   if isinstance(current_user, service_supervisors):
       teachers = teacher.query.all()
       current_time = datetime.now()  # Get the current date and time
       return render_template('bookings.html', user=current_user, current_time=current_time, teachers=teachers)
   else:
       abort(403)


@views.route('/accept-booking', methods=['POST'])
@login_required
def accept_booking():
   data = request.get_json()
   booking_id = data.get('bookingId')
  
   # Find the booking by id
   booking = bookings.query.get(booking_id)
  
   if booking and booking.supervisor_id == current_user.supervisor_id:
       # Update the booking status to 'a' (accepted)
       booking.booking_status = 'a'
       db.session.commit()
       return jsonify({'success': True}), 200
   else:
       return jsonify({'error': 'Booking not found or unauthorized'}), 404


@views.route('/reject-booking', methods=['POST'])
@login_required
def reject_booking():
   data = request.get_json()
   booking_id = data.get('bookingId')
  
   # Find the booking by id
   booking = bookings.query.get(booking_id)
  
   if booking and booking.supervisor_id == current_user.supervisor_id:
       # Delete the booking
       db.session.delete(booking)
       db.session.commit()
       return jsonify({'success': True}), 200
   else:
       return jsonify({'error': 'Booking not found or unauthorized'}), 404
  


@views.route('/delete-booking', methods=['POST'])
def delete_booking():
   data = request.get_json()  # Get JSON data sent in the POST request
   booking_id = data.get('bookingId')  # Extract the booking ID


   # Check if the booking exists
   booking = bookings.query.get(booking_id)  # Replace `bookings` with your model name
   if booking:
       try:
           db.session.delete(booking)  # Delete the booking from the database
           db.session.commit()  # Commit the changes
           return jsonify({'success': True}), 200  # Respond with success
       except Exception as e:
           db.session.rollback()  # Rollback if there's an error
           return jsonify({'error': 'Database error: ' + str(e)}), 500
   else:
       return jsonify({'error': 'Booking not found'}), 404
