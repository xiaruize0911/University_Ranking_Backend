from flask import Blueprint, request, jsonify
from models.universities import filter_universities
from flask import Flask
from models.ranking_options import ranking_options

universities_bp = Blueprint("universities", __name__)

@universities_bp.route("/filter", methods=["GET"])
def filter_universities_route():
    query = request.args.get("query")
    sort_credit = request.args.get("sort_credit")
    country = request.args.get("country")
    city = request.args.get("city")

    results = filter_universities(query, sort_credit, country, city)
    return jsonify(results)

@universities_bp.route("/<int:univ_id>", methods=["GET"])
def get_university(univ_id):
    from models.university import get_university_by_id
    result = get_university_by_id(univ_id)
    if result:
        return jsonify(result)
    return jsonify({"error": "University not found"}), 404

@universities_bp.route('/<string:name>', methods=['GET'])
def get_university_by_name(name):
    from models.university import get_universities_by_name
    result = get_universities_by_name(name)
    if result:
        return jsonify(result)
    return jsonify({"error": "University not found"}), 404

@universities_bp.route('/<string:normalized_name>/rankings/<string:source>', methods=['GET'])
def get_university_rankings_by_source(normalized_name, source):
    from models.university import get_university_rankings_by_source
    result = get_university_rankings_by_source(normalized_name, source)
    return jsonify(result)

@universities_bp.route('/translate/<string:normalized_name>', methods=['GET'])
def get_translated_name(normalized_name):
    language = request.args.get('language', 'en')  # default to English
    from models.translations import get_translated_name_by_normalized
    translated_name = get_translated_name_by_normalized(normalized_name, language)
    if translated_name:
        return jsonify({"normalized_name": normalized_name, "language": language, "name": translated_name})
    return jsonify({"error": "Translation not found"}), 404

@universities_bp.route('/translate/all', method = ['GET'])
def get_all_translations():
    language = request.args.get('language')
    from models.translations import get_all_translations
    translations = get_all_translations(language)
    return jsonify(translations)
