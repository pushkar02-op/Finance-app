import pdfplumber
import pandas as pd
import os
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from sqlalchemy import create_engine, inspect, Table, Column, Integer, String, Float, MetaData, DateTime
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import re

# MySQL database configuration
DATABASE_URI = 'mysql://admin:Pu$hkar121@localhost:3306/mydatabase'
TABLE_NAME = 'grndata'
engine = create_engine(DATABASE_URI)

# Dictionary to keep track of processed files by date and size
processed_files = {}

# Function to check if a table exists in the database
def table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

# Define table schema
metadata = MetaData()

data_table = Table(
    TABLE_NAME, metadata,
    Column('Sr_No', Integer, primary_key=True, autoincrement=True),
    Column('HSN_CODE', String(255)),
    Column('ITEM_CODE', Integer),
    Column('Item', String(255)),
    Column('Quantity', String(255)),
    Column('UOM', String(10)),
    Column('Price', Float),
    Column('Total', Float),
    Column('Date', DateTime),
    Column('StoreName', String(255))
)

# Function to store data to MySQL database
def store_to_db(df, engine, table):
    try:
        if not table_exists(engine, table.name):
            # Create the table with column headers if it does not exist
            metadata.create_all(engine)
            df.to_sql(table.name, con=engine, if_exists='append', index=False)
            print(f"Table '{table.name}' created and data has been stored successfully!")
        else:
            # Insert only rows if the table already exists
            df.to_sql(table.name, con=engine, if_exists='append', index=False)
            print(f"Data has been appended to the existing table '{table.name}' successfully!")
    except SQLAlchemyError as e:
        print(f"Error storing data to the database: {e}")

# Function to process a single PDF file
def process_pdf(input_file, output_folder):
    file_size = os.path.getsize(input_file)

    # Extract tables from PDF using pdfplumber
    with pdfplumber.open(input_file) as pdf:
        tables = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.extend(table)

    # Convert tables to Pandas DataFrame
    df = pd.DataFrame(tables)

    # To get place name
    for index, row in df.iterrows():
        if 'Site Name' in row.values:
            # Get the index of 'Site Name' column
            site_name_index = row.index[row == 'Site Name'][0]

            # Get the place name from the next row in the same column
            place_name = df.iloc[index + 1, site_name_index].strip().replace(' ','_')

            break  # Exit loop after finding 'Site Name'
        
    #Extract Date
    date_str = re.search(r'(\d{2}\.\d{2}\.\d{4})', df.iloc[0, 2]).group(1)
    file_date = datetime.strptime(date_str, "%d.%m.%Y")
    df['Date'] = file_date

    # Check if the file has already been processed
    if (file_date, file_size) in processed_files:
        print(f"File '{input_file}' with date {file_date} and size {file_size} has already been processed. Skipping.")
        return
    else:
        processed_files[(file_date, file_size)] = True
    df=df[8:]


    # Find the index of the first occurrence of 'Sr.No'
    first_occurrence_index = df[0].tolist().index('Sr.No')

    # Filter out rows where the first column has 'Sr.No', except for the first occurrence
    df_filtered = pd.concat([df.iloc[first_occurrence_index:first_occurrence_index+1], df[df[0] != 'Sr.No']])

    # Reset the index of the DataFrame
    df_filtered.reset_index(drop=True, inplace=True)

    df=df_filtered

    # Find the index of the first occurrence of 'Grand Total of Qty'
    first_grand_total_index = df[df[0] == 'Grand Total of Qty'].index.tolist()

    if first_grand_total_index:
        # If 'Grand Total of Qty' exists in the DataFrame
        first_grand_total_index = first_grand_total_index[0]
        # Slice the DataFrame to include rows only up to the first occurrence of 'Grand Total of Qty'
        df_filtered = df.iloc[:first_grand_total_index ]
    else:
        # If 'Grand Total of Qty' does not exist in the DataFrame, keep the original DataFrame
        df_filtered = df.copy()

    df=df_filtered

    # df['Date']  = pd.to_datetime(df[3].str.extract(r'(\d{2}.\d{2}.\d{4})', expand=False),format="%d.%m.%Y")

    df['StoreName'] = place_name

    # Extract the date from the 'Date' column
    date_from_column = df.at[1, 'Date']
    datetime_obj=datetime.strptime(str(date_from_column), '%Y-%m-%d %H:%M:%S') 
    date_from_column = datetime_obj.strftime('%Y_%m_%d')

    # Remove date data from item name
    df[3] = df[3].str.replace(r'\n\d{2}.\d{2}.\d{4}\n\w{4}$', '', regex=True)

    # Remove columns 0, 6, 8 and 9
    df = df.drop(columns=[0, 6, 8, 9])

    #Remove the 1st row
    df = df.iloc[1:]
    
    # Add proper column names to the DataFrame
    df.columns = ['HSN_CODE', 'ITEM_CODE', 'Item',  'Quantity', 'UOM','Price','Total', 'Date', 'StoreName']

    # Function to clean the data
    def clean_data(value):
        return value.split('\n')[0]
    
    # Data Cleaning
    df['Total'] = df['Total'].str.replace(',','')
    df['Item'] = df['Item'].str.strip("._/\n")
    df['HSN_CODE'] = df['HSN_CODE'].str.replace('\n','')
    df['ITEM_CODE'] = df['ITEM_CODE'].apply(clean_data)


    # Change data types of the DataFrame columns
    df = df.astype({
        'Quantity': 'float',
        'Price': 'float',
        'Total': 'float'
    })
    df['Quantity'] = round(df['Quantity'], 2)
    df['Price'] = round(df['Price'], 2)
    df['Total'] = round(df['Total'], 2)

    # Change the output file name and add the date from the column in the file name
    excel_file_path = f"{output_folder}\\GRN_{place_name}_{date_from_column}.xlsx"
    
    # Function to create a unique file name
    def get_unique_filename(base_path, base_name, extension):
        counter = 1
        new_path = f"{base_path}\\{base_name}{extension}"
        while os.path.exists(new_path):
            new_path = f"{base_path}\\{base_name}_{counter}{extension}"
            counter += 1
        return new_path    
    
    # Check if the file already exists
    if not os.path.exists(excel_file_path):
        # Export DataFrame to an Excel file with the new file name
        df.to_excel(excel_file_path, index=False)
        print(f"Data has been extracted from the PDF and saved to Excel file: {excel_file_path}")

        # Store data to MySQL database
        store_to_db(df, engine, data_table)
    else:
        excel_file_path = get_unique_filename(output_folder, f"GRN_{place_name}_{date_from_column}", ".xlsx")
        # Export DataFrame to an Excel file with the new file name
        df.to_excel(excel_file_path, index=False)
        print(f"Data has been extracted from the PDF and saved to Excel file: {excel_file_path}")

        # Store data to MySQL database
        store_to_db(df, engine, data_table)


# Source folder containing PDF files
source_folder = "DATA\\SOURCE_FILES\\"

# Destination folder to save output files
destination_folder = "DATA\\TARGET_FILES\\"

# # Get a list of all PDF files in the source folder
# pdf_files = glob.glob(os.path.join(source_folder, "*.pdf"))

# # Process each PDF file
# for pdf_file in pdf_files:
   
#     # Process the PDF file and save the output file in the output folder
#     process_pdf(pdf_file, destination_folder)


class PDFHandler(FileSystemEventHandler):
    def __init__(self, output_folder):
        self.output_folder = output_folder

    def on_created(self, event):
        if event.src_path.endswith((".pdf",".PDF")):
            print(f"New PDF file detected: {event.src_path}")
            time.sleep(1)
            process_pdf(event.src_path, self.output_folder)


# Set up event handler and observer
event_handler = PDFHandler(destination_folder)
observer = Observer()
observer.schedule(event_handler, path=source_folder, recursive=False)

# Start observer
observer.start()
print(f"Monitoring {source_folder} for new PDF files...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()