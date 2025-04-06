from flask import Flask
from flasgger import Swagger
from app.controllers.cartao_controller import cartao_blueprint
from app.swagger_config import swagger_template, swagger_config
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.register_blueprint(cartao_blueprint)


swagger = Swagger(app, template=swagger_template, config=swagger_config)

if __name__ == "__main__":
    app.run(debug=True, port=3000)


