'''
Name: Kelsey Ackerman
CS230: Section 5
Data: skyscrapers.csv
URL: Link to your web application online (see extra credit)
Description: This program ... (a few sentences about your program and the queries and charts)
'''
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pydeck as pdk
import numpy as np
import random
from PIL import Image

FILENAME = "skyscrapers.csv"
B_GRAPHS = ['bar', 'pie chart']
COLORS = ['', 'pink', 'blue', 'cyan', 'magenta', 'purple', 'orange']
DROPLIST = ['Home', 'By Structure Type', 'By Country', 'Map']


# create country dropdown list
def country_droplist():
    # create country dropdown list
    df_countries = pd.read_csv(FILENAME, usecols=['Country']).drop_duplicates(subset=['Country'])
    df_sort = df_countries.sort_values(['Country'], ascending=[True])
    countries = df_sort.values.flatten().tolist()
    country_list = []
    dict_countries = {}
    for c in countries:
        # get rid of leading space
        country = c
        c = c.strip()
        # if country name is two words, abbreviate with first letter of each word
        if ' ' in c:
            c_split = c.split()
            c_abbrev = c_split[0][0] + c_split[1][0]
        # if country is one work, keep as one word
        else:
            c_abbrev = c
        # add c_abbrev to list
        country_list.append(c_abbrev)
        # add country to dictionary
        dict_countries[c_abbrev] = country

    return dict_countries, country_list


# find how many skyscrapers are in the country in which the user will input
def country_df(df, country='United States'):
    # filter df to only rows where country is equal to the country the user inputs
    df_c = df[df['Country'] == country]
    df_c = df_c[['Name', 'Feet', 'Country', 'City', 'Year']]
    df_c = df_c.sort_values(['Feet', 'Name'], ascending=[False, True])
    return df_c


# list all of the data for the building type which I will get from user input.
def buiding_type(df, type='Skyscraper'):
    # filter df to only rows where type is equal to the type the user inputs
    df_type = df[df['Type'] == type]
    df_type = df_type[['Name', 'Feet', 'Country', 'City']]
    df_type = df_type.sort_values(['Feet', 'Name'], ascending=[False, True])
    st.subheader(f'{type}s Around the World')
    st.write(df_type)
    length = len(df_type)
    if length >= 10:
        set_value = 10
    else:
        set_value = length
    return df_type, length, set_value


# bar chart of the tallest buildings in a specific country or of the tallest skyscrapers(type of building) in the world
def bar_chart_country(df, country=' United States', color='orange'):
    # filter df to only rows where country is equal to the country the user inputs
    df_c = country_df(df, country)
    st.subheader(f'Structures in {country}')
    st.write(df_c)
    sorted_df = df_c.sort_values(['Feet', 'Name'], ascending=[True, True])
    fig, ax = plt.subplots()
    x = sorted_df['Name']
    y = sorted_df['Feet']
    num = len(x)
    plt.bar(x, y, color=color)

    plt.title(f'Tallest Structures in the {country}')
    plt.ylabel('Height in Feet')
    plt.xlabel('Name of Structure')
    # rotate labels to make it easier to read
    plt.xticks(rotation=90)
    ax.set_xticks(x)
    return plt


def bar_chart_building(df, num, type='Skyscraper', color='blue', ):
    bar_df = df.head(num)
    sorted_df = bar_df.sort_values(['Feet', 'Name'], ascending=[True, True])
    fig, ax = plt.subplots()
    x = sorted_df['Name']
    y = sorted_df['Feet']
    num = len(x)
    plt.bar(x, y, color=color)
    plt.title(f'Top {num} Tallest {type}s in the World')
    plt.ylabel('Height in Feet')
    plt.xlabel(f'Name of {type}')
    # rotate labels to make it easier to read
    plt.xticks(rotation=90)
    ax.set_xticks(x)
    return plt


def scatter(df, c1, c2):
    '''
    fig, ax = plt.subplots()
    df1 = country_df(df,c1)['Feet'].max()
    df2 = country_df(df,c2)['Feet'].max()
    st.write(df1)
    x = 'Tallest Structure'
    bar_width = .3
    ax.bar(x, df1, color='cyan', width=bar_width)
    # plot second bar with the low data
    ax.bar(x + bar_width, df2, color='purple', width=bar_width)
    '''
    df1 = country_df(df, c1)
    df2 = country_df(df, c2)
    st.write(df1)
    st.write(df2)
    df2 = country_df(df, c2)
    plt.scatter(df1['Year'], df1['Feet'], color='magenta', marker='*')
    plt.scatter(df2['Year'], df2['Feet'], color='blue', marker='o')
    plt.legend([c1, c2], loc=0)
    plt.title(f'Years Structures were built in{c1} and{c2}')
    plt.ylabel("Structure's Height in Feet")
    plt.xlabel('Year Built')

    return plt


def pie_chart(df):
    # get counts of types and write to screen
    df_pie = df.groupby('Type')['Name'].count()
    st.write(df_pie)

    type_list = []
    count_list = []
    types = df['Type'].drop_duplicates().values.flatten().tolist()
    # for each type, add type to list, get count of structures of that type and add count to another list
    for t in types:
        data = df[df['Type'] == t]['Name'].count().astype(float)
        type_list.append(t)
        count_list.append(data)
    # plot in pie chart
    color = ['mistyrose', 'bisque', 'pink', 'azure', 'lavender', 'honeydew', 'peachpuff']
    plt.pie(count_list, labels=type_list, autopct='%1.1f%%', colors=color)
    plt.axis('equal')
    plt.title('Tallest Structure Types')
    return plt


def map_graph():
    # map graph of the tallest skyscrapers around the world using the lat and long of the buildings
    st.subheader('Map of Tallest Structures Around the World')
    # create df for map
    df_map = pd.read_csv(FILENAME, usecols=['Name', 'Lat', 'Lon'])
    # rename lat and lon columns to lower case so that st.map will work
    df_map.columns = ['Name', 'lat', 'lon']
    # map df

    view_state = pdk.ViewState(
        latitude=df_map["lat"].mean(),
        longitude=df_map["lon"].mean(),
        zoom=2,
        pitch=0)

    layer1 = pdk.Layer('ScatterplotLayer',
                       data=df_map,
                       get_position='[lon, lat]',
                       get_radius=100000,
                       get_color=[random.randint(0, 2555), random.randint(0, 255), random.randint(0, 255)],
                       pickable=True
                       )

    # stylish tool tip
    tool_tip = {"html": "{Name}</br>({lat}, {lon})",
                "style": {"backgroundColor": "gray",
                          "color": "white"}
                }

    map2 = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=view_state,
                    layers=[layer1],
                    tooltip=tool_tip)

    st.pydeck_chart(map2)


def main():
    st.header("Structures Around the World")
    st.sidebar.header('Menu')
    choice = st.sidebar.selectbox('Select a category to display data:', DROPLIST)
    # read in file as a data frame
    df = pd.read_csv(FILENAME)
    if choice == 'Home':
        img = Image.open("skyscraper.jpg")
        st.image(img)
    elif choice == 'By Structure Type':
        graph = st.sidebar.radio('Chart Type', B_GRAPHS)

        if graph == 'bar':
            color = st.sidebar.selectbox('Select a color:', COLORS)
            # create type drop down
            type_list = df['Type'].drop_duplicates().tolist()
            types = st.sidebar.selectbox('Select a structure type:', type_list)
            # get df of building type
            result = buiding_type(df, types)
            bar_df = result[0]
            length = result[1]
            set_value = result[2]
            num = st.sidebar.slider('Select the amount of top structures displayed:',
                                    min_value=1, max_value=length, value=set_value)
            if color != '':
                st.pyplot(bar_chart_building(df, num, types, color))
            else:
                st.pyplot(bar_chart_building(df, num, types))

        elif graph == 'pie chart':
            st.pyplot(pie_chart(df))

    elif choice == 'By Country':
        # display country dropdown list and get dictionary
        country_results = country_droplist()
        # set list from results
        country_list = country_results[1]
        # set dictionary from results
        country_dict = country_results[0]
        # add selectbox for countries
        countries = st.sidebar.selectbox('Select a Country:', country_list)
        # get full country name from dictionary
        country = country_dict[countries]
        # checkbox for comparing in a scatter plot
        compare = st.sidebar.checkbox('Compare with another country', False)
        if not compare:
            color = st.sidebar.selectbox('Select a color:', COLORS)
            # make and display bar chart
            if color != '':
                st.pyplot(bar_chart_country(df, country, color))
            else:
                st.pyplot(bar_chart_country(df, country))
        else:
            countries2 = st.sidebar.selectbox('Select a Second Country:', country_list)
            country2 = country_dict[countries2]
            st.pyplot(scatter(df, country, country2))


    elif choice == 'Map':
        map_graph()


main()
