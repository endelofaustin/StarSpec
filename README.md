# StarSpec
A FastAPI and JavaScript-based application for real-time monitoring of URL statuses. Features a dynamic frontend for visualizing URL accessibility over time.

## Description

This URL Monitor Application is a FastAPI-based web service designed to monitor the status of specified URLs. It periodically pings the given URLs and records their status as 'green' for a successful HTTP response or 'red' for failure. The application features a minimalistic frontend that displays the status history of each monitored URL on a dynamic grid, providing a clear, real-time visual representation of their accessibility over time.

## Features

- **URL Monitoring**: Periodically pings a list of user-specified URLs to check their accessibility.
- **Status Tracking**: Records the status of each ping (success or failure) and maintains a history for each URL.
- **Dynamic Frontend**: Displays the status history of monitored URLs on a grid, with colors indicating the success (green) or failure (red) of each ping.
- **Easy URL Addition**: Users can easily add URLs to monitor through a simple input form on the frontend.

## Technologies Used

- **FastAPI**: For the backend server, providing a robust, efficient framework for developing APIs.
- **aiohttp**: For making asynchronous HTTP requests within the FastAPI application.
- **JavaScript**: Powers the frontend logic for dynamically updating the status grid and handling user input.
- **HTML/CSS**: For structuring and styling the frontend.

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourgithub/url-monitor.git
   cd url-monitor
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install the dependencies:

bash
Copy code
pip install -r requirements.txt
Run the application:

bash
Copy code
uvicorn main:app --reload
The application should now be running on http://127.0.0.1:8000. Open your web browser and navigate to this address to view the frontend and start monitoring URLs.
