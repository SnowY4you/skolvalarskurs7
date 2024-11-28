import pandas as pd

# Read the .xlsm file
df = pd.read_excel(r'C:\Users\svanb\OneDrive\Python\Noah_School\raw_data\School_choise_Noah.xlsm')

# Set the option to display all columns
pd.set_option('display.max_columns', None)

# Display the dataframe
print("The dataframe is:")
print(df.columns.values)

# Print the 'Profil_Inriktning' column
print("\nValues in the 'Profil_Inriktning' column are:")
print(df['Profil_Inriktning'])