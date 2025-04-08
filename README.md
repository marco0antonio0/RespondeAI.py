
# 🧠 RespondeAI - Geração e Correção de Cartões-Resposta

O **RespondeAI** é um sistema de análise e correção automatizada de cartões-resposta, que permite:

✅ Gerar cartões-resposta personalizados em PDF  
✅ Corrigir cartões a partir de imagens (base64)  
✅ API documentada com Swagger  
✅ Preparado para múltiplos cartões por folha  

---

## 🚀 Acesse a documentação interativa (Swagger)

📄 Swagger Docs - [https://api-respondeai.dirrocha.com/apidocs](https://api-respondeai.dirrocha.com/apidocs)

---

## 📁 Estrutura do Projeto

```
pyAnalise/
├─ app/
│  ├─ controllers/                # Rotas e endpoints da API
│  │  └─ cartao_controller.py     # Endpoints /gerar-cartao e /corrigir
│  ├─ repositories/               # Camada de processamento e lógica
│  │  └─ processamento_repository.py
│  ├─ services/                   # Geração visual do cartão-resposta
│  │  └─ cartao_service.py
│  └─ swagger_config.py           # Configuração personalizada do Swagger
├─ main.py                        # Entrada principal do aplicativo Flask
├─ requirements.txt               # Dependências Python
├─ Dockerfile                     # Dockerfile para deploy containerizado
```

---

## 🔧 Instalação

### 💻 Rodar localmente

1. Clone o projeto:

```bash
git clone https://github.com/seu-usuario/pyAnalise.git
cd pyAnalise
```

2. Crie um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Rode o app:

```bash
python main.py
```

### 🐳 Usar com Docker

```bash
docker build -t pyanalise .
docker run -p 3000:3000 pyanalise
```

---

## 📬 Endpoints da API

### 📄 `POST /gerar-cartao`

Gera um ou mais cartões-resposta em PDF.

#### Corpo esperado (JSON):

```json
{
  "quantidade": 30,
  "marcar": false
}
```

| Campo              | Tipo     | Obrigatório | Descrição                                        |
|-------------------|----------|-------------|--------------------------------------------------|
| `quantidade`       | inteiro  | opcional    | Número de questões por cartão (padrão: 30)      |
| `marcar`           | booleano | opcional    | Se as respostas corretas devem ser marcadas     |

📎 **Retorno:** Arquivo PDF com os cartões.

---

### 📄 `POST /corrigir`

Corrige um cartão-resposta baseado em uma imagem (base64).

#### Corpo esperado (JSON):

```json
{
  "imagem_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "gabarito": {
    "1": "A",
    "2": "B",
    "3": "C"
  }
}
```

| Campo           | Tipo     | Obrigatório | Descrição                                           |
|----------------|----------|-------------|-----------------------------------------------------|
| `imagem_base64` | string   | sim         | Imagem do cartão codificada em base64               |
| `gabarito`      | objeto   | sim         | Dicionário com as respostas corretas por questão    |

📎 **Retorno:**  
```json
{
  "respostas_detectadas": {
    "1": "A",
    "2": "D",
    "3": "C"
  },
  "acertos": 2
}
```

---

## 🔗 Tecnologias usadas

- Python 3.10+
- Flask
- OpenCV (para análise de imagem)
- Matplotlib (para gerar os cartões)
- ReportLab (PDF)
- Flasgger (Swagger UI)
- Docker (para deploy)

---

## 🛠️ Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## ✉️ Contato

Desenvolvido por **Marco Antonio da Silva Mesquita**  
📬 Email: marco.mesquita.dev@gmail.com  
🌍 [respondeai.dirrocha.com](https://api-respondeai.dirrocha.com)
