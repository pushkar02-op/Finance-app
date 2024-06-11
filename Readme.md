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

2. **Create a virtual environment and activate it:**

   ```sh
   python -m venv venv
   source venv/bin/activate # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up the database configuration:**
   Update the following environment variables with your database credentials:
   ```sh
   export DB_HOST="mydatabase.cnqug0sk235z.ap-south-1.rds.amazonaws.com"
   export DB_USER="admin"
   export DB_PASSWORD='Pushkar&121'
   export DB_NAME="mydatabase"
   ```

## Running the Application

1. **Start the Flask application:**

   ```sh
   python app.py
   ```

2. **Open your web browser and navigate to:**
   ```
   http://127.0.0.1:5000/
   ```

## API Endpoints

## Endpoints

### 1. Home Endpoint

#### `GET /`

**Description:** Renders the main HTML page.

**Request Parameters:** None

**Response:**

- Renders the `main.html` page.

### 2. Submit Data Endpoint

#### `POST /submit`

**Description:** Submits data related to spent items to the database.

**Request Parameters:**

- `date` (string): Date of the transaction.
- `store` (string): Store name.
- `item` (string): Item name.
- `qty` (float): Quantity of the item.
- `price` (float): Price of the item.
- `total` (float): Total cost of the item.

**Response:**

- `200 OK`: "Data submitted successfully!"

### 3. Get Data Endpoint

#### `GET /get_data`

**Description:** Retrieves spent data for a specific date.

**Request Parameters:**

- `reqdate` (string): Date for which the data is requested.

**Response:**

- `200 OK`: JSON array of data objects containing:
  - `date` (string)
  - `store` (string)
  - `item` (string)
  - `qty` (float)
  - `price` (float)
  - `total` (float)

### 4. Data Analysis Endpoint

#### `GET /data`

**Description:** Retrieves a summary of spent and received data between specified dates, including daily profit/loss and other costs.

**Request Parameters:**

- `start_date` (string): Start date for the data range.
- `end_date` (string): End date for the data range.

**Response:**

- `200 OK`: JSON array of summarized data objects containing:
  - `date` (string)
  - `total_spent` (float)
  - `total_received` (float)
  - `daily_profit_loss` (float)
  - `other_costs` (float)
  - `items` (array): List of item objects with details.

### 5. File Data Endpoint

#### `POST /FILEDATA`

**Description:** Uploads and processes PDF files to extract and store data in the database.

**Request Parameters:**

- Files are uploaded through a multipart/form-data request with `files` field.

**Response:**

- `200 OK`: JSON array of objects containing:
  - `filename` (string)
  - `success` (boolean)
  - `error` (string, optional)

#### `GET /FILEDATA`

**Description:** Retrieves data from the database for a specific date, sorted by a specified column in a specified order.

**Request Parameters:**

- `reqdate` (string): Date for which the data is requested.
- `column` (string): Column name to sort by.
- `sortorder` (string): Order to sort the column (ASC or DESC).

**Response:**

- `200 OK`: JSON array of data objects containing:
  - `SR_NO` (integer)
  - `ITEM` (string)
  - `QUANTITY` (float)
  - `PRICE` (float)
  - `TOTAL` (float)
  - `STORENAME` (string)

### 6. Update Row Endpoint

#### `POST /updateRow`

**Description:** Updates a specific row in the database.

**Request Parameters:**

- JSON object containing:
  - `SR_NO` (integer): Serial number of the row to update.
  - `QUANTITY` (float): Updated quantity.
  - `PRICE` (float): Updated price.
  - `TOTAL` (float): Updated total.

**Response:**

- `200 OK`: JSON object containing `success` (boolean).

### 7. Delete Row Endpoint

#### `POST /deleteRow`

**Description:** Deletes a specific row from the database.

**Request Parameters:**

- JSON object containing:
  - `SR_NO` (integer): Serial number of the row to delete.

**Response:**

- `200 OK`: JSON object containing `success` (boolean).

## Database Schema

1. **spent_data Table**

   - `id` (Integer, Primary Key)
   - `date` (DateTime, Not Null)
   - `store` (String(50), Not Null)
   - `item` (String(100), Not Null)
   - `qty` (Float, Not Null)
   - `price` (Float, Not Null)
   - `total` (Float, Not Null)

2. **grndata Table**

   - `Sr_No` (Integer, Primary Key, Auto-increment)
   - `HSN_CODE` (String(255))
   - `ITEM_CODE` (Integer)
   - `Item` (String(255))
   - `Quantity` (Float)
   - `UOM` (String(10))
   - `Price` (Float)
   - `Total` (Float)
   - `Date` (DateTime)
   - `StoreName` (String(255))

3. **file_hashes Table**
   - `id` (Integer, Primary Key, Auto-increment)
   - `file_hash` (String(64), Not Null, Unique)
   - `store_name` (String(255))
   - `file_date` (DateTime)
   - Unique Constraint on `file_hash`, `store_name`, and `file_date`

### Directory Structure

project-root/

├── app.py

├── requirements.txt

├── templates/

│ └── main.html

├── static/

│ └── ...
└── temp/

└── ...

## Releasing a New Version

1. **Make changes and push them to GitHub:**

2. **Login to EC2:**

3. **Run these commands in the same order:**
   ```sh
   sudo su
   source /home/ubuntu/flask_app_env/bin/activate && pip install --upgrade pip
   cd /home/ubuntu/flask-app
   git pull origin main
   sudo systemctl daemon-reload
   sudo systemctl restart flask-app.service
   sudo systemctl enable flask-app.service
   ```
