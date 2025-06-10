from modules import ConnectDB
from flask import Flask, request, render_template, jsonify
from logger import logging

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
            conn.connect_to_db # Establish the database connection
            logging.info("Successfully connected to the database for current request.")
        except Exception as e:
            logging.error(f"Failed to connect to DB for POST request: {e}", exc_info=True)
            # Render an error message if connection fails
            return render_template("index.html", error_message="Error connecting to database. Please try again later.")

        # Getting inputs from index.html
        source= request.form.get('source') 
        destination= request.form.get('destination')
        travel_date= request.form.get('travelDate')
        
        logging.info(f"User search parameters - Source: {source}, Destination: {destination}, Travel Date: {travel_date}")

        try:
            # Gathering info of available buses
            avialable_buses= conn.find_available_buses(source=source,destination=destination,travel_date=travel_date)
            
            if avialable_buses is None or not avialable_buses: # Check for empty list as well
                logging.info(f"No buses available for {source} to {destination} on {travel_date}.")
                # Pass error_message to template
                return render_template("index.html", error_message="No buses available on this route for the selected date.")  
            else:
                # Assuming avialable_buses is a list of dictionaries and we take the first one
                schedule_id= avialable_buses[0]['ScheduleID']
                logging.info(f"Found available bus with ScheduleID: {schedule_id} for booking.")
            
                seat_number= request.form.get('seatNumber')
                user_id= request.form.get('userId')
                logging.info(f"Attempting to book seat {seat_number} for UserID: {user_id} on ScheduleID: {schedule_id}")

                # book_seat returns True if booking confirms else False
                booking= conn.book_seat(schedule_id=schedule_id,seat_number=seat_number,user_id=user_id) 
                logging.info(f"Booking Status for seat {seat_number}, user {user_id}: {booking}")
            
                if booking == True:
                    try:
                        # Extract details from the first available bus for display
                        # Ensure keys match what your find_available_buses returns
                        bus_details_data = avialable_buses[0] # Use the first bus's details
                        bus_number= bus_details_data.get('BusNumber')
                        company_name= bus_details_data.get('CompanyName')
                        departure_time= bus_details_data.get('DepartureTime')
                        arrival_time= bus_details_data.get('ArrivalTime')
                        price= bus_details_data.get('Price')
                        distance= bus_details_data.get('Distance')
                        departure_date= bus_details_data.get('DepartureDate')
                        
                        # Collect details into a list (for consistency with your original code)
                        bus_details=[bus_number,company_name,departure_time,arrival_time,price,distance,departure_date] 
                            
                        logging.info("Booking successful. About to render result.html with bus details.")
                        return render_template("result.html", bus_details= bus_details)
                    except KeyError as e:
                        logging.error(f"KeyError accessing bus data for rendering result.html: {e}", exc_info=True)
                        return render_template("index.html", error_message="Error accessing bus details for display.")
                else:
                    logging.info("Booking failed. Rendering index.html with error message.")
                    return render_template("index.html", error_message="Booking failed. Please try again, perhaps the seat is taken.")
        except Exception as e:
            logging.error(f"An error occurred during bus search or booking: {e}", exc_info=True)
            return render_template("index.html", error_message="An unexpected error occurred. Please try again.")
        finally:
            # Ensure database connection is closed even if booking fails or errors occur
            conn.close_connection()
            logging.info("Database connection closed for current request.")
            
# app is getting started from here
if __name__== '__main__':
    logging.info("Flask application starting...")
    app.run(host= '0.0.0.0', port= 8080)
    # Note: The logging.info("Flask application stopped.") line might not always run
    # depending on how app.run exits (e.g., if killed by Ctrl+C).
