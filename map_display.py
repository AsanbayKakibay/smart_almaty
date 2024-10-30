import folium
from streamlit_folium import folium_static
import pandas as pd
import streamlit as st
from geopy.distance import geodesic

@st.cache_resource
def create_map(valid_properties, social_objects_df, relevant_objects, distance_threshold=1):
    color_mapping = {
        'school': 'green',
        'park': 'lightgreen',
        'kindergarten': 'orange',
        'coworking': 'darkgreen',
        'sportarea': 'purple',
        'trc': 'brown',
        'gym': 'darkpurple',
        'pharmacy': 'red',
        'theatre': 'darkred',
        'museum': 'darkorange',
        'polyclinic': 'lightred'
    }

    m = folium.Map(location=[valid_properties['latitude'].mean(), valid_properties['longitude'].mean()], zoom_start=12)

    for idx, row in valid_properties.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Description: {row['short_description']}",
            icon=folium.Icon(color='blue', icon='home')
        ).add_to(m)

    nearby_social_objects = []
    for obj_type in relevant_objects:
        relevant_locs = social_objects_df[social_objects_df['type'] == obj_type]
        relevant_locs = relevant_locs.dropna(subset=['latitude', 'longitude'])
        for _, obj_row in relevant_locs.iterrows():
            obj_location = (obj_row['latitude'], obj_row['longitude'])
            for _, prop_row in valid_properties.iterrows():
                property_location = (prop_row['latitude'], prop_row['longitude'])
                if (pd.notna(property_location[0]) and pd.notna(property_location[1]) and pd.notna(
                        obj_location[0]) and pd.notna(obj_location[1])):
                    if geodesic(property_location, obj_location).km <= distance_threshold:
                        nearby_social_objects.append(obj_row)
                        break

    nearby_social_objects_df = pd.DataFrame(nearby_social_objects).drop_duplicates()

    for _, row in nearby_social_objects_df.iterrows():
        popup_text = f"Type: {row['type']}"
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

    return m

def display_map(properties, social_objects_df, relevant_objects, distance_threshold=1):
    valid_properties = properties.dropna(subset=['latitude', 'longitude'])

    if not valid_properties.empty:
        m = create_map(valid_properties, social_objects_df, relevant_objects, distance_threshold)
        folium_static(m)
    else:
        st.write("No valid properties to display on the map.")