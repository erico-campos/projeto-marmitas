from flask import Flask, render_template, request, jsonify
import json
import os
import time

app = Flask(__name__)

DB_FILE = 'pedidos.json'
ADMIN_FILE = 'configs_salvas.json'
CUSTOS_FILE = 'custos.json'
USUARIOS_FILE = 'usuarios.json'  # Arquivo para armazenar usuários

def carregar(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def salvar(dados, arquivo):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

# Rota de Login Dinâmica
@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    usuarios = carregar(USUARIOS_FILE)

    # Validação: procura o usuário no arquivo
    for u in usuarios:
        if u['usuario'] == dados.get('usuario') and u['senha'] == dados.get('senha'):
            return jsonify({"status": "sucesso"})

    # Fallback para o admin original se nenhum usuário for criado
    if dados.get('usuario') == "admin" and dados.get('senha') == "1234":
        return jsonify({"status": "sucesso"})

    return jsonify({"status": "erro", "mensagem": "Usuário ou senha incorretos"})

# Rota para cadastrar novo usuário
@app.route('/salvar_usuario', methods=['POST'])
def salvar_usuario():
    dados = request.json
    usuarios = carregar(USUARIOS_FILE)
    # Adiciona novo usuário
    usuarios.append({'usuario': dados['usuario'], 'senha': dados['senha']})
    salvar(usuarios, USUARIOS_FILE)
    return jsonify({"status": "sucesso"})

# Rota para excluir usuário
@app.route('/excluir_usuario', methods=['POST'])
def excluir_usuario():
    user_to_delete = request.json.get('usuario')
    usuarios = carregar(USUARIOS_FILE)
    # Filtra mantendo apenas os usuários que NÃO possuem o nome enviado
    novos = [u for u in usuarios if u['usuario'] != user_to_delete]
    salvar(novos, USUARIOS_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/listar_usuarios', methods=['GET'])
def listar_usuarios():
    return jsonify(carregar(USUARIOS_FILE))

# --- DEMAIS ROTAS ---
@app.route('/salvar_config', methods=['POST'])
def salvar_config():
    nova_config = request.json
    configs = carregar(ADMIN_FILE)
    if nova_config.get('id'):
        for i, c in enumerate(configs):
            if str(c.get('id')) == str(nova_config['id']):
                configs[i] = nova_config
                salvar(configs, ADMIN_FILE)
                return jsonify({"status": "sucesso"})
    nova_config['id'] = int(time.time())
    configs.append(nova_config)
    salvar(configs, ADMIN_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/listar_configs', methods=['GET'])
def listar_configs(): return jsonify(carregar(ADMIN_FILE))

@app.route('/excluir_config', methods=['POST'])
def excluir_config():
    config_id = request.json.get('id')
    configs = carregar(ADMIN_FILE)
    novas = [c for c in configs if str(c.get('id')) != str(config_id)]
    salvar(novas, ADMIN_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/salvar_pedido', methods=['POST'])
def salvar_pedido():
    dados = request.json
    todos = carregar(DB_FILE)
    if 'id' in dados and dados['id']:
        for i, p in enumerate(todos):
            if str(p.get('id')) == str(dados['id']):
                todos[i] = dados
                salvar(todos, DB_FILE)
                return jsonify({"status": "sucesso"})
    dados['id'] = int(time.time())
    dados['pronto'] = False
    todos.append(dados)
    salvar(todos, DB_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/listar_pedidos', methods=['GET'])
def listar_pedidos(): return jsonify(carregar(DB_FILE))

@app.route('/excluir_pedido', methods=['POST'])
def excluir_pedido():
    pedido_id = request.json.get('id')
    todos = carregar(DB_FILE)
    novos = [p for p in todos if str(p.get('id')) != str(pedido_id)]
    salvar(novos, DB_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/atualizar_producao', methods=['POST'])
def atualizar_producao():
    pedido_id = request.json.get('id')
    todos = carregar(DB_FILE)
    for p in todos:
        if str(p.get('id')) == str(pedido_id):
            p['pronto'] = not p.get('pronto', False)
            break
    salvar(todos, DB_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/limpar_ciclo', methods=['POST'])
def limpar_ciclo():
    salvar([], DB_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/listar_custos/<lote_id>', methods=['GET'])
def listar_custos(lote_id):
    custos = carregar(CUSTOS_FILE)
    return jsonify([c for c in custos if str(c.get('lote_id')) == str(lote_id)])

@app.route('/salvar_custo', methods=['POST'])
def salvar_custo():
    dados = request.json
    custos = carregar(CUSTOS_FILE)
    dados['id'] = int(time.time())
    custos.append(dados)
    salvar(custos, CUSTOS_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/excluir_custo', methods=['POST'])
def excluir_custo():
    custo_id = request.json.get('id')
    custos = carregar(CUSTOS_FILE)
    novos = [c for c in custos if str(c.get('id')) != str(custo_id)]
    salvar(novos, CUSTOS_FILE)
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    app.run(debug=True)
