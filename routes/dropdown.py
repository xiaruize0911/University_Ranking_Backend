from flask import Blueprint, request, jsonify
from flask import Flask

dropdown_bp = Blueprint('dropdown', __name__)

@dropdown_bp.route('/countries', methods=['GET'])
def get_countries():
    from models.countries import get_countries_db
    countries = get_countries_db()
    return countries

@dropdown_bp.route('/ranking_options', methods=['GET'])
def get_ranking_options():
    from models.ranking_options import ranking_options
    tables = ranking_options()
    return jsonify(tables)

@dropdown_bp.route('/cities',methods=['GET'])
def get_cities():
    from models.cities import get_cities_db
    country = request.args.get('country')
    cities = get_cities_db(country)
    return jsonify(cities)