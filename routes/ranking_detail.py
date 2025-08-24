from flask import Blueprint, request, jsonify
from models.ranking_options import get_ranking_detail

ranking_detail_bp = Blueprint('ranking_detail', __name__)

@ranking_detail_bp.route('/ranking_detail', methods=['GET'])
def ranking_detail():
    table = request.args.get('table')
    source = request.args.get('source')
    subject = request.args.get('subject')
    print(f'ranking_detail {{"table": "{table}", "source": "{source}", "subject": "{subject}"}}')
    if not table or not source or not subject:
        return jsonify({'error': 'Missing parameters'}), 400
    detail = get_ranking_detail(table, source, subject)
    return jsonify(detail)
