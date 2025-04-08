import cv2
import numpy as np
import base64
import io
import matplotlib.pyplot as plt

OPCOES = 5

def preprocessar(imagem):
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    borrada = cv2.GaussianBlur(cinza, (5, 5), 0)
    _, binarizada = cv2.threshold(borrada, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binarizada

def encontrar_contornos(imagem_bin):
    contornos, _ = cv2.findContours(imagem_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bolhas = [c for c in contornos if cv2.contourArea(c) > 150]
    return bolhas

def detectar_respostas_base64(imagem_base64):
    imagem_bytes = base64.b64decode(imagem_base64.split(',')[-1])
    imagem_np = np.frombuffer(imagem_bytes, np.uint8)
    imagem = cv2.imdecode(imagem_np, cv2.IMREAD_COLOR)
    if imagem is None:
        raise ValueError("Imagem inválida.")

    imagem_bin = preprocessar(imagem)
    contornos = encontrar_contornos(imagem_bin)

    bolhas = []
    for c in contornos:
        (x, y, w, h) = cv2.boundingRect(c)
        aspecto = w / float(h)
        if 0.8 <= aspecto <= 1.2:
            bolhas.append((x, y, w, h, c))

    if not bolhas:
        return {}

    bolhas = sorted(bolhas, key=lambda b: (b[1], b[0]))
    respostas = {}

    for i in range(0, len(bolhas), OPCOES):
        grupo = bolhas[i:i + OPCOES]
        if len(grupo) < OPCOES:
            continue
        grupo = sorted(grupo, key=lambda b: b[0])
        intensidade = []

        for idx, (x, y, w, h, c) in enumerate(grupo):
            mask = np.zeros(imagem_bin.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            total = cv2.countNonZero(cv2.bitwise_and(imagem_bin, imagem_bin, mask=mask))
            intensidade.append((idx, total))

        marcada = max(intensidade, key=lambda x: x[1])[0]
        respostas[i // OPCOES + 1] = chr(ord('A') + marcada)

    return respostas


def desenhar_cartao(respostas_dict, marcar=True):
    import matplotlib.pyplot as plt
    import io

    total_questoes = 30
    altura_por_questao = 0.7
    margem_topo = 3
    largura_total = 7
    altura_total = total_questoes * altura_por_questao + margem_topo

    fig, ax = plt.subplots(figsize=(largura_total, altura_total))
    ax.text(-1.2, total_questoes + 2, "Nome do Aluno:", fontsize=12, va="center", ha="left")
    ax.text(-1.2, total_questoes + 1, "Disciplina:", fontsize=12, va="center", ha="left")

    for idx in range(1, total_questoes + 1):
        y = total_questoes - idx
        alternativa = respostas_dict.get(str(idx))

        # Só exibe o número da questão se ela existir
        if alternativa is not None:
            ax.text(-0.6, y, f"{idx}", fontsize=12, va='center', ha='right')

        for i, letra in enumerate("ABCDE"):
            x = i * 1.2

            # Se for uma questão preenchida
            if marcar and alternativa and letra.upper() == alternativa.upper():
                facecolor = "black"
                edgecolor = "black"
                text = letra
                textcolor = "white"

            # Questão não marcada, mas dentro da quantidade
            elif alternativa:
                facecolor = "white"
                edgecolor = "black"
                text = letra
                textcolor = "black"

            # Questão excedente (não usada)
            else:
                facecolor = "white"
                edgecolor = "#FFFFFF"  # cinza claro
                text = ""
                textcolor = "black"

            circle = plt.Circle((x, y), 0.4, edgecolor=edgecolor, facecolor=facecolor, linewidth=1.5)
            ax.add_patch(circle)
            ax.text(x, y, text, fontsize=11, ha="center", va="center", color=textcolor)

    ax.set_xlim(-2, 6.5)
    ax.set_ylim(-1, total_questoes + margem_topo + 1)
    ax.set_aspect('equal')
    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    buf.seek(0)
    return buf
