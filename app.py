from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask import Flask, render_template, request, jsonify, session, flash
from datetime import datetime
from flask_mail import Mail,Message

from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to something secure

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'  # Replace with your MySQL host
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'Murari@24'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'booktrain'  # Replace with your database name

mysql = MySQL(app)

# Home route (after successful login)
@app.route('/')
def home():
    if 'user_id' not in session:
        flash('You need to login first!', 'danger')
        return redirect(url_for('login'))
    
    return render_template('home.html', username=session['username'])

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate password strength
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('signup.html')
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')
        
        # Hash password
        hashed_password = generate_password_hash(password)

        # Check if email is already in use
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        cursor.close()
        if existing_user:
            flash('Email already exists. Please use a different email.', 'danger')
            return render_template('signup.html')

        # Insert new user into database
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Users (username, email, phone_number, password_hash) VALUES (%s, %s, %s, %s)', 
                       (username, email, phone_number, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[3], password):  # user[3] is the password_hash column
            session['user_id'] = user[0]  # Store the user ID in the session
            session['username'] = user[1] 
            session['mail']=user[2]# Store the username in the session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to home page
        else:
            flash('Invalid Credentials. Please try again.', 'danger')
            return render_template('Login.html', message='Invalid Credentials', is_error=True)

    return render_template('Login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to login first!', 'danger')
        return redirect(url_for('login'))
    
    # Get user_id from the session
    user_id = session['user_id']

    # Fetch user details from the Users table
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username, email, phone_number FROM Users WHERE user_id = %s", (user_id,))
    user_details = cursor.fetchone()

    # Fetch all bookings made by the user
    cursor.execute("""
        SELECT b.booking_id, t.train_number, t.train_name, s.coach_type, b.journey_date, b.status
        FROM Bookings b
        JOIN Trains t ON b.train_id = t.train_id
        JOIN Coaches s ON b.coach_id = s.coach_id
        WHERE b.user_id = %s
    """, (user_id,))
    bookings = cursor.fetchall()

    cursor.close()

    return render_template('profile.html', user_details=user_details, bookings=bookings)

@app.route('/get_stations')
def get_stations():
    query = request.args.get('query')
    
    if not query:
        return jsonify([])  # If no query, return an empty list
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT station_name FROM Stations WHERE station_name LIKE %s LIMIT 10', ('%' + query + '%',))
    stations = cursor.fetchall()
    cursor.close()
    
    if stations:
        return jsonify([station[0] for station in stations])
    else:
        return jsonify({'error': 'No stations found.'}), 404  # Return error if no stations are found

@app.route('/search_trains', methods=['POST'])
def search_trains():
    from_station = request.form['from_station']
    to_station = request.form['to_station']
    travel_date = request.form['travel_date']

    # Store the journey date in session for later use
    session['journey_date'] = travel_date  # Store the journey date in session

    # Query to find trains that match the criteria (using Trains, Stations, and Schedules)
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT t.train_number, t.train_name, s1.station_name AS source_station, s2.station_name AS destination_station,
        t.train_id, sch.arrival_time, sch.departure_time
        FROM Trains t
        JOIN Stations s1 ON t.source_station_id = s1.station_id  -- Source station
        JOIN Stations s2 ON t.destination_station_id = s2.station_id  -- Destination station
        JOIN schedules sch ON sch.train_id = t.train_id
        WHERE s1.station_name = %s  -- From Station 1
          AND s2.station_name = %s  -- To Station 2
            -- Ensure we're querying the correct travel date
    """, (from_station, to_station))  # Make sure to pass the parameters as a tuple
    
    trains = cursor.fetchall()
    cursor.close()

    if trains:
        train_list = []
        for train in trains:
            # Convert arrival_time and departure_time from datetime to string (HH:MM format)
            arrival_time = train[5].strftime('%H:%M')  # Format datetime to HH:MM
            departure_time = train[6].strftime('%H:%M')  # Format datetime to HH:MM

            train_list.append({
                'train_number': train[0],
                'train_name': train[1],
                'source_station': train[2],
                'destination_station': train[3],
                'arrival_time': arrival_time,  # Formatted time
                'departure_time': departure_time,  # Formatted time
                'train_id': train[4]
            })
            print('Train found')
        return render_template('train_results.html', trains=train_list ,username=session['username'])
    else:
        flash('No trains found for the selected route and date.', 'danger')
        return redirect(url_for('home'))

@app.route('/seat_selection/<int:train_id>', methods=['GET', 'POST'])
def seat_selection(train_id):
    if request.method == 'POST':
        coach_id = request.form['coach_id']
        return redirect(url_for('seat_selection_with_coach', train_id=train_id, coach_id=coach_id))
    
    # Fetch available coaches for the selected train
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT coach_id, coach_type, ticket_price, available_seats 
        FROM Coaches 
        WHERE train_id = %s
    """, (train_id,))
    coaches = cursor.fetchall()

    # Fetch train details
    cursor.execute("""
        SELECT train_number, train_name, s1.station_name AS source_station, s2.station_name AS destination_station 
        FROM Trains t
        JOIN Stations s1 ON t.source_station_id = s1.station_id
        JOIN Stations s2 ON t.destination_station_id = s2.station_id
        WHERE t.train_id = %s
    """, (train_id,))
    train_details = cursor.fetchone()

    cursor.close()

    return render_template('seat_selection.html', train_id=train_id, coaches=coaches, train_details=train_details)

@app.route('/selected_seats/<int:train_id>/<int:coach_id>', methods=['GET', 'POST'])
def selected_seats(train_id, coach_id):
    if request.method == 'POST':
            # Assuming you pass selected seat data (for multiple seats) to the backend here
            selected_seats = request.form['selected_seats'].split(',')  # Get selected seats
            # You can pass selected seats and other necessary details to the passenger details page
            return redirect(url_for('passenger_details', train_id=train_id, coach_id=coach_id, selected_seats=','.join(selected_seats)))
        

@app.route('/seat_selection/<int:train_id>/<int:coach_id>', methods=['GET', 'POST'])
# if request.method == 'POST':
    #     # Assuming you pass selected seat data (for multiple seats) to the backend here
    #     selected_seats = request.form['selected_seats'].split(',')  # Get selected seats
    #     # You can pass selected seats and other necessary details to the passenger details page
    #     return redirect(url_for('passenger_details', train_id=train_id, coach_id=coach_id, selected_seats=','.join(selected_seats)))
    
    # Fetch train details for the given train_id
def seat_selection_with_coach(train_id, coach_id):
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT train_number, train_name, s1.station_name AS source_station, s2.station_name AS destination_station 
        FROM Trains t
        JOIN Stations s1 ON t.source_station_id = s1.station_id
        JOIN Stations s2 ON t.destination_station_id = s2.station_id
        WHERE t.train_id = %s
    """, (train_id,))
    train_details = cursor.fetchone()

    # Fetch the available seats for the selected coach
    cursor.execute("""
        SELECT s.seat_id, s.seat_number, s.is_available 
        FROM Seats s
        WHERE s.coach_id = %s 
    """, (coach_id,))
    seats = cursor.fetchall()

    # Fetch coach details (ticket price and available seats)
    cursor.execute("""
        SELECT coach_type, ticket_price, available_seats 
        FROM Coaches 
        WHERE coach_id = %s
    """, (coach_id,))
    coach_details = cursor.fetchone()

    cursor.close()

    return render_template('seat_selection_with_coach.html', train_id=train_id, coach_id=coach_id, seats=seats, coach_details=coach_details, train_details=train_details)


# Passenger details route
@app.route('/confirm_booking/<int:train_id>/<int:coach_id>', methods=['POST'])
def confirm_booking(train_id, coach_id):
    # Get selected seats and passenger details from the form
    selected_seats = request.form['selected_seats'].split(',')  # Selected seats as a comma-separated string
    passenger_names = request.form['passenger_name']  # List of passenger names
    passenger_ages = request.form['passenger_age']  # List of passenger ages
    passenger_genders = request.form['passenger_gender']  # List of passenger genders
    
    # Fetch the user ID (from session or wherever it's stored)
    user_id = session.get('user_id')  # Example: getting user_id from session
    journey_date = session.get('journey_date', datetime.now().date())

    cursor = mysql.connection.cursor()

    # Step 1: Insert booking into Bookings table (without booking_id)
    cursor.execute("""
        INSERT INTO Bookings (user_id, train_id, coach_id, journey_date, total_price, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, train_id, coach_id, journey_date, 0.0, 'Confirmed'))  # Adjust total_price as needed
    
    # Commit the transaction to save the booking
    mysql.connection.commit()

    # Step 2: Retrieve the generated booking_id
    booking_id = cursor.lastrowid  # Fetch the last inserted ID (the booking_id)
    
    # Debugging: Print the booking_id to verify it
    print(f"Booking ID: {booking_id}")

    # Step 3: Insert passenger details into Passengers table using the booking_id
    for i, seat_number in enumerate(selected_seats):
        cursor.execute("""
            INSERT INTO Passengers (booking_id, seat_number, name, age, gender)
            VALUES (%s, %s, %s, %s, %s)
        """, (booking_id, seat_number, passenger_names, passenger_ages, passenger_genders))

        # Step 4: Mark the seat as occupied in the Seats table
        cursor.execute("""
            UPDATE Seats
            SET is_available = FALSE
            WHERE seat_number = %s AND coach_id = %s
        """, (seat_number, coach_id))

    # Step 5: Update the available seats for the coach after booking
    cursor.execute("""
        UPDATE Coaches
        SET available_seats = available_seats - %s
        WHERE coach_id = %s AND train_id = %s
    """, (len(selected_seats), coach_id, train_id))

    # Commit all the changes (passenger and seat updates)
    mysql.connection.commit()
    cursor.close()

    # Flash a success message and redirect to the ticket confirmation page
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('ticket_confirmed', booking_id=booking_id))





# Ticket confirmation route
@app.route('/passenger_details/<int:train_id>/<int:coach_id>', methods=['GET', 'POST'])
def passenger_details(train_id, coach_id):
    selected_seats = request.args.get('selected_seats').split(',')
    
    if request.method == 'POST':
        # Get passenger details from the form
        passenger_names = [request.form[f'passenger_name_{i}'] for i in range(1, len(selected_seats) + 1)]
        passenger_ages = [request.form[f'passenger_age_{i}'] for i in range(1, len(selected_seats) + 1)]
        passenger_genders = [request.form[f'passenger_gender_{i}'] for i in range(1, len(selected_seats) + 1)]
        
        cursor = mysql.connection.cursor()

        # Insert passenger details into Passengers table
        for i, seat_number in enumerate(selected_seats):
            cursor.execute("""
                INSERT INTO Passengers (train_id, coach_id, seat_number, passenger_name, passenger_age, passenger_gender)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (train_id, coach_id, seat_number, passenger_names[i], passenger_ages[i], passenger_genders[i]))

            # Mark the seat as unavailable
            cursor.execute("""
                UPDATE Seats
                SET is_available = FALSE
                WHERE seat_number = %s AND train_id = %s
            """, (seat_number, train_id))

        mysql.connection.commit()
        cursor.close()

        flash('Booking confirmed successfully!', 'success')
        return redirect(url_for('t', train_id=train_id))

    return render_template('passenger_details.html', train_id=train_id, coach_id=coach_id, selected_seats=selected_seats)

@app.route('/ticket_confirmed/<int:booking_id>')
def ticket_confirmed(booking_id):
    # Fetch booking details
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT b.booking_id, t.train_number, t.train_name, s.coach_type,b.status, b.journey_date,
               p.seat_number, p.name, p.age, p.gender
        FROM Bookings b
        JOIN Trains t ON b.train_id = t.train_id
        JOIN Coaches s ON b.coach_id = s.coach_id
        JOIN Passengers p ON b.booking_id = p.booking_id
        WHERE b.booking_id = %s
    """, (booking_id,))  # Pass booking_id as a tuple (booking_id,)
    
    booking_details = cursor.fetchall()
    cursor.close()

    # Pass booking details to the template
    return render_template('ticket_confirmed.html', booking_details=booking_details)

@app.route('/pnr')
def pnr():
    if 'user_id' not in session:
        flash('You need to login first!', 'danger')
        return redirect(url_for('login'))
    
    return render_template('pnr.html', username=session['username'])



@app.route('/check_pnr', methods=['POST'])
def check_pnr():
    booking_id = request.form.get('booking_id')

    cursor = mysql.connection.cursor()

    # Query to get booking and passenger details
    cursor.execute("""
        SELECT b.booking_id, t.train_number, t.train_name, s.coach_type, b.status, b.journey_date, 
               p.seat_number, p.name, p.age, p.gender
        FROM Bookings b
        JOIN Trains t ON b.train_id = t.train_id
        JOIN Coaches s ON b.coach_id = s.coach_id
        JOIN Passengers p ON b.booking_id = p.booking_id
        WHERE b.booking_id = %s
    """, (booking_id,))

    booking_details = cursor.fetchall()

    if not booking_details:
        error_message = "No booking found with the provided Booking ID."
        return render_template('pnr.html', error=error_message)

    cursor.close()

    return render_template('pnr.html', booking_details=booking_details)

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587  # Replace with your SMTP port
app.config['MAIL_USE_TLS'] = True  # Enable TLS encryption
app.config['MAIL_USERNAME'] = 'nithinkandi@myyahoo.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'Bluehorn@2004.'  # Replace with your email password

mail = Mail(app)

# Route for sending email
@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        booking_details = request.form.get('booking_details')  # Adjust based on your form data structure

        # Compose email message
        msg = Message('Booking Confirmation Details',
                      sender='nithinkandi@myyahoo.com',
                      recipients=session['mail'])  # Replace with recipient email address

        msg.body = f'Booking Details:\n{booking_details}'  # Example body content

        # Send email
        try:
            mail.send(msg)
            return 'Email sent successfully.'
        except Exception as e:
            return str(e), 500  # Return error message if email fails to send

if __name__ == '__main__':
    app.run(debug=True)
