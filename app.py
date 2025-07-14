from flask import Flask
from routes.universities import universities_bp
# from routes.rankings import rankings_bp
# from routes.stats import stats_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(universities_bp, url_prefix="/universities")
if __name__ == "__main__":
    app.run(debug=True)
