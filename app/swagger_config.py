swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API de Correção de Cartões-Resposta",
        "description": "Geração e correção automática de cartões-resposta usando Flask, OpenCV e PDF.",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["https"]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs"
}
