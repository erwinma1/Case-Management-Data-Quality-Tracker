'''
Litigation Support Data Quality Tracker
In order to keep track of LM data error validation progress, the Data Quality Tracker ingests data from LM and creates
summary statistics and charts from the Data Quality Team.

Data collection began in Nov 2025. Previous dates are undercounted due to updated_by fields being overwritten resulting
in data loss.

1) Extract the data (every 2 weeks) from SQL into the directory folder
2) Save a new file name
3) Run the script

For any questions contact ema@legal-aid.org
'''


import os
import pandas as pd
import openpyxl as ox

#Update file paths
directory = 'C:/Users/ema/PycharmProjects LAS/LM Data Quality Tracker/Archive'
write_path = 'C:/Users/ema/PycharmProjects LAS/Litigation Support Data Quality Tracker/Data Quality Dashboard 4.9.26.xlsx'
test_path = 'C:/Users/ema/Documents/PycharmProjects LAS/Litigation Support Data Quality Tracker/Data Quality Case Appearance Error 4.9.26.xlsx'

#----------------- Process LM NCD and Init Charge Data ---------------#
#Extract data from LM and weekly cleaning lists

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


#----------------- Process D3 Dashboard Data ---------------#
#Process data extract files from D3 Dashboard
ctc_dir = 'C:/Users/ema/Documents/SQL Server Management Studio/LM CDP Dashboard No Current Top Charge/Dashboard Error Extracts'

data_frames_ctc_error = []

#Read and stack files
for file in os.listdir(ctc_dir):
    if file.endswith('.xlsx'):
        ctc_path = os.path.join(ctc_dir, file)

        try:
            df_ctc_error = pd.read_excel(ctc_path, sheet_name='Export', skipfooter=3)

            creation_time = os.path.getctime(ctc_path)
            df_ctc_error['file_created_date'] = pd.to_datetime(creation_time, unit='s')

            data_frames_ctc_error.append(df_ctc_error)

        except Exception as e:
            print(f"Error reading {file}: {e}")

#----------------- Process Active Case Backlog  ---------------#
ncd_dir = 'C:/Users/ema/Documents/PycharmProjects LAS/LM Cleaning and Notes Joining/Inputs/New File/Archive'

data_frames_ncd = []

for file in os.listdir(ncd_dir):
    if file.endswith('.xlsx'):
        ncd_path = os.path.join(ncd_dir, file)

        try:
            df_ncd = pd.read_excel(ncd_path)

            ncd_creation_time = os.path.getctime(ncd_path)
            df_ncd['file_created_date'] = pd.to_datetime(ncd_creation_time, unit='s')

            data_frames_ncd.append(df_ncd)

        except Exception as e:
            print(f"Error reading {file}: {e}")

data_ncd = pd.concat(data_frames_ncd, ignore_index=True)
data_ncd['date_opened'] = pd.to_datetime(data_ncd['date_opened'], format='%m/%d/%Y %H:%M', errors='coerce')
data_ncd['latest_appear_date'] = pd.to_datetime(data_ncd['latest_appear_date'], format='%m/%d/%Y %H:%M', errors='coerce')
data_ncd = data_ncd.sort_values(by='file_created_date', ascending=False)

pivot_ncd = pd.DataFrame(data=data_ncd, columns=['matter_key', 'latest_appear_date', ]) # 'date_opened','file_created_date'
pivot_ncd = pivot_ncd.drop_duplicates(subset=['matter_key'], keep='first')
pivot_ncd['latest_appear_date'] = pivot_ncd['latest_appear_date'].dt.to_period('Y').dt.to_timestamp()
#pivot_ncd['file_created_date'] = pivot_ncd['file_created_date'].dt.to_period('M').dt.to_timestamp()
pivot_ncd = pd.pivot_table(data=pivot_ncd, values='matter_key', index=['latest_appear_date'], aggfunc='count')
pivot_ncd = pivot_ncd.reset_index()


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


#------------------ Format Curr Top Charge Data ------------------#
data_ctc_error = pd.concat(data_frames_ctc_error)
pivot_ctc_error = data_ctc_error

pivot_ctc_error['file_created_date'] = pd.to_datetime(pivot_ctc_error['file_created_date'])
pivot_ctc_error = data_ctc_error.sort_values(by='file_created_date', ascending=False)
pivot_ctc_error = pd.DataFrame(data=pivot_ctc_error, columns=['docket_number','file_created_date'])

pivot_ctc_error = pd.pivot_table(pivot_ctc_error, values='docket_number', index='file_created_date', aggfunc='count')
pivot_ctc_error = pivot_ctc_error.rename(columns={'docket_number': 'ctc_error_count'})
pivot_ctc_error = pivot_ctc_error.reset_index()

#------------------------- Write File --------------------------#

#write dashboard
with pd.ExcelWriter(write_path, engine='openpyxl') as writer:
    pivot_appear.to_excel(writer, sheet_name='Case_Appearance_Corrections', index=False)
    pivot_matter.to_excel(writer, sheet_name='Matter_Corrections', index=False)
    pivot_intcharge.to_excel(writer, sheet_name='Init_Top_Charge_Corrections', index=False)
    pivot_ctc_error.to_excel(writer, sheet_name='Curr_Top_Charge_Errors', index=False)
    pivot_ncd.to_excel(writer, sheet_name='NCD_Error_Backlog', index=False)
