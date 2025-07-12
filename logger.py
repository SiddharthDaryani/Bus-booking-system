import logging
import os
from datetime import datetime

# Define the base path for your application logs
# This path was provided by you earlier.
base_application_path = os.getcwd()
log_folder_name = 'logs'

# Construct the full path to the logs directory
log_path = os.path.join(base_application_path, log_folder_name)

try:
    # Create the log directory if it does not exist
    # exist_ok=True prevents an error if the directory already exists
    os.makedirs(log_path, exist_ok=True)
    
    # Generate a unique log file name based on the current timestamp
    log_file = f"{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.log"
    log_file_path = os.path.join(log_path, log_file)

    # Configure the root logger using basicConfig
    # This sets up file logging for the entire application.
    logging.basicConfig(
        level=logging.INFO,  # Set the minimum logging level to INFO
        filename=log_file_path, # Specify the log file
        format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s" # Define log message format
    )
    
    # Log a message to confirm successful setup (this will go to the file)
    logging.info(f"Logger configured successfully to: {log_file_path}")

except OSError as e:
    # If there's an OS error (e.g., permissions issue or invalid path),
    # print an error message to the console and fall back to console logging.
    print(f"ERROR (logger.py): Could not create log directory or file at {log_path}. Error: {e}")
    print("Falling back to console logging.")
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
    logging.error("Failed to set up file logging. Logging to console instead.")
except Exception as e:
    # Catch any other unexpected errors during logging setup
    print(f"ERROR (logger.py): An unexpected error occurred during logging setup: {e}")
    print("Falling back to console logging.")
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
    logging.error("Failed to set up file logging. Logging to console instead due to unexpected error.")