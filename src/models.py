from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorites = db.relationship("Favorite", backref="user", uselist=True)
    # Esto es para que cuando se haga un print nos devuelba este mesanje
    def __repr__(self):
        return f"User with email {self.email} and id {self.id}"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }

    
class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    diameter = db.Column(db.Integer)
    rotation = db.Column(db.Integer)
    terrain = db.Column(db.String(80))

    def __repr__(self):
        return f'El planeta con {self.name} con ID: {self.id}'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "rotation": self.rotation,
            "terrain": self.terrain
        }


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    height = db.Column(db.Integer)
    mass = db.Column(db.Integer)
    hair_color = db.Column(db.String(80))
    planet_id =  db.Column(db.Integer, db.ForeignKey("planet.id"))
    planet = db.relationship("Planet")



    def __repr__(self):
        return f"The people with name: {self.name} and ID: {self.id}"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    __table_args__= (db.UniqueConstraint(
        'user_id',
        'name',
        name= 'favorite_unique'
    ),)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id
        }
    
    @classmethod
    def create(cls, favorite):
        try:
            new_favorite = cls(**favorite)
            db.session.add(new_favorite)
            db.session.commit()
            return new_favorite
        except Exception as error:
            print(error)
            db.session.rollback()
            return None