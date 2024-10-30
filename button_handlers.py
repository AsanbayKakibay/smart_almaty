import streamlit as st
from map_display import display_map

def handle_buttons(df, social_objects_df):
    if st.button('Бизнес-класс'):
        filtered_df = df[df['dist_to_coworking'] <= 1]
        high_price_data = filtered_df[filtered_df['price'] > 80000000].dropna(subset=['latitude', 'longitude'])
        st.write('ЖК Бизнес-класса')

        relevant_objects = ['coworking']
        filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

        display_map(high_price_data, social_objects_df, relevant_objects)

    if st.button('Семейный'):
        filtered_df = df[
            (df['dist_to_school'] <= 2) &
            (df['dist_to_park'] <= 2) &
            (df['dist_to_kindergarten'] <= 2)
        ]
        medium_price_data = filtered_df[(filtered_df['price'] > 40000000) & (filtered_df['price'] < 80000000)].dropna(subset=['latitude', 'longitude'])
        st.write('Семейные ЖК')

        relevant_objects = ['school', 'park', 'kindergarten']
        filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

        display_map(medium_price_data, filtered_social_objects, relevant_objects)

    if st.button('Молодежный'):
        filtered_df = df[
            (df['dist_to_sportarea'] <= 0.5) &
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

        display_map(filtered_df, social_objects_df, relevant_objects)

    if st.button('Любители культуры'):
        filtered_df = df[
            (df['dist_to_theatre'] <= 5) &
            (df['dist_to_museum'] <= 5)
        ]

        relevant_objects = ['museum', 'theatre']
        filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

        display_map(filtered_df, social_objects_df, relevant_objects)

    if st.button('Пенсионеры'):
        filtered_df = df[
            (df['dist_to_polyclinic'] <= 1) &
            (df['dist_to_pharmacy'] <= 0.5) &
            (df['dist_to_park'] <= 0.5)
        ]

        relevant_objects = ['park', 'polyclinic', 'pharmacy']
        filtered_social_objects = social_objects_df[social_objects_df['type'].isin(relevant_objects)]

        display_map(filtered_df, social_objects_df, relevant_objects)

