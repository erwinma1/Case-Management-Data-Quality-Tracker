'''
Litigation Support Data Quality Tracker
In order to keep track of LM data error validation progress, the Data Quality Tracker ingests data from LM and creates
summary statistics and charts from the Data Quality Team.

Data collection began in Nov 2025. Previous dates are undercounted due to updated_by fields being overwritten resulting
in data loss.

1) Extract the data (monthly) from SQL into the directory folder
2) Save a new file name
3) Run the script

For any questions contact ema@legal-aid.org
'''


import os
import pandas as pd
import openpyxl as ox

#Update file paths

directory = 'C:/Users/ema/Documents/SQL Server Management Studio/LM Data Quality Tracker/Archive'
write_path = 'C:/Users/ema/Documents/PycharmProjects LAS/Litigation Support Data Quality Tracker/Data Quality Dashboard 3.3.26.xlsx'

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

#------------------Format Case Appearance Data------------------#
data_appear = pd.concat(data_frames_appear)
data_appear['date_updated'] = pd.to_datetime(data_appear['date_updated'], format='%m/%d/%Y %H:%M', errors='coerce') #date updated + updated by are the unique ids
data_appear = data_appear.sort_values(by='date_updated', ascending=False)
#remove dupes
data_appear = data_appear.drop_duplicates(subset=['date_updated','updated_by'])

pivot_appear = data_appear

#format date
pivot_appear['update_date'] = pivot_appear['date_updated'].dt.to_period('M').dt.to_timestamp()

#drop columns
pivot_appear = pivot_appear.drop(columns=['date_updated','updated_by'])

pivot_appear = pd.pivot_table(data=pivot_appear, values='appear_count', index='update_date', aggfunc='sum')
pivot_appear = pivot_appear.reset_index()

#-------------------------Format Matter Data--------------------------#
data_matter = pd.concat(data_frames_matter)

data_matter['date_updated'] = pd.to_datetime(data_matter['date_updated'], errors='coerce')
data_matter['update_date'] = data_matter['date_updated'].dt.to_period('M').dt.to_timestamp()
data_matter = data_matter.drop_duplicates(subset=['date_updated','updated_by'])


pivot_matter = data_matter.drop(columns=['date_updated','updated_by'])

pivot_matter = pd.pivot_table(data=pivot_matter, values='matter_count', index='update_date', aggfunc='sum')

pivot_matter = pivot_matter.reset_index()

#-------------------------Format Init Top Charge Data--------------------------#
data_intcharge = pd.concat(data_frames_init_charge)

data_intcharge['date_added'] = pd.to_datetime(data_intcharge['date_added'], errors='coerce')
data_intcharge['added_date'] = data_intcharge['date_added'].dt.to_period('M').dt.to_timestamp()
data_intcharge = data_intcharge.drop_duplicates(subset=['date_added', 'added_by'])


pivot_intcharge = data_intcharge

pivot_intcharge = data_intcharge.drop(columns=['charge_key', 'added_by', 'date_added'])

pivot_intcharge = pd.pivot_table(data=pivot_intcharge, values='matter_key', index='added_date', aggfunc='count')

pivot_intcharge = pivot_intcharge.reset_index()

#------------------------- Write File --------------------------#

with pd.ExcelWriter(write_path, engine='openpyxl') as writer:
    pivot_appear.to_excel(writer, sheet_name='Case_Appearance', index=False)
    pivot_matter.to_excel(writer, sheet_name='Matter', index=False)
    pivot_intcharge.to_excel(writer, sheet_name='Init_Top_Charge', index=False)

