import cv2
import numpy as np
import base64
import io
import matplotlib.pyplot as plt

# Número de alternativas por questão (A, B, C, D, E)
OPCOES = 5

def preprocessar(imagem, usar_morfologia=True):
    """
    Converte a imagem para escala de cinza, aplica desfoque e threshold com inversão.
    As áreas preenchidas (com tinta preta) serão convertidas para branco (255)
    e as não preenchidas ficarão pretas (0).
    """
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    borrada = cv2.GaussianBlur(cinza, (5, 5), 0)
    # THRESH_BINARY_INV com Otsu: áreas escuras (marcadas) → branco e fundo → preto
    _, binarizada = cv2.threshold(borrada, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    if usar_morfologia:
        kernel = np.ones((3, 3), np.uint8)
        binarizada = cv2.morphologyEx(binarizada, cv2.MORPH_CLOSE, kernel)
    
    # # Visualiza a imagem binarizada (ajude na depuração)
    # plt.figure(figsize=(6, 4))
    # plt.imshow(binarizada, cmap='gray')
    # plt.title("Imagem Binarizada")
    # plt.axis("off")
    # plt.show()
    
    return binarizada

def encontrar_contornos(imagem_bin):
    """
    Encontra os contornos na imagem binarizada e descarta os pequenos (provavelmente ruídos).
    """
    contornos, _ = cv2.findContours(imagem_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Filtra contornos com área maior que 150
    bolhas = [c for c in contornos if cv2.contourArea(c) > 150]
    return bolhas

def detectar_respostas_base64(imagem_base64, usar_morfologia=True, total_questoes=None, gabarito=None):
    """
    Processa uma imagem (em base64) de um cartão de respostas onde cada questão possui 5 bolhas.
    Retorna um dicionário no formato:
       {
          "acertos": <número de acertos, calculado se gabarito for informado>,
          "respostas_detectadas": {
               "1": <alternativa ou None>,
               "2": <alternativa ou None>,
               ... 
          }
       }
    
    Argumentos:
      - imagem_base64: a imagem do cartão codificada em base64.
      - usar_morfologia: se True, aplica operação morfológica para melhorar os contornos.
      - total_questoes: (opcional) número total de questões esperadas; se informado,
                        as chaves de 1 até total_questoes serão garantidas.
      - gabarito: (opcional) um dicionário com as respostas corretas para comparar, por exemplo:
                 { "1": "B", "2": "D", "3": "B", "4": "A" }.
    """
    # Converte a string base64 em imagem OpenCV
    imagem_bytes = base64.b64decode(imagem_base64.split(',')[-1])
    imagem_np = np.frombuffer(imagem_bytes, dtype=np.uint8)
    imagem = cv2.imdecode(imagem_np, cv2.IMREAD_COLOR)
    if imagem is None:
        raise ValueError("Imagem inválida.")
    
    # Pré-processa a imagem
    imagem_bin = preprocessar(imagem, usar_morfologia=usar_morfologia)
    contornos = encontrar_contornos(imagem_bin)
    
    # Seleciona os contornos que tenham formato circular (aspecto ≈ 1)
    bolhas = []
    for c in contornos:
        x, y, w, h = cv2.boundingRect(c)
        aspecto = w / float(h)
        if 0.8 <= aspecto <= 1.2:
            bolhas.append((x, y, w, h, c))
    
    if not bolhas:
        # print("Nenhuma bolha encontrada.")
        # Se não houver nada, retorna um dicionário completo com todas as questões (se informado)
        respostas_vazias = {}
        if total_questoes is None:
            total_questoes = 1  # ao menos uma questão
        for q in range(1, total_questoes + 1):
            respostas_vazias[str(q)] = None
        return {"acertos": 0, "respostas_detectadas": respostas_vazias}
    
    # Ordena os contornos por posição: primeiro pela linha (y) depois pela coluna (x)
    bolhas = sorted(bolhas, key=lambda b: (b[1], b[0]))
    
    respostas = {}
    # Parâmetros de decisão:  
    # Se a bolha estiver marcada (preenchida) após threshold, ela terá muitos pixels brancos.
    LIMIAR_RAZAO = 0.5       # Exige que 50% (ou mais) da área do contorno (ou região interna) seja branca
    MIN_PREENCHIMENTO = 100  # Deve haver pelo menos 100 pixels brancos para ser considerado preenchido
    
    # Processa os grupos de OPCOES bolhas (cada grupo corresponde a uma questão)
    total_grupos = len(bolhas) // OPCOES
    for i in range(total_grupos):
        grupo = bolhas[i * OPCOES:(i+1) * OPCOES]
        q = i + 1  # número da questão
        
        # Ordena as bolhas da esquerda para a direita (opções A a E)
        grupo = sorted(grupo, key=lambda b: b[0])
        
        # Usaremos a estratégia de analisar apenas a região interna do círculo para ignorar o contorno
        metricas = []
        for idx, (x, y, w, h, c) in enumerate(grupo):
            # Define um "padding" para excluir a borda (20% dos lados)
            padding = 0.2
            sx = int(x + w * padding)
            sy = int(y + h * padding)
            sw = int(w * (1.0 - 2 * padding))
            sh = int(h * (1.0 - 2 * padding))
            # Ajusta os limites para não exceder a imagem
            sx = max(0, sx)
            sy = max(0, sy)
            ex = min(imagem_bin.shape[1], sx + sw)
            ey = min(imagem_bin.shape[0], sy + sh)
            if sx >= ex or sy >= ey:
                total_branco_interno = 0
                area_interna = 1  # para evitar divisão por zero
            else:
                regiao_interna = imagem_bin[sy:ey, sx:ex]
                total_branco_interno = cv2.countNonZero(regiao_interna)
                area_interna = regiao_interna.shape[0] * regiao_interna.shape[1]
            
            razao_interna = total_branco_interno / float(area_interna)
            metricas.append((idx, total_branco_interno, razao_interna))
            # print(f"Questão {q} - {chr(ord('A')+idx)}: BrancoInterno={total_branco_interno}, ÁreaInterna={area_interna}, RazãoInterna={razao_interna:.2f}")
        
        # Seleciona a alternativa com maior razão interna
        idx_melhor, total_melhor, razao_melhor = max(metricas, key=lambda x: x[2])
        # print(f"Questão {q}: Melhor alternativa = {chr(ord('A')+idx_melhor)}; Razão={razao_melhor:.2f}, Total={total_melhor}")
        
        # Se a melhor alternativa atingir os critérios, ela é marcada; senão, a questão fica sem resposta (None)
        if total_melhor >= MIN_PREENCHIMENTO and razao_melhor >= LIMIAR_RAZAO:
            respostas[str(q)] = chr(ord('A') + idx_melhor)
        else:
            respostas[str(q)] = None

    # Se for informado o total de questões esperado, preenche com None as que faltarem
    if total_questoes is not None:
        for q in range(1, total_questoes + 1):
            if str(q) not in respostas:
                respostas[str(q)] = None

    return respostas


def desenhar_cartao(respostas_dict, marcar=True):
    import matplotlib.pyplot as plt
    import io

    total_questoes = 30
    altura_por_questao = 1
    margem_topo = 3
    largura_total = 7
    # Adiciona espaço extra para os dados do aluno e o cabeçalho
    altura_total = total_questoes * altura_por_questao + margem_topo + 2

    fig, ax = plt.subplots(figsize=(largura_total, altura_total))
    
    # Dados do aluno ficam no topo
    ax.text(-1.2, total_questoes + margem_topo + 1, "Nome do Aluno:", fontsize=12, va="center", ha="left")
    ax.text(-1.2, total_questoes + margem_topo, "Disciplina:", fontsize=12, va="center", ha="left")
    
    # Cabeçalho: letras das alternativas (A, B, C, D, E)
    header_y = total_questoes + margem_topo - 1  # logo abaixo dos dados do aluno
    for i, letra in enumerate("ABCDE"):
        x = i * 1.2
        ax.text(x, header_y, letra, fontsize=12, ha="center", va="center", fontweight="bold")
    base_y = header_y - 1
    for idx in range(1, total_questoes + 1):
        y = base_y - (idx - 1) * altura_por_questao

        alternativa = respostas_dict.get(str(idx))

        # Só exibe o número da questão se ela existir
        if alternativa is not None:
            ax.text(-0.99, y, f"{idx})", fontsize=16, va='center', ha='right')

        for i, letra in enumerate("     "):
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
                edgecolor = "#FFFFFF" 
                text = ""
                textcolor = "black"

            circle = plt.Circle((x, y), 0.35, edgecolor=edgecolor, facecolor=facecolor, linewidth=1.5)
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
