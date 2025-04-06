from flask import jsonify, send_file
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
from app.repositories.processamento_repository import detectar_respostas_base64, desenhar_cartao


def gerar_pdf_cartao(dados):
    marcar = dados.get("marcar", True)
    respostas = dados.get("respostas")
    quantidade = dados.get("quantidade")

    if not respostas:
        if not quantidade or not isinstance(quantidade, int) or quantidade < 1:
            raise ValueError("Você deve informar 'respostas' ou um número válido em 'quantidade'.")
        respostas = {str(i + 1): "A" for i in range(quantidade)}

    imagem_buf = desenhar_cartao(respostas, marcar=marcar)

    imagem_pil = Image.open(imagem_buf)
    largura_img, altura_img = imagem_pil.size
    imagem_buf.seek(0)

    pagina_largura, pagina_altura = A4
    max_width = pagina_largura - 100
    max_height = pagina_altura - 100
    escala = min(max_width / largura_img, max_height / altura_img)
    largura_final = largura_img * escala
    altura_final = altura_img * escala
    x = (pagina_largura - largura_final) / 2
    y = (pagina_altura - altura_final) / 2

    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=A4)
    imagem = ImageReader(imagem_buf)
    c.drawImage(imagem, x, y, width=largura_final, height=altura_final, mask='auto')
    c.save()
    pdf_buf.seek(0)

    return send_file(pdf_buf, mimetype='application/pdf', as_attachment=True, download_name="cartao_resposta.pdf")


def corrigir_imagem(dados):
    imagem_base64 = dados.get("imagem_base64")
    gabarito = dados.get("gabarito")

    if not imagem_base64 or not gabarito:
        raise ValueError("Parâmetros ausentes")

    respostas_detectadas = detectar_respostas_base64(imagem_base64)
    acertos = 0

    for numero, resposta_correta in gabarito.items():
        detectada = respostas_detectadas.get(int(numero))
        if detectada and detectada.upper() == resposta_correta.upper():
            acertos += 1

    return jsonify({
        "respostas_detectadas": respostas_detectadas,
        "acertos": acertos
    })