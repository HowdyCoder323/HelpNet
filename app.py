import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import sqlite3
import uuid
import geocoder
import folium

# Initialize SQLite database
conn = sqlite3.connect('volunteering_app.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT,
    role TEXT,
    phone TEXT,
    latitude REAL,
    longitude REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sos_requests (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    description TEXT,
    latitude REAL,
    longitude REAL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')
conn.commit()

def render_map(user_lat, user_lon, nearby_requests):
    # Create a map centered around the user's location
    user_map = folium.Map(location=[user_lat, user_lon], zoom_start=12)

    # Add a marker for the user's location
    folium.Marker(
        location=[user_lat, user_lon],
        popup="You are here",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(user_map)

    # Add markers for each nearby SOS request with the same icon and color
    for req in nearby_requests:
        folium.Marker(
            location=[req['latitude'], req['longitude']],
            popup=f"Name: {req['name']}<br>Description: {req['description']}<br>Distance: {req['distance_km']} km",
            icon=folium.Icon(color='green', icon='exclamation-sign')  # Same icon and color for all requests
        ).add_to(user_map)

    # Save map to an HTML representation
    map_html = user_map._repr_html_()
    return map_html

# Function to register users
def register_user(name, role, phone, location):
    user_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO users (id, name, role, phone, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, role, phone, location[0], location[1]))
    conn.commit()
    print(f"Registered User - ID: {user_id}, Name: {name}, Role: {role}, Phone: {phone}, Location: {location}")
    return user_id

# Function to add SOS requests
def add_sos_request(user_id, description):
    request_id = str(uuid.uuid4())
    cursor.execute('''
        SELECT latitude, longitude FROM users WHERE id = ?
    ''', (user_id,))
    user_location = cursor.fetchone()
    if user_location:
        cursor.execute('''
            INSERT INTO sos_requests (id, user_id, description, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
        ''', (request_id, user_id, description, user_location[0], user_location[1]))
        conn.commit()
        return request_id
    return None

# Function to find nearby SOS requests
def find_nearby_requests(helper_location, radius_km):
    cursor.execute('''
        SELECT r.id, r.description, r.latitude, r.longitude, u.name
        FROM sos_requests r
        JOIN users u ON r.user_id = u.id
    ''')
    requests = cursor.fetchall()
    nearby_requests = []
    for request in requests:
        request_location = (request[2], request[3])
        distance = geodesic(helper_location, request_location).km
        if distance <= radius_km:
            nearby_requests.append({
                'id': request[0],
                'description': request[1],
                'name': request[4],
                'latitude': request[2],
                'longitude': request[3],
                'distance_km': round(distance, 2)
            })
    return sorted(nearby_requests, key=lambda x: x['distance_km'])

# Function to get the current device location
def get_current_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.latlng
    else:
        return None

# App layout
st.title("HelpNet Volunteering")

st.write("This project is a platform to connect volunteers with people in need during emergencies. Users can register, raise SOS requests, or search for nearby requests based on their location. The platform visualizes requests on an interactive map, fostering quick assistance and collaboration within the community to address urgent needs effectively.")

menu = ["Register", "Make SOS Request", "Find Requests"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.header("Register as Helper or Seeker")
    name = st.text_input("Name")
    role = st.selectbox("Role", ["Helper", "Seeker"])
    phone = st.text_input("Phone Number")

    # Maintain latitude and longitude in session state
    if "lat" not in st.session_state:
        st.session_state["lat"] = 0.0
    if "lon" not in st.session_state:
        st.session_state["lon"] = 0.0

    lat = st.number_input("Latitude", format="%.6f", value=st.session_state["lat"])
    lon = st.number_input("Longitude", format="%.6f", value=st.session_state["lon"])

    if st.button("Use Current Location"):
        current_location = get_current_location()
        if current_location:
            st.session_state["lat"], st.session_state["lon"] = current_location
            st.success(f"Current location detected: Latitude {current_location[0]}, Longitude {current_location[1]}")
        else:
            st.error("Unable to detect current location. Please enter manually.")

    location = (st.session_state["lat"], st.session_state["lon"])

    if st.button("Register"):
        user_id = register_user(name, role, phone, location)
        st.success(f"Registered successfully! Your user ID is {user_id}")

elif choice == "Make SOS Request":
    st.header("Make an SOS Request")
    user_id = st.text_input("Enter your User ID")
    description = st.text_area("Describe your need")

    if st.button("Submit Request"):
        request_id = add_sos_request(user_id, description)
        if request_id:
            st.success("SOS Request submitted successfully!")
        else:
            st.error("Invalid User ID. Please register first.")

elif choice == "Find Requests":
    st.header("Find Nearby SOS Requests")

    # Maintain latitude and longitude in session state for finding requests
    if "lat_find" not in st.session_state:
        st.session_state["lat_find"] = 0.0
    if "lon_find" not in st.session_state:
        st.session_state["lon_find"] = 0.0

    lat = st.number_input("Your Latitude", format="%.6f", value=0)
    lon = st.number_input("Your Longitude", format="%.6f", value=0)
    radius_km = st.slider("Search Radius (km)", min_value=1, max_value=50, value=5)

    if st.toggle("Use Current Location"):
        current_location = get_current_location()
        if current_location:
            st.session_state["lat_find"], st.session_state["lon_find"] = current_location
            st.success(f"Current location detected: Latitude {current_location[0]}, Longitude {current_location[1]}")
        else:
            st.error("Unable to detect current location. Please enter manually.")

    helper_location = (st.session_state["lat_find"], st.session_state["lon_find"])

    # Create list of dictionaries for nearby requests
    if st.button("Search"):
        # Get nearby SOS requests within the specified radius
        nearby_requests = find_nearby_requests(helper_location, radius_km)

        if nearby_requests:
            st.write("### Nearby SOS Requests")

            # Display the requests in a table
            df = pd.DataFrame(nearby_requests)
            st.dataframe(df[['name', 'description', 'distance_km']])

            # Render map showing all nearby SOS requests
            map_html = render_map(helper_location[0], helper_location[1], nearby_requests)
            st.components.v1.html(map_html, height=600)
        else:
            st.info("No SOS requests found within the specified radius.")


