import pandas as pd
import glob
import streamlit as st

def clean_price(price_str):
    cleaned_price = ''.join(filter(str.isdigit, str(price_str)))
    return float(cleaned_price) if cleaned_price else 0.0

@st.cache_data
def load_properties(filepath):
    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.astype(str)
        df['price'] = df['price'].apply(clean_price)
        return df
    except FileNotFoundError:
        st.error("CSV file not found.")
        st.stop()

@st.cache_data
def load_social_objects(file_pattern):
    social_objects = {}
    csv_files = glob.glob(file_pattern)

    for file in csv_files:
        obj_type = file.split('/')[-1].split('.')[0]
        data = pd.read_csv(file)

        if 'latitude' in data.columns and 'longitude' in data.columns:
            locations = list(zip(data['latitude'], data['longitude']))
        elif 'Широта' in data.columns and 'Долгота' in data.columns:
            locations = list(zip(data['Широта'], data['Долгота']))
        else:
            st.warning(f"File {file} does not contain expected latitude/longitude columns.")
            continue

        social_objects[obj_type] = locations

    social_objects_list = []
    for obj_type, locs in social_objects.items():
        for loc in locs:
            social_objects_list.append({'type': obj_type.replace('1\\', ''), 'latitude': loc[0], 'longitude': loc[1]})

    return pd.DataFrame(social_objects_list), social_objects
