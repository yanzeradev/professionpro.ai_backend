from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import markdown
import unicodedata
import os

# Configuração da API do Google
GOOGLE_GEMINI_API_KEY = 'AIzaSyDJ9ixc9hziZ6ckYz_Wbj0TuqwYW7usXUA'  # Substitua pela sua chave real
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Função para remover acentos
def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Função para verificar se a pergunta é sobre profissões
def is_profession_related(pergunta, palavras_chave):
    pergunta_normalizada = remover_acentos(pergunta.lower())  # Normaliza a pergunta
    return any(remover_acentos(palavra).lower() in pergunta_normalizada for palavra in palavras_chave)

# Função para ler palavras de um arquivo .txt
def carregar_palavras_chave(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            conteudo = arquivo.read()
            palavras_chave = [palavra.strip() for palavra in conteudo.split(',')]
        return palavras_chave
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho_arquivo}")
        return []

# Carregar palavras-chave
caminho_arquivo = 'palavras_chave.txt'
palavras_chave = carregar_palavras_chave(caminho_arquivo)

# Inicialização do Flask
app = Flask(__name__)
CORS(app)

# Lista para armazenar o histórico da conversa
historico_conversa = []

@app.route('/pergunta', methods=['POST'])
def pergunta():
    # Obtém a pergunta do corpo da requisição JSON
    data = request.json
    pergunta_usuario = data.get('pergunta', '').strip()

    # Verifica se a pergunta está relacionada a profissões
    if is_profession_related(pergunta_usuario, palavras_chave):
        # Adiciona a pergunta do usuário ao histórico
        historico_conversa.append(f"Usuário: {pergunta_usuario}")
        
        # Cria o contexto da conversa
        contexto_conversa = '\n'.join(historico_conversa)
        
        # Gera a resposta usando o modelo, passando o contexto da conversa
        resposta = model.generate_content(contexto_conversa)

        # Adiciona a resposta ao histórico
        historico_conversa.append(f"Chatbot: {resposta.text}")

        # Converte o markdown para HTML
        resposta_formatada = markdown.markdown(resposta.text)
        return jsonify({'resposta': resposta_formatada})
    else:
        return jsonify({'resposta': "Desculpe, eu só posso responder perguntas relacionadas a profissões."})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usa a porta definida pelo ambiente ou 5000 como padrão
    app.run(host='0.0.0.0', port=port, debug=True)
