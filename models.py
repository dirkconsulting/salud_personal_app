from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=date.today, unique=True)
    dolor = db.Column(db.Integer)
    digestion = db.Column(db.String(200))
    energia = db.Column(db.Integer)
    notas = db.Column(db.Text)

    suplementoregistro = db.relationship('SuplementoRegistro', backref='registro', lazy=True)
    ejercicioregistro = db.relationship('EjercicioRegistro', backref='registro', lazy=True)

class Suplemento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class SuplementoRegistro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suplemento_id = db.Column(db.Integer, db.ForeignKey('suplemento.id'))
    registro_id = db.Column(db.Integer, db.ForeignKey('registro.id'))

    suplemento = db.relationship('Suplemento', backref='registros')

class Ejercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    repeticiones = db.Column(db.String(50))
    series = db.Column(db.String(50))

class EjercicioRegistro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ejercicio_id = db.Column(db.Integer, db.ForeignKey('ejercicio.id'))
    registro_id = db.Column(db.Integer, db.ForeignKey('registro.id'))

    ejercicio = db.relationship('Ejercicio', backref='registros')

class Alimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20))  # permitido / prohibido
    categoria = db.Column(db.String(50))  # verdura, fruta, grasa, etc.

class Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20))  # desayuno, comida, cena, snack
    ingredientes = db.Column(db.Text)
    pasos = db.Column(db.Text)
