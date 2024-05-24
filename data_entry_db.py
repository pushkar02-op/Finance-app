from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    date = request.form["date"]
    item = request.form["item"]
    qty = request.form["qty"]
    price = request.form["price"]
    total = request.form["total"]

    # # Parse date string to datetime object
    # date_obj = datetime.strptime(date, "%Y-%m-%d").date()

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

if __name__ == "__main__":
    # Start the Flask application
    app.run(debug=True)
