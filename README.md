# HelpNet

A platform designed to connect volunteers (helpers) with individuals in need (seekers) during emergencies. This project enables users to register, raise SOS requests, and locate nearby help using an interactive map, fostering a community-driven approach to addressing urgent needs effectively.

## Features

- **User Registration**: Sign up as a helper or seeker with name, role, phone number, and location.
- **Raise SOS Requests**: Seekers can create SOS requests with detailed descriptions.
- **Find Nearby Requests**: Helpers can search for requests within a specified radius and visualize them on an interactive map.
- **Interactive Map**: View all requests and user locations dynamically plotted on the map.

---

## How to Run

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-repository/immediate-volunteering-platform.git
    cd immediate-volunteering-platform
    ```

2. **Install dependencies**:  
   Make sure you have Python installed, then install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application**:  
   Launch the Streamlit app with the following command:
    ```bash
    streamlit run app.py
    ```

4. **Access the app**:  
   Open the local server URL (e.g., `http://localhost:8501`) displayed in the terminal in your browser.

---

## How to Use

### 1. Register:
- Enter your details (name, role, phone, and location).
- Use the "Current Location" feature to auto-detect your coordinates or manually enter them.

### 2. Raise an SOS Request:
- Enter your user ID (provided during registration).
- Provide a description of your emergency and submit.

### 3. Find Requests:
- Enter your location or use the "Current Location" feature.
- Specify the search radius in kilometers and view all nearby requests.
- Explore details of each request in a table or on an interactive map.

---

## Project Structure

### Key Files:
- **`app.py`**: Main Streamlit app script implementing all functionality.
- **`requirements.txt`**: File specifying the necessary Python libraries.
- **`volunteering_app.db`**: SQLite database created automatically to store user and SOS request data.

---

## Code Explanation

### Database Setup:
- SQLite is used to manage user registrations and SOS requests.
- Two tables:
  - **`users`**: For storing user details.
  - **`sos_requests`**: For storing SOS data.

### User Registration:
- Users register with name, role (helper or seeker), phone number, and location.
- Auto-generated UUIDs uniquely identify each user.

### Raising SOS Requests:
- Seekers submit a description of their emergency. Their location is fetched from the database.

### Finding Nearby Requests:
- Helpers search by location and radius, utilizing geospatial calculations via `geopy`.
- Results are displayed in a sortable table and plotted on an interactive map using `folium`.

---

## Technologies Used

- **Streamlit**: Web app framework for interactive user interfaces.
- **SQLite**: Lightweight database for data storage and management.
- **Folium**: For creating dynamic, interactive maps.
- **Geopy**: For geospatial calculations (e.g., distance between points).
- **Geocoder**: To fetch current device location.

---

## Future Improvements

- Add user authentication for secure access.
- Implement real-time updates for SOS requests.
- Integrate email or SMS notifications for urgent alerts.
- Enhance map visualization with clustering for dense request areas.
