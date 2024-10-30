import pandas as pd
from geopy.distance import geodesic
import streamlit as st

def calculate_distance(row, social_objects):
    if pd.isna(row['latitude']) or pd.isna(row['longitude']):
        return pd.Series({
            f'dist_to_{obj_type}': float('nan')
            for obj_type in social_objects.keys()
        })

    property_location = (row['latitude'], row['longitude'])
    distances = {}
    for obj_type, loc in social_objects.items():
        try:
            valid_locs = [obj_loc for obj_loc in loc if pd.notna(obj_loc[0]) and pd.notna(obj_loc[1])]
            if valid_locs:
                distances[f'dist_to_{obj_type}'] = min([geodesic(property_location, obj_loc).km for obj_loc in valid_locs])
            else:
                distances[f'dist_to_{obj_type}'] = float('nan')
        except Exception as e:
            st.error(f"Error calculating distance to {obj_type}: {e}")
            distances[f'dist_to_{obj_type}'] = float('nan')

    return pd.Series(distances)

@st.cache_data
def calculate_distances(df, social_objects):
    df = df.dropna(subset=['latitude', 'longitude'])
    distances_df = df.apply(calculate_distance, social_objects=social_objects, axis=1)
    distances_df.columns = [col.replace('1\\', '').replace('/', '_') for col in distances_df.columns]
    return pd.concat([df, distances_df], axis=1)
