from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.controllers.cartao_controller import cartao_blueprint
from app.swagger_config import swagger_template, swagger_config
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
app.register_blueprint(cartao_blueprint)


swagger = Swagger(app, template=swagger_template, config=swagger_config)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=False, port=3000)


