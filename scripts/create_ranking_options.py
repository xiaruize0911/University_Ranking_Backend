from time import time
start_time = time()
from flask import jsonify, request
from models.ranking_options import ranking_options
tables = ranking_options()
end_time = time()
duration = end_time - start_time
print(f"Duration: {duration} seconds")
result = jsonify(tables)