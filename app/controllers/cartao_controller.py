from flask import Blueprint, request, jsonify, send_file
from app.services.cartao_service import gerar_pdf_cartao, corrigir_imagem
from flasgger.utils import swag_from

cartao_blueprint = Blueprint('cartao', __name__, url_prefix="/")

@cartao_blueprint.route("/gerar-cartao", methods=["GET"])
def gerar_cartao():
    """
    Gera um cartão-resposta em PDF a partir de respostas ou quantidade de questões.
    ---
    tags:
      - Cartão Resposta
    parameters:
      - name: quantidade
        in: query
        type: integer
        required: false
        description: "Número de questões (se 'respostas' não for fornecido)"
        example: 10
      - name: marcar
        in: query
        type: boolean
        required: false
        description: "Se True, marca a alternativa nas bolhas"
        example: false
    responses:
      200:
        description: PDF com o cartão-resposta gerado
        content:
          application/pdf:
            schema:
              type: string
              format: binary
    """
    try:
        quantidade = request.args.get("quantidade", type=int)
        marcar = request.args.get("marcar", default=False, type=lambda v: v.lower() == "true")

        if quantidade is not None and quantidade > 30:
            return jsonify({"erro": "A quantidade máxima permitida é 30 questões."}), 400

        dados = {"quantidade": quantidade, "marcar": marcar}
        return gerar_pdf_cartao(dados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@cartao_blueprint.route("/corrigir", methods=["POST"])
def corrigir():
    """
    Corrige um cartão-resposta a partir da imagem (base64) e do gabarito.
    ---
    tags:
      - Correção
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - imagem_base64
            - gabarito
          properties:
            imagem_base64:
              type: string
              description: Imagem do cartão-resposta em base64
              example: data:image/png;base64,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
            gabarito:
                type: object
                additionalProperties:
                  type: string
                example: { "1": "C", "2": "D", "3": "B", "4": "D", "5": "D" }
                description: Gabarito com as respostas corretas
    responses:
      200:
        description: Resultado da correção
        schema:
          type: object
          properties:
            respostas_detectadas:
              type: object
            acertos:
              type: integer
    """
    dados = request.get_json()
    try:
        return corrigir_imagem(dados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
