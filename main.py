from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# ----------------Cafe TABLE Configuration---------------
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # print(column)
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])  # GET is by default, we can remove this.
def get_random_cafe():

    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(all_cafes)
    # print(random_cafe.name)

    # return jsonify(cafe={
    #     "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "amenities": {
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #     }
    # })
    return jsonify(cafe=random_cafe.to_dict())


# --------------HTTP GET - Read Record---------------
@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
    # print(all_cafes)
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def search_cafe_at_location():
    query_location = request.args.get("loc")    # http://127.0.0.1:5000/search?loc=London
    all_cafes = db.session.execute(db.select(Cafe).where(Cafe.location == query_location)).scalars().all()
    if all_cafes:   # if list not empty
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# --------------- HTTP POST - Create Record---------------
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# ------------HTTP PUT/PATCH - Update Record------------
@app.route("/update-price/<int:cafe_id>", methods=["GET", "PATCH"])    # http://127.0.0.1:5000/update-price/63?new_price=$25
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    # cafe = db.get_or_404(Cafe, cafe_id)
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        # Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        # 404 = Resource not found
        return jsonify(error={"Not Found": f"Sorry a cafe with id '{cafe_id}' was not found in the database."}), 404


# ----------------HTTP DELETE - Delete Record-----------------
@app.route("/delete_record/<int:cafe_id>",  methods=["GET", "DELETE"])
def delete_record(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":

        cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe:
            cafe_name = cafe.name
            db.session.delete(cafe)
            db.session.commit()
            # Just add the code after the jsonify method. 200 = Ok
            return jsonify(response={"success": f"Successfully deleted cafe id- {cafe_id},'{cafe_name}' record."}), 200
        else:
            # 404 = Resource not found
            return jsonify(error={"Not Found": f"Sorry a cafe with id '{cafe_id}' was not found in the database."}), 404

    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

# https://documenter.getpostman.com/view/32072324/2s9YsDmFab


if __name__ == '__main__':
    app.run(debug=True)


