from modules import ConnectDB
from flask import Flask, request, render_template, jsonify
from logger import logging
from datetime import date 

app = Flask(__name__)

@app.route('/',methods= ['GET','POST'])
def home_page():
    # Logging for GET request (rendering the initial form)
    if request.method== 'GET':
        logging.info("Rendering index.html for GET request.")
        return render_template("index.html")
    else:
        # This block handles POST requests (form submission for booking)
        logging.info("Starting the bus booking process for POST request.")
        
        # Initialize connection within the request context
        # This ensures a fresh connection for each POST request
        conn = ConnectDB() 
        try:
            conn.connect_to_db() # Establish the database connection.
            logging.info("Successfully connected to the database for current request.")
        except ConnectionError as e: # Catch the specific ConnectionError from modules.py
            logging.error(f"Failed to connect to DB for POST request: {e}", exc_info=True)
            # Render an error message if connection fails
            return render_template("index.html", error_message="Error connecting to database. Please try again later.")
        except Exception as e:
            logging.error(f"An unexpected error occurred during DB connection: {e}", exc_info=True)
            return render_template("index.html", error_message="An unexpected error occurred. Please try again later.")

        # Getting inputs from index.html (including the new hidden fields)
        user_id = request.form.get('userId')
        source = request.form.get('source') 
        destination = request.form.get('destination')
        travel_date = request.form.get('travelDate') 
        schedule_id = request.form.get('selectedScheduleId') 
        seat_number = request.form.get('seatNumber')

        logging.info(f"Booking attempt - User ID: {user_id}, Source: {source}, Destination: {destination}, Travel Date: {travel_date}, Schedule ID: {schedule_id}, Seat Number: {seat_number}")

        # Basic validation for essential booking parameters
        if not all([user_id, source, destination, travel_date, schedule_id, seat_number]):
            logging.warning("Missing required booking parameters in POST request.")
            conn.close_connection()
            return render_template("index.html", error_message="Please select all booking details (Source, Destination, Date, Seat).")

        try:
            # Type conversion for seat_number and schedule_id
            seat_number_int = int(seat_number)
            schedule_id_int = int(schedule_id)
            user_id_int = int(user_id) # Convert UserID to int
        except ValueError:
            logging.error("Invalid input for Seat Number, Schedule ID, or User ID (not integers).")
            conn.close_connection()
            return render_template("index.html", error_message="Invalid input for Seat Number, Schedule ID, or User ID.")

        try:
            # Check if UserID exists. If not, attempt to register.
            if not conn.check_user_exists(user_id_int):
                logging.info(f"User ID {user_id_int} does not exist. Attempting to register new user.")
                # AUTO-REGISTRATION: Using placeholder data for other user fields
                registered_successfully = conn.register_user(
                    user_id=user_id_int,
                    first_name=f"NewUser_{user_id_int}", # Placeholder
                    last_name="Auto",                     # Placeholder
                    email=f"user_{user_id_int}@example.com", # Placeholder
                    phone_number="000-000-0000",          # Placeholder
                    password="password"                   # VERY IMPORTANT: Use secure hashing in production!
                )
                if not registered_successfully:
                    logging.error(f"Failed to auto-register user {user_id_int}. Could be duplicate ID if not auto-incremented.")
                    conn.close_connection()
                    return render_template("index.html", error_message=f"Failed to register User ID {user_id_int}. It might already exist or there's a DB issue.")
                else:
                    logging.info(f"User ID {user_id_int} successfully auto-registered.")
            else:
                logging.info(f"User ID {user_id_int} already exists. Proceeding with booking.")

            # Attempt to book the seat (now that user is guaranteed to exist)
            booking = conn.book_seat(
                schedule_id=schedule_id_int, 
                seat_number=seat_number_int, 
                user_id=user_id_int # Use the integer UserID
            ) 
            logging.info(f"Booking Status for seat {seat_number_int}, user {user_id_int}: {booking}")
        except Exception as e:
            logging.error(f"Error during user check/registration or booking: {e}", exc_info=True)
            return render_template("index.html", error_message="Error occurred during user validation or booking.")
        finally:
            # Ensure database connection is closed even if booking fails or errors occur
            conn.close_connection()
            logging.info("Database connection closed for current request.")
        
        if booking == True:
            try:
                # Fetch complete bus details for the booked schedule to display on result.html
                bus_details_data = conn.get_schedule_details_by_id(schedule_id_int)

                if bus_details_data:
                    # Format date/time objects to strings if they are not already
                    if isinstance(bus_details_data.get('DepartureDate'), date):
                        bus_details_data['DepartureDate'] = bus_details_data['DepartureDate'].strftime('%Y-%m-%d')
                    # Time objects will also need formatting if not strings
                    if isinstance(bus_details_data.get('DepartureTime'), (type(None), object)): # Check if it's a time object (not None)
                        # Assuming DepartureTime is a datetime.time object
                        try:
                            bus_details_data['DepartureTime'] = bus_details_data['DepartureTime'].strftime('%H:%M')
                        except AttributeError: # If it's already a string or other non-time format
                            pass
                    if isinstance(bus_details_data.get('ArrivalTime'), (type(None), object)):
                        try:
                            bus_details_data['ArrivalTime'] = bus_details_data['ArrivalTime'].strftime('%H:%M')
                        except AttributeError:
                            pass


                    logging.info("Booking confirmed! Rendering result.html with detailed bus information.")
                    return render_template("result.html", bus_details=bus_details_data)
                else:
                    logging.warning(f"Booking confirmed but could not retrieve details for ScheduleID {schedule_id_int}.")
                    return render_template("result.html", bus_details={"message": "Booking Confirmed! Details could not be retrieved.", "ScheduleID": schedule_id_int})
            except Exception as e:
                logging.error(f"Error preparing result.html after successful booking: {e}", exc_info=True)
                return render_template("result.html", message="Booking confirmed! An error occurred displaying details.")
        else:
            logging.info("Booking failed. Rendering index.html with error message.")
            return render_template("index.html", error_message="Booking failed. Please try again, perhaps the seat is taken or another issue occurred.")
            
# New API endpoint to get available dates for a given source and destination
@app.route('/api/available_dates')
def get_available_dates():
    source = request.args.get('source')
    destination = request.args.get('destination')
    logging.info(f"API request for available dates - Source: {source}, Destination: {destination}")

    if not source or not destination:
        logging.warning("Missing source or destination for /api/available_dates request.")
        return jsonify([]) # Return an empty list if parameters are missing

    conn = ConnectDB()
    try:
        conn.connect_to_db()
        available_dates_data = conn.get_available_bus_schedules(source, destination)
        logging.info(f"Found {len(available_dates_data)} available schedules for {source} to {destination}.")
        formatted_data = []
        for item in available_dates_data:
            if isinstance(item.get('TravelDate'), date):
                item['TravelDate'] = item['TravelDate'].strftime('%Y-%m-%d')
            formatted_data.append(item)
        return jsonify(formatted_data)
    except ConnectionError as e:
        logging.error(f"API - Connection error fetching available dates: {e}", exc_info=True)
        return jsonify([]), 500 # Internal server error
    except Exception as e:
        logging.error(f"API - Error fetching available dates: {e}", exc_info=True)
        return jsonify([]), 500
    finally:
        conn.close_connection()
        logging.info("API - Database connection closed for /api/available_dates.")

# New API endpoint to get available seats for a specific schedule ID
@app.route('/api/available_seats')
def get_available_seats():
    schedule_id = request.args.get('schedule_id')
    logging.info(f"API request for available seats - Schedule ID: {schedule_id}")

    if not schedule_id:
        logging.warning("Missing schedule_id for /api/available_seats request.")
        return jsonify({"total_seats": 0, "occupied_seats": []})

    try:
        schedule_id_int = int(schedule_id)
    except ValueError:
        logging.error(f"Invalid schedule_id received: {schedule_id}")
        return jsonify({"total_seats": 0, "occupied_seats": []}), 400 # Bad request

    conn = ConnectDB()
    try:
        conn.connect_to_db()
        seat_data = conn.get_seat_availability(schedule_id_int)
        logging.info(f"Seat availability for Schedule ID {schedule_id_int}: {seat_data}")
        return jsonify(seat_data)
    except ConnectionError as e:
        logging.error(f"API - Connection error fetching available seats: {e}", exc_info=True)
        return jsonify({"total_seats": 0, "occupied_seats": []}), 500
    except Exception as e:
        logging.error(f"API - Error fetching available seats: {e}", exc_info=True)
        return jsonify({"total_seats": 0, "occupied_seats": []}), 500
    finally:
        conn.close_connection()
        logging.info("API - Database connection closed for /api/available_seats.")


if __name__== '__main__':
    logging.info("Flask application starting...")
    app.run(host= '0.0.0.0', port= 8080, debug=True)
    logging.info("Flask application stopped.") 
