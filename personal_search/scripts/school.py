import pandas as pd
from tabulate import tabulate
import folium
from folium.plugins import Search
from geopy.distance import geodesic

# Load the data file
file_path = r'/personal_search/data/School_choise.xlsm'
df = pd.read_excel(file_path)

# Set display option to show all columns
pd.set_option('display.max_columns', None)

# Convert columns to numeric, errors='coerce' will convert non-numeric values to NaN
df['Andel (%) elever behöriga till yrkesprog.'] = pd.to_numeric(df['Andel (%) elever behöriga till yrkesprog.'], errors='coerce')
df['Andel (%) elever behöriga till estetiskt program'] = pd.to_numeric(df['Andel (%) elever behöriga till estetiskt program'], errors='coerce')
df['Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program'] = pd.to_numeric(df['Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program'], errors='coerce')
df['Andel (%) elever som uppfyllt betygskriterierna i alla ämnen'] = pd.to_numeric(df['Andel (%) elever som uppfyllt betygskriterierna i alla ämnen'], errors='coerce')
df['Genomsnittligt meritvärde (17 ämnen)'] = pd.to_numeric(df['Genomsnittligt meritvärde (17 ämnen)'], errors='coerce')

# Calculate average scores
avg_yrkesprog = df['Andel (%) elever behöriga till yrkesprog.'].mean()
avg_estetiskt = df['Andel (%) elever behöriga till estetiskt program'].mean()
avg_nat_tech = df['Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program'].mean()
avg_betyg = df['Andel (%) elever som uppfyllt betygskriterierna i alla ämnen'].mean()
avg_merit = df['Genomsnittligt meritvärde (17 ämnen)'].mean()

# Display the Average scores
print(f"\nAverage score for 'Andel (%) elever behöriga till yrkesprog.': {avg_yrkesprog:.2f}")
print(f"Average score for 'Andel (%) elever behöriga till estetiskt program': {avg_estetiskt:.2f}")
print(f"Average score for 'Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program': {avg_nat_tech:.2f}")
print(f"Average score for 'Andel (%) elever som uppfyllt betygskriterierna i alla ämnen': {avg_betyg:.2f}")
print(f"Average score for 'Genomsnittligt meritvärde (17 ämnen)': {avg_merit:.2f}")

# List schools above or at the average for 'Andel (%) elever behöriga till ...'
schools_above_avg_yrkesprog = df[df['Andel (%) elever behöriga till yrkesprog.'] >= avg_yrkesprog][['Skola', 'elev_år', 'Profil_Inriktning']]
schools_above_avg_estetiskt = df[df['Andel (%) elever behöriga till estetiskt program'] >= avg_estetiskt][['Skola', 'elev_år', 'Profil_Inriktning']]
schools_above_avg_nat_tech = df[df['Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program'] >= avg_nat_tech][['Skola', 'elev_år', 'Profil_Inriktning']]
schools_above_avg_betyg = df[df['Andel (%) elever som uppfyllt betygskriterierna i alla ämnen'] >= avg_betyg][['Skola', 'elev_år', 'Profil_Inriktning']]
schools_above_avg_merit = df[df['Genomsnittligt meritvärde (17 ämnen)'] >= avg_merit][['Skola', 'elev_år', 'Profil_Inriktning']]


# Display the DataFrame using tabulate
print("Schools at or above average for 'Andel (%) elever behöriga till yrkesprog.':")
print(tabulate(schools_above_avg_yrkesprog, headers='keys', tablefmt='pretty'))

# Add a blank line
print("\n")

print("Schools at or above average for 'Andel (%) elever behöriga till estetiskt program':")
print(tabulate(schools_above_avg_estetiskt, headers='keys', tablefmt='pretty'))

# Add a blank line
print("\n")

print("Schools at or above average for 'Andel (%) elever behöriga till Naturvetenskapligt och tekniskt program':")
print(tabulate(schools_above_avg_nat_tech, headers='keys', tablefmt='pretty'))

# List schools with specific profile
profile_keywords = ['språk', 'MA', 'NO', 'Framtidsinriktning']
schools_with_profiles = df[df['Profil_Inriktning'].str.contains('|'.join(profile_keywords), case=False, na=False)][['Skola', 'elev_år', 'Profil_Inriktning']]

print("\nSchools with specific profile (språk, MA, NO, Framtidsinriktning):")
print(tabulate(schools_with_profiles, headers='keys', tablefmt='pretty'))

# List schools with gymnasium
schools_with_gymnasium = df[df['Finns_Gymnasiumskolan'].str.lower() == 'ja'][['Skola', 'elev_år', 'Profil_Inriktning']]

print("\nSchools with Gymnasium Schools included:")
print(tabulate(schools_with_gymnasium, headers='keys', tablefmt='pretty'))

#Rank schools based on multiple conditions
# Assign points based on ranking
def assign_points(dataframe, num_points):
    points = {}
    for i, row in dataframe.iterrows():
        points[row['Skola']] = num_points - i
    return points

points_yrkesprog = assign_points(schools_above_avg_yrkesprog, 9)
points_estetiskt = assign_points(schools_above_avg_estetiskt, 9)
points_nat_tech = assign_points(schools_above_avg_nat_tech, 9)
points_betyg = assign_points(schools_above_avg_betyg, 9)
points_merit = assign_points(schools_above_avg_merit, 9)
points_profiles = assign_points(schools_with_profiles, 5)

# Sum up the points for each school
total_points = {}
for school in set(points_yrkesprog) | set(points_estetiskt) | set(points_nat_tech) | set(points_betyg) | set(points_betyg) | set(points_profiles):
    total_points[school] = (points_yrkesprog.get(school, 0) +
                            points_estetiskt.get(school, 0) +
                            points_nat_tech.get(school, 0) +
                            points_betyg.get(school, 0) +
                            points_merit.get(school, 0) +
                            points_profiles.get(school, 0))

# Convert to DataFrame for sorting
total_points_df = pd.DataFrame(list(total_points.items()), columns=['Skola', 'Total Points'])
total_points_df = total_points_df.merge(df[['Skola', 'elev_år', 'Profil_Inriktning']], on='Skola')

# Sort the schools by total points
sorted_schools = total_points_df.sort_values(by='Total Points', ascending=False)

print("\nSchools sorted by total points, based on Profil_Inriktning and highest scores in behörigheten till Gymnasium:")
print(tabulate(sorted_schools, headers='keys', tablefmt='pretty'))

# Distance from "Home" to school
# Convert sample data to DataFrame
df = pd.DataFrame(data)

# Coordinates for 'Home'
home_coords = (58.40653, 15.56610)

# Create a map with satellite view
m = folium.Map(location=home_coords, zoom_start=13, tiles='OpenStreetMap')

# Add 'Home' marker
folium.Marker(
    location=home_coords,
    popup='Home',
    icon=folium.Icon(color='pink')
).add_to(m)

# Create a FeatureGroup for the schools to use with the Search plugin
school_markers = folium.FeatureGroup(name='Schools')

# Calculate distances and add school markers
for i, row in df.iterrows():
    school_coords = (row['Latitude'], row['Longitude'])
    distance = geodesic(home_coords, school_coords).km
    marker = folium.Marker(
        location=school_coords,
        popup=f"{row['Skola']}\nDistance: {distance:.2f} km",
        icon=folium.Icon(color='darkpurple')
    )
    marker.add_to(school_markers)

# Add the FeatureGroup with school markers to the map
school_markers.add_to(m)

# Add the Search plugin
search = Search(
    layer=school_markers,
    search_label='popup',
    placeholder='Search for a school',
    collapsed=False
)
search.add_to(m)

# Display the map
m
