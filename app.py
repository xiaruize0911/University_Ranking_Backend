from flask import Flask
from routes.universities import universities_bp
from routes.dropdown import dropdown_bp
# from routes.rankings import rankings_bp
# from routes.stats import stats_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(universities_bp, url_prefix="/universities")
app.register_blueprint(dropdown_bp, url_prefix="/dropdown")

if __name__ == "__main__":
    app.run(port=10000,debug=True)
