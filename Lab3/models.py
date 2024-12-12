from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_mdl = db.Column(db.Integer, nullable=False)
    price_eur = db.Column(db.Float, nullable=False)

