'''
Litigation Support Data Quality Tracker
In order to keep track of LM data error validation progress, the Data Quality Tracker ingests data from LM and creates
summary statistics and charts from the Data Quality Team
1) Extract the data (monthly) from SQL into the directory folder
2) Save a new file name
3) Run the script
'''


import os
import pandas as pd
import openpyxl as ox


directory = 'C:/directory_file_path'

data_frames_appear = []
data_frames_matter = []
data_frames_init_charge = []

#Read and stack files
for file in os.listdir(directory):
    if file.endswith('.xlsx'):
        file_path = os.path.join(directory, file)

        try:
            df_appear = pd.read_excel(file_path, sheet_name='Case_Appearance')
            data_frames_appear.append(df_appear)

            df_matter = pd.read_excel(file_path, sheet_name='Matter')
            data_frames_matter.append(df_matter)

            try:
                df_init_charge = pd.read_excel(file_path, sheet_name='Init_Top_Charge')
                data_frames_init_charge.append(df_init_charge)
            except ValueError:
                pass

        except Exception as e:
            print(f"Skipping {file}: e")

#Format Case Appearance Data
data_appear = pd.concat(data_frames_appear)
data_appear['date_updated'] = pd.to_datetime(data_appear['date_updated'], format='%m/%d/%Y %H:%M') #date updated is the unique id
data_appear = data_appear.sort_values(by='date_updated', ascending=False)
data_appear = data_appear.drop_duplicates(subset=['date_updated','updated_by'])

data_appear.to_excel('C:/Project_Write_Path/Project.xlsx', index=False)

#data_matter = pd.concat(data_frames_appear)

#data_init_charge = pd.concat(data_frames_appear)