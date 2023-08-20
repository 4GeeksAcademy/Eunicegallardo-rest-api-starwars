"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


# USER ENDPOINTS

# get the list of users
@app.route("/user", methods=['GET'])
def get_user():
    users = User.query.all()
    users_serialized = list(map(lambda x: x.serialize(), users))

    return jsonify({"msg": 'Completado', "planets": users_serialized})


# get the list of favorites
@app.route('/user/favorite', methods=['GET'])
def get_user_favorite():
    favorties = Favorite.query.all()
    favorties_serialized = list(map(lambda x: x.serialize(), favorties))

    return jsonify({"msg": "Get the list of favorites", "Favorites": favorties_serialized})


# PLANET ENDPOINTS

# GET a list of all the planets
@app.route("/planet", methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_serialized = list(map(lambda x: x.serialize(), planets))

    return jsonify({"msg": 'Completado', "planets": planets_serialized})

# GET one planet by id
@app.route("/planet/<int:planet_id>", methods=['GET'])
def get_planets_id(planet_id):
    single_planet = People.query.get(planet_id)
    if single_planet is None:
        raise APIException(f"No existe el id {planet_id}", status_code=400)
    response_body = {
        "msg": "Hello, this is your GET /planet_id ",
        "people_id": planet_id,
        "people_info": single_planet.serialize()
    }

    return jsonify(response_body), 200

# POST to Planet
@app.route('/planet', methods=['POST'])
def post_planet():
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("Debes enviar info en el body", status_code=400)
    print(body)
    if "id" not in body:
        raise APIException("Debes poner un ID", status_code=400)
    if "name" not in body:
        raise APIException("Debes poner un nombre, por favor", status_code=400)
    if "diameter" not in body:
        raise APIException(
            "Debes colocar la info del diametro", status_code=400)
    if "rotation" not in body:
        raise APIException(
            "Debes colocar la info de la rotación", status_code=400)
    if "terrain" not in body:
        raise APIException("Debes poner la info del terreno", status_code=400)

    new_planet = Planet(id=body['id'], name=body['name'], diameter=body['diameter'],
                        rotation=body['rotation'], terrain=body['terrain'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": "Lograste el POST", "new_planet_info": new_planet.serialize()})

# PUT method of planet
@app.route("/planet", methods=['PUT'])
def modify_planet():
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("Debes enviar info en el body", status_code=400)
    if "id" not in body:
        raise APIException(
            "Debes enviar el id del planeta modificado", status_code=400)
    if "name" not in body:
        raise APIException("Debes enviar el nombre nuevo", status_code=400)
    if "diameter" not in body:
        raise APIException(
            "Debes enviar la nueva info de diametro", status_code=400)
    if "rotation" not in body:
        raise APIException("Debes la nueva rotation", status_code=400)
    if "terrain" not in body:
        raise APIException("Debes enviar el nuevo terreno")
    single_planet = Planet.query.get(body['id'])
    single_planet.name = body['name']
    single_planet.diameter = body['diameter']
    single_planet.rotation = body['rotation']
    single_planet.terrain = body['terrain']
    db.session.commit()
    return jsonify({"msg": "PUT completado"})

# DELETE a planet
@app.route("/planet/<int:planet_id>", methods=['DELETE'])
def delete_planet(planet_id):
    single_planet = Planet.query.get(planet_id)
    if single_planet is None:
        raise APIException("Planeta no existe", status_code=400)

    db.session.delete(single_planet)
    db.session.commit()

    return jsonify({"msg": "DELETE Completado"})


# POST method to add a new favorite PLANET as favorite
@app.route("/favorite/planet/<int:planet_id>", methods=['POST'])
def add_new_favorite_planet(planet_id):
    current_user = 1
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet is not None:
        favorite = Favorite.query.filter_by(name=planet.name).first()
        if favorite:
            return jsonify({"ok": True, "msg": "El favorito existe"}), 200
        body = {
            "name": planet.name,
            "user_id": current_user
        }
        new_favorite = Favorite.create(body)
        if new_favorite is not None:
            return jsonify(new_favorite.serialize()), 201
        return jsonify({"msg": "Ocurrió un error del lado del servidor"}), 500
    return jsonify({
        "msg": "Planeta no encontrado"
    }), 404

# Eliminar en favorito un planeta por su id
@app.route("/favorite/planet/<int:planet_id>", methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user = 1
    planet = Planet.query.filter_by(id=planet_id).first()

    if planet is not None:
        favorite = Favorite.query.filter_by(
            name=planet.name, user_id=current_user).first()

        if not favorite:
            return jsonify({"ok": False, "msg": "El favorito no existe"}), 404

        try:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"ok": True, "msg": "Favorito eliminado exitosamente"}), 200
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify({"msg": "Ocurrió un error del lado del servidor"}), 500
    return jsonify({
        "msg": "Planeta no encontrado"
    }), 404


# PEOPLE ENDPOINTS

# GET a list of people
@app.route("/people", methods=['GET'])
def get_people():
    people = People.query.all()
    people_serialized = list(map(lambda x: x.serialize(), people))

    return jsonify({"msg": 'Get people completado', "people": people_serialized}), 200

# GET one person by id
@app.route("/people/<int:people_id>", methods=['GET'])
def get_people_id(people_id):
    single_people = People.query.get(people_id)
    if single_people is None:
        raise APIException(f"No existe el id {people_id}", status_code=400)
    response_body = {
        "msg": "Hello, this is your GET /people_id ",
        "people_id": people_id,
        "people_info": single_people.serialize()
    }

    return jsonify(response_body), 200

# POST method to people
@app.route('/people', methods=['POST'])
def post_people():
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("Debes enviar info en el body", status_code=400)
    print(body)
    if "id" not in body:
        raise APIException("Debes poner un ID", status_code=400)
    if "name" not in body:
        raise APIException("Debes poner un nombre, por favor", status_code=400)
    if "height" not in body:
        raise APIException("Debes enviar nueva altura", status_code=400)
    if "mass" not in body:
        raise APIException("Debes enviar nueva info de mass", status_code=400)
    if "hair_color" not in body:
        raise APIException("Debes nuevo color de cabello", status_code=400)

    new_people = People(id=body['id'], name=body['name'], height=body['height'],
                        mass=body['mass'], hair_color=body['hair_color'])
    db.session.add(new_people)
    db.session.commit()
    return jsonify({"msg": "Lograste el POST", "new_people_info": new_people.serialize()})

# PUT method of people
@app.route("/people", methods=['PUT'])
def modify_people():
    body = request.get_json(silent=True)
    if body is None:
        raise APIException("Debes enviar info en el body", status_code=400)
    if "id" not in body:
        raise APIException(
            "Debes enviar el id de la persona modificado", status_code=400)
    if "name" not in body:
        raise APIException("Debes enviar el nombre nuevo", status_code=400)
    if "height" not in body:
        raise APIException(
            "Debes enviar la nueva info de la altura", status_code=400)
    if "mass" not in body:
        raise APIException("Debes la enviar la nueva info de masa", status_code=400)
    if "hair_color" not in body:
        raise APIException("Debes enviar el nuevo color de cabello")
    single_people = People.query.get(body['id'])
    single_people.name = body['name']
    single_people.height= body['height']
    single_people.mass = body['mass']
    single_people.hair_color = body['hair_color']
    db.session.commit()
    return jsonify({"msg": "PUT completado"})

# DELETE a planet
@app.route("/people/<int:people_id>", methods=['DELETE'])
def delete_people(people_id):
    single_people = People.query.get(people_id)
    if single_people is None:
        raise APIException("People no existe", status_code=400)

    db.session.delete(single_people)
    db.session.commit()

    return jsonify({"msg": "DELETE Completado"})

# POST method to add a new favortie PEOPLE as favorite
@app.route("/favorite/people/<int:people_id>", methods=['POST'])
def add_new_favorite_people(people_id):
    current_user = 1
    people = People.query.filter_by(id=people_id).first()
    if people is not None:
        favorite = Favorite.query.filter_by(name=people.name).first()
        if favorite:
            return jsonify({"ok": True, "msg": "El favorito existe"}), 200
        body = {
            "name": people.name,
            "user_id": current_user
        }
        new_favorite = Favorite.create(body)
        if new_favorite is not None:
            return jsonify(new_favorite.serialize()), 201
        return jsonify({"msg": "Ocurrió un error del lado del servidor"}), 500
    return jsonify({
        "msg": "People no encontrado"
    }), 404

# Eliminar en favorito PEOPLE por su id
@app.route("/favorite/people/<int:people_id>", methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user = 1
    people = People.query.filter_by(id=people_id).first()

    if people is not None:
        favorite = Favorite.query.filter_by(
            name=people.name, user_id=current_user).first()

        if not favorite:
            return jsonify({"ok": False, "msg": "El favorito no existe"}), 404

        try:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"ok": True, "msg": "Favorito eliminado exitosamente"}), 200
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify({"msg": "Ocurrió un error del lado del servidor"}), 500
    return jsonify({
        "msg": "People no encontrado"
    }), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
