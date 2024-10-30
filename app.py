import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static
import glob


def clean_price(price_str):
    cleaned_price = ''.join(filter(str.isdigit, str(price_str)))
    return float(cleaned_price) if cleaned_price else 0.0


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
                if (pd.notna(property_location[0]) and pd.notna(property_location[1]) and pd.notna(obj_location[0]) and pd.notna(obj_location[1])):
                    if geodesic(property_location, obj_location).km <= distance_threshold:
                        nearby_social_objects.append(obj_row)
                        break

    nearby_social_objects_df = pd.DataFrame(nearby_social_objects).drop_duplicates()

    for _, row in nearby_social_objects_df.iterrows():
        popup_text = f"Type: {row['type']}"
        color = color_mapping.get(row['type'], 'gray')
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)

    return m


def display_map(properties, social_objects_df, relevant_objects, distance_threshold=1):
    valid_properties = properties.dropna(subset=['latitude', 'longitude'])

    if not valid_properties.empty:
        m = create_map(valid_properties, social_objects_df, relevant_objects, distance_threshold)
        folium_static(m)
    else:
        st.write("No valid properties to display on the map.")

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


@st.cache_data
def calculate_distances(df, social_objects):
    df = df.dropna(subset=['latitude', 'longitude'])
    distances_df = df.apply(calculate_distance, social_objects=social_objects, axis=1)
    distances_df.columns = [col.replace('1\\', '').replace('/', '_') for col in distances_df.columns]
    return pd.concat([df, distances_df], axis=1)


st.title("Real Estate Filter")

df = load_properties("./data/updated_krisha_new_b.csv")

social_objects_df, social_objects = load_social_objects('./data/1/*.csv')

df = df.dropna(subset=['latitude', 'longitude'])

df = calculate_distances(df, social_objects)

st.write('Raw data')
st.dataframe(df)

st.write("Choose your preferred house type")

if st.button('Бизнес-класс'):
    filtered_df = df[df['dist_to_coworking'] <= 1]
    high_price_data = filtered_df[filtered_df['price'] > 80000000].dropna(subset=['latitude', 'longitude'])
    st.write('ЖК Бизнес-класса')

    relevant_objects = ['coworking']
    filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

    display_map(high_price_data, filtered_social_objects, relevant_objects)

if st.button('Семейный'):
    filtered_df = df[
        (df['dist_to_school'] <= 2) &
        (df['dist_to_park'] <= 2) &
        (df['dist_to_kindergarten'] <= 2)
        ]
    medium_price_data = (filtered_df[(filtered_df['price'] > 40000000) & (filtered_df['price'] < 80000000)].dropna
                         (subset=['latitude', 'longitude']))
    st.write('Семейные ЖК')

    relevant_objects = ['school', 'park', 'kindergarten']
    filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

    display_map(medium_price_data, filtered_social_objects, relevant_objects)

if st.button('Молодежный'):
    filtered_df = df[
        (df['dist_to_sportarea'] <= 0.2) &
        (df['dist_to_coworking'] <= 2) &
        (df['dist_to_trc'] <= 3)
    ]
    small_price_data = filtered_df[filtered_df['price'] < 40000000].dropna(subset=['latitude', 'longitude'])
    st.write('Молодежные ЖК')

    relevant_objects = ['sportarea', 'coworking', 'trc']
    filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

    display_map(small_price_data, filtered_social_objects, relevant_objects)

if st.button('Спортсмены'):
    filtered_df = df[
        (df['dist_to_gym'] <= 1) &
        (df['dist_to_park'] <= 1) &
        (df['dist_to_pharmacy'] <= 1)
    ]
    st.write('ЖК для спортсменов')

    relevant_objects = ['gym']
    filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]
    filtered_social_objects = filtered_social_objects.dropna(subset=['latitude', 'longitude'])

    display_map(filtered_df, filtered_social_objects, relevant_objects)

if st.button('Любители культуры'):
    filtered_df = df[
        (df['dist_to_theatre'] <= 4) &
        (df['dist_to_museum'] <= 4)
        ]

    relevant_objects = ['museum', 'theatre']
    filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

    display_map(filtered_df, filtered_social_objects, relevant_objects)

if st.button('Пенсионеры'):
    filtered_df = df[
        (df['dist_to_polyclinic'] <= 1) &
        (df['dist_to_pharmacy'] <= 0.5) &
        (df['dist_to_park'] <= 0.5)
    ]

    relevant_objects = ['park', 'polyclinic', 'pharmacy']
    filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

    display_map(filtered_df, filtered_social_objects, relevant_objects)


