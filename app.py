from flask import Flask
# from routes.rankings import rankings_bp
# from routes.stats import stats_bp
from routes.universities import universities_bp
from routes.dropdown import dropdown_bp
from routes.ranking_detail import ranking_detail_bp
# from routes.rankings import rankings_bp
# from routes.stats import stats_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(universities_bp, url_prefix="/universities")
app.register_blueprint(dropdown_bp, url_prefix="/dropdown")
app.register_blueprint(ranking_detail_bp, url_prefix="/subject_rankings")

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=10000)
