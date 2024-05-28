import pdfplumber
import pandas as pd
import os
from sqlalchemy import create_engine, inspect,text, Table, Column, Integer, String, Float, MetaData, DateTime,UniqueConstraint
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import re
from flask import Flask, request, render_template
import hashlib



app = Flask(__name__)

# MySQL database configuration
DATABASE_URI = 'mysql://admin:Pu$hkar121@localhost:3306/mydatabase'
TABLE_NAME = 'grndata'
HASH_TABLE_NAME = 'file_hashes'
engine = create_engine(DATABASE_URI)


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

hash_table = Table(
    HASH_TABLE_NAME, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('file_hash', String(64), nullable=False),
    Column('store_name', String(255)),
    Column('file_date', DateTime),
    UniqueConstraint('file_hash', 'store_name', 'file_date', name='unique_file')
)

# Create tables if they don't exist
metadata.create_all(engine)

# Function to check if a table exists in the database
def table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def compute_file_hash(file_path):
    hash_func = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def is_duplicate_file(file_hash, store_name, file_date):
    with engine.connect() as connection:
        query = text(f"""
        SELECT COUNT(*) 
        FROM {HASH_TABLE_NAME} 
        WHERE file_hash = :file_hash 
        AND store_name = :store_name 
        AND file_date = :file_date
        """)
        params = {'file_hash': file_hash, 'store_name': store_name, 'file_date': file_date}
        result = connection.execute(query, params).scalar()
        return result > 0


def store_file_hash(file_hash, store_name, file_date):
    with engine.connect() as connection:
        metadata.create_all(engine)
        query = text(f"""
        INSERT INTO {HASH_TABLE_NAME} (file_hash, store_name, file_date) 
        VALUES ('{file_hash}', '{store_name}', '{file_date}')
        """)        
        try:
            connection.execute(query)
            connection.commit()  
            print("Data inserted into hash table successfully!")
        except SQLAlchemyError as e:
            print(f"Error inserting data into hash table: {e}")
        
    
# Function to store data to MySQL database
def store_to_db(df, engine, table):
    try:
        if not table_exists(engine, table.name):
            metadata.create_all(engine)
            df.to_sql(table.name, con=engine, if_exists='append', index=False)
            print(f"Table '{table.name}' created and data has been stored successfully!")
        else:
            df.to_sql(table.name, con=engine, if_exists='append', index=False)
            print(f"Data has been appended to the existing table '{table.name}' successfully!")
        
    except SQLAlchemyError as e:
        print(f"Error storing data to the database: {e}")

# Function to process a single PDF file
def process_pdf(input_file):
    file_size = os.path.getsize(input_file)
    file_hash = compute_file_hash(input_file)

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

    if is_duplicate_file(file_hash, place_name, file_date):
        print(f"Duplicate file detected for {place_name} on {file_date}. Skipping processing.")
        return
    
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

    store_to_db(df, engine, data_table)
    store_file_hash(file_hash, place_name, file_date)
from flask import jsonify

@app.route('/FILEDATA', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if files are present in the request
        if 'files' not in request.files:
            return jsonify(error="No file part in the request"), 400

        files = request.files.getlist('files')
        response_data = []

        # Process each file
        for file in files:
            if file.filename == '':
                response_data.append({"filename": file.filename, "success": False, "error": "No selected file"})
                continue
            if file:
                # Save the file temporarily
                temp_file_path = os.path.join('temp', file.filename)
                file.save(temp_file_path)

                try:
                    # Process the PDF file
                    process_pdf(temp_file_path)
                    response_data.append({"filename": file.filename, "success": True})
                except Exception as e:
                    response_data.append({"filename": file.filename, "success": False, "error": str(e)})

                # Remove the temporary file
                os.remove(temp_file_path)

        return jsonify(response_data)

    return render_template('test.html')


if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(debug=True)