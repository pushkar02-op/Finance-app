# Flask MySQL Database App

This project demonstrates a Flask application that connects to an AWS RDS MySQL database, retrieves and processes data, and provides various endpoints for data operations. The application uses SQLAlchemy for database interactions and Pandas for data manipulation.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Directory Structure](#directory-structure)
- [License](#license)

## Prerequisites

- Python 3.8+
- Flask
- SQLAlchemy
- Pandas
- pdfplumber
- AWS RDS MySQL instance

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. Create a virtual environment and activate it:

```sh
Copy code
python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
```

3. Install the required dependencies:

```sh
Copy code
pip install -r requirements.txt
Set up the database configuration in the app.py file:
```

4. Update the following variables with your database credentials:

python
Copy code
DB_USERNAME = 'admin'
DB_PASSWORD = 'Pu$hkar121'
DB_HOST = 'mydatabase.cnqug0sk235z.ap-south-1.rds.amazonaws.com'
DB_PORT = '3306'
DB_NAME = 'mydatabase'
Configuration
Ensure that your AWS RDS instance is properly set up and accessible. Update the DATABASE_URI in the app.py file accordingly.

Running the Application
Start the Flask application:

sh
Copy code
python app.py
Open your web browser and navigate to http://127.0.0.1:5000/.

API Endpoints
GET /data
Retrieve daily spent and received data within a date range.

Parameters:

start_date (required): Start date in YYYY-MM-DD format.
end_date (required): End date in YYYY-MM-DD format.
Response:

JSON object containing the daily summary of spent, received, and profit/loss data.
POST /submit
Submit spent data.

Parameters:

date (required): Date of the record.
item (required): Item name.
qty (required): Quantity.
price (required): Price per unit.
total (required): Total amount.
Response:

Message indicating the success of the operation.
GET /get_data
Retrieve spent data for a specific date.

Parameters:

reqdate (required): Date in YYYY-MM-DD format.
Response:

JSON object containing the spent data for the specified date.
POST /FILEDATA
Upload and process PDF files.

Parameters:

files (required): PDF files to be processed.
Response:

JSON object indicating the success or failure of each file processing.
POST /updateRow
Update a row in the database.

Parameters:

SR_NO (required): Serial number of the row to be updated.
QUANTITY (required): Updated quantity.
PRICE (required): Updated price.
TOTAL (required): Updated total amount.
Response:

JSON object indicating the success of the operation.
POST /deleteRow
Delete a row from the database.

Parameters:

SR_NO (required): Serial number of the row to be deleted.
Response:

JSON object indicating the success of the operation.
Database Schema
spent_data Table
id (Integer, Primary Key)
date (DateTime, Not Null)
item (String(100), Not Null)
qty (Float, Not Null)
price (Float, Not Null)
total (Float, Not Null)
grndata Table
Sr_No (Integer, Primary Key, Auto-increment)
HSN_CODE (String(255))
ITEM_CODE (Integer)
Item (String(255))
Quantity (Float)
UOM (String(10))
Price (Float)
Total (Float)
Date (DateTime)
StoreName (String(255))
file_hashes Table
id (Integer, Primary Key, Auto-increment)
file_hash (String(64), Not Null, Unique)
store_name (String(255))
file_date (DateTime)
Unique Constraint on file_hash, store_name, and file_date
Directory Structure
arduino
Copy code
project-root/
├── app.py
├── requirements.txt
├── templates/
│ └── main.html
├── static/
│ └── ...
└── temp/
└── ...
