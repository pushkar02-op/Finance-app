from sqlalchemy import create_engine
import pandas as pd
from flask import Flask, render_template, jsonify


# Initialize Flask app
app = Flask(__name__)

# MySQL database configuration
DATABASE_URI = 'mysql://admin:Pu$hkar121@localhost:3306/mydatabase'

# Create a connection to the database
engine = create_engine(DATABASE_URI)

# Function to retrieve data from tables
def get_data_from_db(engine, table_name):
    query = f"SELECT * FROM {table_name} ORDER BY date desc, item"
    return pd.read_sql(query, engine)

def get_recdata_from_db(engine, table_name):
    query = f"SELECT Item, SUM(total) Total, SUM(quantity) Quantity, AVG(price) Price, Date FROM {table_name} GROUP BY date, item ORDER BY date desc, item"
    return pd.read_sql(query, engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
        
    # Retrieve daily spent and daily received data
    df_spent = get_data_from_db(engine, 'spent_data')
    df_received = get_recdata_from_db(engine, 'grndata')

    # Normalize column names to have consistent names for merging
    df_received = df_received.rename(columns={
        'Item': 'item',
        'Quantity': 'qty',
        'Price': 'price',
        'Total': 'total',
        'Date': 'date'
    })
    # print(df_received)
    # Standardize date formats
    df_spent['date'] = pd.to_datetime(df_spent['date'], dayfirst=False).dt.strftime('%Y-%m-%d')
    df_received['date'] = pd.to_datetime(df_received['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
    df_received['qty'] = round(df_received['qty'],2)
    df_received['total'] = round(df_received['total'],2)
    df_received['price'] = round(df_received['price'],2)
    
    
    # Trim whitespace from item names
    df_spent['item'] = df_spent['item'].str.strip()
    df_received['item'] = df_received['item'].str.strip()

    # Merge the data on the date and item columns
    df_merged = pd.merge(df_spent, df_received, on=['date', 'item'], suffixes=('_spent', '_received'))

    # Calculate daily profit/loss for each item
    df_merged['daily_profit_loss'] = round(df_merged['total_received'] - df_merged['total_spent'],2)

    # Calculate cumulative profit/loss for each item
    df_merged['cumulative_profit_loss'] = round(df_merged.groupby('item')['daily_profit_loss'].cumsum(),2)

    # Aggregate data to get daily totals and prepare the response format
    # df_merged['date'] = pd.to_datetime(df_merged['date'])  # Ensure date is in datetime format for grouping

    # Group by date to get the total spent, received, and daily profit/loss
    daily_summary = df_merged.groupby('date').agg({
        'total_spent': 'sum',
        'total_received': 'sum',
        'daily_profit_loss': 'sum'
    }).reset_index()
    
    #Rounding it off to 2 digits
    daily_summary['total_spent'] = round(daily_summary['total_spent'],2)
    daily_summary['total_received'] = round(daily_summary['total_received'],2)
    daily_summary['daily_profit_loss'] = round(daily_summary['daily_profit_loss'],2)

    daily_summary['items'] = daily_summary['date'].apply(
        lambda d: df_merged[df_merged['date'] == d].sort_values(by='item').to_dict(orient='records')
    )
    daily_summary = daily_summary.sort_values(by='date', ascending=False)

    response_data = daily_summary.to_dict(orient='records')
    return jsonify(response_data)



    

if __name__ == '__main__':
    app.run(debug=True, port=5001)
