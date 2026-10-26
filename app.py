import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")

database_url = os.environ.get("DATABASE_URL", "sqlite:///lost_found.db")
# Render PostgreSQL URLs may start with postgres://; SQLAlchemy expects postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

CATEGORIES = ["ID Card", "Books & Notes", "Electronics", "Keys", "Wallet / Purse",
              "Clothing", "Bottle / Lunch Box", "Other"]
ITEM_TYPES = ["Lost", "Found"]
STATUSES = ["Open", "Claimed", "Returned"]


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    item_type = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    item_date = db.Column(db.String(20), nullable=False)
    contact_name = db.Column(db.String(80), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    item_type = request.args.get("type", "").strip()
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "Open").strip()

    items_query = Item.query
    if query:
        pattern = f"%{query}%"
        items_query = items_query.filter(or_(
            Item.title.ilike(pattern),
            Item.description.ilike(pattern),
            Item.location.ilike(pattern),
            Item.category.ilike(pattern)
        ))
    if item_type in ITEM_TYPES:
        items_query = items_query.filter_by(item_type=item_type)
    if category in CATEGORIES:
        items_query = items_query.filter_by(category=category)
    if status in STATUSES:
        items_query = items_query.filter_by(status=status)
    elif status == "All":
        pass
    else:
        status = "Open"
        items_query = items_query.filter_by(status="Open")

    items = items_query.order_by(Item.created_at.desc()).all()
    stats = {
        "total": Item.query.count(),
        "lost": Item.query.filter_by(item_type="Lost", status="Open").count(),
        "found": Item.query.filter_by(item_type="Found", status="Open").count(),
        "returned": Item.query.filter_by(status="Returned").count()
    }
    return render_template("index.html", items=items, stats=stats,
                           categories=CATEGORIES, selected={
                               "q": query, "type": item_type,
                               "category": category, "status": status
                           })


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        required = ["title", "item_type", "category", "description", "location",
                    "item_date", "contact_name", "contact_email"]
        if any(not request.form.get(field, "").strip() for field in required):
            flash("Please fill in all required fields.", "error")
            return render_template("report.html", categories=CATEGORIES, item_types=ITEM_TYPES)

        item_type = request.form["item_type"]
        category = request.form["category"]
        if item_type not in ITEM_TYPES or category not in CATEGORIES:
            flash("Please choose a valid item type and category.", "error")
            return render_template("report.html", categories=CATEGORIES, item_types=ITEM_TYPES)

        item = Item(
            title=request.form["title"].strip(),
            item_type=item_type,
            category=category,
            description=request.form["description"].strip(),
            location=request.form["location"].strip(),
            item_date=request.form["item_date"],
            contact_name=request.form["contact_name"].strip(),
            contact_email=request.form["contact_email"].strip(),
            status="Open"
        )
        db.session.add(item)
        db.session.commit()
        flash("Your report has been published successfully.", "success")
        return redirect(url_for("index"))

    return render_template("report.html", categories=CATEGORIES, item_types=ITEM_TYPES)


@app.route("/item/<int:item_id>")
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template("detail.html", item=item)


@app.route("/item/<int:item_id>/status", methods=["POST"])
def update_status(item_id):
    item = Item.query.get_or_404(item_id)
    new_status = request.form.get("status", "")
    if new_status in STATUSES:
        item.status = new_status
        db.session.commit()
        flash("Item status updated.", "success")
    else:
        flash("Invalid status.", "error")
    return redirect(url_for("item_detail", item_id=item.id))


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
