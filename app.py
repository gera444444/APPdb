from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import re

# Инициализация приложения
app = Flask(__name__)

# Конфигурация базы данных 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных и схемы
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Модель автомобиля
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

# Схема для сериализации данных автомобиля
class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car

# Создание базы данных
with app.app_context():
    db.create_all()

# Валидация данных с помощью регулярных выражений
def validate_car_data(data):
    if not re.match(r'^[A-Za-zs]+$', data['make']):
        return "Invalid make"
    if not re.match(r'^[A-Za-z0-9s]+$', data['model']):
        return "Invalid model"
    if not isinstance(data['year'], int) or not (1886 <= data['year'] <= 2023):
        return "Invalid year"
    return None

# Создание нового автомобиля (POST)
@app.route('/cars', methods=['POST'])
def add_car():
    data = request.json
    error = validate_car_data(data)
    if error:
        return jsonify({'error': error}), 400

    new_car = Car(make=data['make'], model=data['model'], year=data['year'])
    db.session.add(new_car)
    db.session.commit()
    
    car_schema = CarSchema()
    return car_schema.jsonify(new_car), 201

# Получение списка автомобилей (GET)
@app.route('/cars', methods=['GET'])
def get_cars():
    cars = Car.query.all()
    car_schema = CarSchema(many=True)
    return car_schema.jsonify(cars)

# Получение автомобиля по ID (GET)
@app.route('/cars/<int:id>', methods=['GET'])
def get_car(id):
    car = Car.query.get_or_404(id)
    car_schema = CarSchema()
    return car_schema.jsonify(car)

# Обновление информации об автомобиле (PUT)
@app.route('/cars/<int:id>', methods=['PUT'])
def update_car(id):
    car = Car.query.get_or_404(id)
    data = request.json
    error = validate_car_data(data)
    if error:
        return jsonify({'error': error}), 400

    car.make = data['make']
    car.model = data['model']
    car.year = data['year']
    
    db.session.commit()
    
    car_schema = CarSchema()
    return car_schema.jsonify(car)

# Удаление автомобиля (DELETE)
@app.route('/cars/<int:id>', methods=['DELETE'])
def delete_car(id):
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    
    return jsonify({'message': 'Car deleted'}), 204

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
    

import sqlite3

# Подключение к базе данных 
conn = sqlite3.connect('cars.db')
cursor = conn.cursor()

