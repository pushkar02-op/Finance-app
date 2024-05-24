from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
import time

app = Flask(__name__)


# MySQL database configuration
DATABASE_URI = 'mysql://admin:Pu$hkar121@localhost:3306/mydatabase'

# Create a connection to the database
engine = create_engine(DATABASE_URI)

# Function to retrieve data from tables
def get_data_from_db(engine, table_name, start_date, end_date):
    query = f"SELECT * FROM {table_name} where date between '{start_date}' and '{end_date}' ORDER BY date desc, item"
    return pd.read_sql(query, engine)

def get_recdata_from_db(engine, table_name, start_date, end_date):
    query = f"SELECT Item, SUM(total) Total, SUM(quantity) Quantity, AVG(price) Price, Date FROM {table_name} where date between '{start_date}' and '{end_date}' GROUP BY date, item ORDER BY date desc, item"
    return pd.read_sql(query, engine)


@app.route('/data', methods=['GET'])
def data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
        
    # Retrieve daily spent and daily received data
    df_spent = get_data_from_db(engine, 'spent_data',start_date, end_date)
    df_received = get_recdata_from_db(engine, 'grndata', start_date, end_date)

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
    # df_merged['cumulative_profit_loss'] = round(df_merged.groupby('item')['daily_profit_loss'].cumsum(),2)
   
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




# Configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://admin:Pu$hkar121@localhost/mydatabase"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SpentData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    item = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

# Create the database
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/submit", methods=["POST"])
def submit():
    date = request.form["date"]
    item = request.form["item"]
    qty = request.form["qty"]
    price = request.form["price"]
    total = request.form["total"]

    # Check if data with the same date and item already exists
    existing_data = SpentData.query.filter_by(date=date, item=item).first()
    if existing_data:
        # Update existing row with the same date and item
        existing_data.qty = qty
        existing_data.price = price
        existing_data.total = total
    else:
        # If data with the same date and item does not exist, create a new row
        new_data = SpentData(date=date, item=item, qty=qty, price=price, total=total)
        db.session.add(new_data)
    
    db.session.commit()
    return "Data submitted successfully!"

@app.route("/get_data")
def get_data():
    req_date = request.args.get("reqdate")
    
    data = SpentData.query.filter_by(date=req_date).order_by(SpentData.date.desc(), SpentData.item.asc()).all()
    if not data:
        return jsonify([])  # Return empty list if no data found for the given date

    result = []
    for row in data:
        row_data = {
            "date": row.date,
            "item": row.item,
            "qty": row.qty,
            "price": row.price,
            "total": row.total
        }
        result.append(row_data)

    return jsonify(result)

@app.route("/keep-alive")
def keep_alive():
    return jsonify({"message": "Server is alive"}) 




        
if __name__ == "__main__":
    # Start the Flask application
    app.run(debug=True)
