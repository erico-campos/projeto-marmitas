'''
from flask import Flask, render_template, request, jsonify
import json
import os
import time

app = Flask(__name__)

DB_FILE = 'pedidos.json'
ADMIN_FILE = 'configs_salvas.json'
CUSTOS_FILE = 'custos.json'

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

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    if dados.get('usuario') == "admin" and dados.get('senha') == "1234":
        return jsonify({"status": "sucesso"})
    return jsonify({"status": "erro", "mensagem": "Usuário ou senha incorretos"})

# --- ROTAS DE CONFIGURAÇÃO (ADM) ---
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
def listar_configs():
    return jsonify(carregar(ADMIN_FILE))

@app.route('/excluir_config', methods=['POST'])
def excluir_config():
    config_id = request.json.get('id')
    configs = carregar(ADMIN_FILE)
    novas = [c for c in configs if str(c.get('id')) != str(config_id)]
    salvar(novas, ADMIN_FILE)
    return jsonify({"status": "sucesso"})

# --- ROTAS DE PEDIDOS ---
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
def listar_pedidos():
    return jsonify(carregar(DB_FILE))

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

# --- NOVAS ROTAS DE CUSTOS ---
@app.route('/salvar_custo', methods=['POST'])
def salvar_custo():
    dados = request.json
    custos = carregar(CUSTOS_FILE)
    dados['id'] = int(time.time())
    custos.append(dados)
    salvar(custos, CUSTOS_FILE)
    return jsonify({"status": "sucesso"})

@app.route('/listar_custos/<lote_id>', methods=['GET'])
def listar_custos(lote_id):
    todos = carregar(CUSTOS_FILE)
    filtrados = [c for c in todos if str(c.get('lote_id')) == str(lote_id)]
    return jsonify(filtrados)

@app.route('/excluir_custo', methods=['POST'])
def excluir_custo():
    id_custo = request.json.get('id')
    todos = carregar(CUSTOS_FILE)
    novos = [c for c in todos if str(c.get('id')) != str(id_custo)]
    salvar(novos, CUSTOS_FILE)
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    app.run(debug=True)

'''


'''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sabor com Propósito - Gestão</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        :root { --primary: #000000; --secondary: #d4af37; --bg: #121212; --card: #1e1e1e; --text: #ffffff; --danger: #d9534f; --success: #27ae60; }
        #tela-bloqueio { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 9999; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: opacity 0.5s; }
        #logo-inicio { width: 280px; cursor: pointer; }
        #formulario-login { display: none; margin-top: 20px; width: 280px; text-align: center; }
        .input-login { background: #1a1a1a; color: #fff; border: 1px solid var(--secondary); margin-bottom: 10px; width: 100%; padding: 12px; border-radius: 8px; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; }
        nav { background: var(--primary); display: flex; justify-content: center; gap: 5px; padding: 10px; position: sticky; top: 0; z-index: 1000; border-bottom: 1px solid var(--secondary); }
        nav button { background: none; border: none; color: white; font-size: 0.8rem; cursor: pointer; padding: 10px; border-radius: 5px; }
        nav button.active { background: var(--secondary); color: black; font-weight: bold; }
        .tab-content { display: none; padding: 20px; max-width: 1000px; margin: auto; }
        .tab-content.active { display: block; }
        .card { background: var(--card); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #333; }
        .row-item { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
        input, select, textarea { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #2a2a2a; color: white; box-sizing: border-box; }
        .btn-main { background: var(--secondary); color: black; border: none; border-radius: 8px; padding: 15px; width: 100%; font-size: 1.1rem; cursor: pointer; font-weight: bold; margin-top: 10px; }
        .btn-danger { background: var(--danger); color: white; border: none; border-radius: 8px; padding: 10px; cursor: pointer; margin-top: 20px; width: 100%; }
        .btn-acao { border: none; background: none; cursor: pointer; font-size: 1.1rem; color: var(--secondary); }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #333; }
        .linha-paga { background-color: #1b3320 !important; color: #4ade80 !important; }
        .resumo-financeiro { display: flex; justify-content: space-between; margin-bottom: 15px; gap: 10px; flex-wrap: wrap; }
        .financeiro-box { background: #2a2a2a; padding: 10px; border-radius: 8px; flex: 1; min-width: 100px; text-align: center; border-bottom: 3px solid #444; }
        .val-recebido { color: #4ade80; border-color: #27ae60; }
        .val-pendente { color: var(--secondary); border-color: var(--secondary); }
        .val-custo { color: #ff4d4d; border-color: #d9534f; }
    </style>
</head>
<body onload="verificarLogin()">

<div id="tela-bloqueio">
    <img src="{{ url_for('static', filename='logo.jpg') }}" id="logo-inicio" onclick="mostrarLogin()">
    <div id="formulario-login">
        <input type="text" id="user" class="input-login" placeholder="Usuário">
        <input type="password" id="pass" class="input-login" placeholder="Senha">
        <button class="btn-main" onclick="efetuarLogin()">ENTRAR</button>
        <p id="erro-login" style="color: #ff4d4d; margin-top: 10px; display: none;"></p>
    </div>
</div>

<nav>
    <button onclick="switchTab('aba-producao')" id="btn-producao" class="active"><i class="fas fa-tasks"></i> PRODUÇÃO</button>
    <button onclick="switchTab('aba-novo')" id="btn-novo"><i class="fas fa-plus"></i> PEDIDO</button>
    <button onclick="switchTab('aba-financeiro')" id="btn-financeiro"><i class="fas fa-wallet"></i> GASTOS</button>
    <button onclick="switchTab('aba-adm')" id="btn-adm"><i class="fas fa-cog"></i> ADM</button>
</nav>

<div id="aba-producao" class="tab-content active">
    <div class="card">
        <h3><i class="fas fa-chart-bar" style="color: var(--secondary);"></i> Pendências de Preparo</h3>
        <div style="height: 180px;"><canvas id="meuGrafico"></canvas></div>
    </div>
    <div class="card">
        <div class="resumo-financeiro">
            <div class="financeiro-box val-recebido"><strong>Pago</strong><span id="valorPago">R$ 0,00</span></div>
            <div class="financeiro-box val-pendente"><strong>Pendente</strong><span id="valorPendente">R$ 0,00</span></div>
        </div>
        <table id="tabelaPedidos">
            <thead><tr><th>Cliente e Pedido</th><th style="text-align:center;">Tipo</th><th>Pago</th><th>Ação</th></tr></thead>
            <tbody></tbody>
        </table>
        <button class="btn-danger" onclick="fimDeCiclo()">FINALIZAR CICLO</button>
    </div>
</div>

<div id="aba-novo" class="tab-content">
    <div class="card">
        <h3 id="tituloPedido" style="color: var(--secondary);">Anotar Pedido</h3>
        <div id="formPedidoConteudo">
            <input type="text" id="nomeCliente" placeholder="Nome do Cliente">
            <select id="tipoEntrega" style="margin-top:10px;" onchange="document.getElementById('endDiv').style.display = this.value === 'sim' ? 'block' : 'none'">
                <option value="nao">Retirada</option>
                <option value="sim">Entrega</option>
            </select>
            <div id="endDiv" style="display:none; margin-top:10px;"><input type="text" id="endereco" placeholder="Endereço"></div>
            <div id="opcoesLoteAtivo" style="margin-top:10px;"></div>
            <textarea id="obsPedido" placeholder="Observações..." style="margin-top:10px;"></textarea>
            <button class="btn-main" onclick="salvarPedido()">SALVAR PEDIDO</button>
        </div>
    </div>
</div>

<div id="aba-financeiro" class="tab-content">
    <div id="area-pdf">
        <div class="card">
            <h3 style="color: var(--secondary);">Resumo de Lucratividade</h3>
            <div class="resumo-financeiro">
                <div class="financeiro-box val-recebido"><strong>Vendas</strong><span id="fin-vendas">R$ 0,00</span></div>
                <div class="financeiro-box val-custo"><strong>Materiais</strong><span id="fin-custos">R$ 0,00</span></div>
                <div class="financeiro-box" style="color:#fff; background:#222;"><strong>LUCRO</strong><span id="fin-lucro">R$ 0,00</span></div>
            </div>
            <div id="graficoLucroContainer" style="height: 150px; margin-top:10px;">
                <canvas id="chartLucro"></canvas>
            </div>
        </div>
        <div class="card">
            <h4>Materiais Comprados</h4>
            <div class="row-item no-print">
                <input type="text" id="insumo-nome" placeholder="Item">
                <input type="number" id="insumo-valor" style="width:100px;" placeholder="R$">
                <button class="btn-acao" onclick="adicionarGasto()"><i class="fas fa-plus-circle"></i></button>
            </div>
            <table id="tabelaCustos">
                <thead><tr><th>Item</th><th>Valor</th><th class="no-print">Ação</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
    <button class="btn-main" style="background:#444; color:white;" onclick="gerarPDFRelatorio()"><i class="fas fa-file-pdf"></i> GERAR RELATÓRIO PDF</button>
</div>

<div id="aba-adm" class="tab-content">
    <div class="card">
        <h3>Gerenciar Cardápios</h3>
        <button class="btn-main" onclick="toggleSecao('secaoPratos')">PRATOS</button>
        <div id="secaoPratos" style="display:none;"><div id="listaAdmPratos"></div><button class="btn-main" onclick="addLinhaAdm('listaAdmPratos')">+ Novo Prato</button></div>
        <button class="btn-main" onclick="toggleSecao('secaoSobremesas')">SOBREMESAS</button>
        <div id="secaoSobremesas" style="display:none;"><div id="listaAdmSobremesas"></div><button class="btn-main" onclick="addLinhaAdm('listaAdmSobremesas')">+ Nova Sobremesa</button></div>
        <button class="btn-main" style="border: 2px solid var(--secondary);" onclick="salvarConfig()">SALVAR LOTE</button>
    </div>
    <div id="listaConfigsSalvas"></div>
</div>

<script>
    let chartInstance = null;
    let chartLucro = null;
    let pedidoEdicaoId = null;

    function mostrarLogin() { document.getElementById('formulario-login').style.display = 'block'; }
    async function efetuarLogin() {
        const usuario = document.getElementById('user').value;
        const senha = document.getElementById('pass').value;
        const res = await fetch('/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({usuario, senha}) });
        const dados = await res.json();
        if (dados.status === "sucesso") { sessionStorage.setItem('logado', 'true'); document.getElementById('tela-bloqueio').style.display = 'none'; inicializarApp(); }
        else { alert(dados.mensagem); }
    }
    function verificarLogin() { if (sessionStorage.getItem('logado') === 'true') { document.getElementById('tela-bloqueio').style.display = 'none'; inicializarApp(); } }

    async function inicializarApp() { await carregarLoteAtivo(); carregarPedidos(); carregarConfigsSalvas(); atualizarFinanceiroDetalhado(); }

    function switchTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        document.getElementById('btn-' + tabId.split('-')[1]).classList.add('active');
        if(tabId === 'aba-financeiro') atualizarFinanceiroDetalhado();
    }

    async function carregarLoteAtivo() {
        const res = await fetch('/listar_configs');
        const configs = await res.json();
        const div = document.getElementById('opcoesLoteAtivo');
        const idAtivo = localStorage.getItem('loteAtivoId');
        if(!idAtivo) return div.innerHTML = "Ative um cardápio no ADM";
        let config = configs.find(c => String(c.id) === String(idAtivo));
        if(config) {
            let html = "";
            [...config.pratos, ...config.sobremesas].forEach(p => {
                html += `<div class='row-item-pedido card' style='display:flex; gap:5px; padding:10px; margin-bottom:5px;'><input type='number' class='qtd-item' value='0' style='width:60px;'><input type='text' class='nome-item-pedido' value='${p.nome}' style='flex:2;' readonly><input type='number' class='preco-item-pedido' value='${p.preco}' style='width:80px;'></div>`;
            });
            div.innerHTML = html;
        }
    }

    async function carregarPedidos() {
        const res = await fetch('/listar_pedidos');
        const pedidos = await res.json();
        const corpo = document.querySelector('#tabelaPedidos tbody');
        corpo.innerHTML = "";
        let t = {}; let totalPago = 0; let totalPendente = 0;
        const idLoteAtivo = localStorage.getItem('loteAtivoId');

        pedidos.forEach(p => {
            if (String(p.lote_id) === String(idLoteAtivo)) {
                let valor = 0; let listaItens = "";
                p.itens.forEach(i => {
                    valor += (i.qtd * i.preco);
                    listaItens += `<div style="font-size:0.8rem; color:#aaa; margin-left:10px;">• ${i.qtd}x ${i.desc}</div>`;
                });
                if(p.pronto) totalPago += valor; else { totalPendente += valor; p.itens.forEach(i => t[i.desc] = (t[i.desc] || 0) + parseInt(i.qtd)); }
                const tr = document.createElement('tr');
                if(p.pronto) tr.classList.add('linha-paga');
                tr.innerHTML = `<td><strong>${p.cliente}</strong>${listaItens}${p.obs?`<small style="color:red;display:block;margin-left:10px;">obs: ${p.obs}</small>`:''}</td><td style="text-align:center;">${p.entrega=='sim'?'🚚':'🏠'}</td><td><input type="checkbox" ${p.pronto?'checked':''} onclick="marcarPronto('${p.id}')"></td><td><button class="btn-acao" onclick="excluirPedido('${p.id}')"><i class="fas fa-trash"></i></button></td>`;
                corpo.appendChild(tr);
            }
        });
        document.getElementById('valorPago').innerText = `R$ ${totalPago.toFixed(2)}`;
        document.getElementById('valorPendente').innerText = `R$ ${totalPendente.toFixed(2)}`;
        desenharGrafico(t);
    }

    async function salvarPedido() {
        const itens = [];
        document.querySelectorAll('#opcoesLoteAtivo .row-item-pedido').forEach(row => {
            const qtd = row.querySelector('.qtd-item').value;
            if(parseInt(qtd) > 0) itens.push({ qtd, desc: row.querySelector('.nome-item-pedido').value, preco: row.querySelector('.preco-item-pedido').value });
        });
        if(!document.getElementById('nomeCliente').value) return alert("Insira o nome do cliente");
        const d = { id: pedidoEdicaoId, lote_id: localStorage.getItem('loteAtivoId'), cliente: document.getElementById('nomeCliente').value, entrega: document.getElementById('tipoEntrega').value, endereco: document.getElementById('endereco').value, itens: itens, obs: document.getElementById('obsPedido').value };
        await fetch('/salvar_pedido', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(d) });
        location.reload();
    }

    async function atualizarFinanceiroDetalhado() {
        const loteId = localStorage.getItem('loteAtivoId');
        if (!loteId) return;
        const resP = await fetch('/listar_pedidos');
        const pedidos = await resP.json();
        let totalVendas = 0;
        pedidos.filter(p => String(p.lote_id) === String(loteId)).forEach(p => p.itens.forEach(i => totalVendas += (i.qtd * i.preco)));
        const resC = await fetch(`/listar_custos/${loteId}`);
        const custos = await resC.json();
        let totalCustos = 0;
        const corpoCustos = document.querySelector('#tabelaCustos tbody');
        corpoCustos.innerHTML = "";
        custos.forEach(c => {
            totalCustos += parseFloat(c.valor);
            corpoCustos.innerHTML += `<tr><td>${c.item}</td><td>R$ ${parseFloat(c.valor).toFixed(2)}</td><td class="no-print"><button class="btn-acao" onclick="excluirCusto(${c.id})"><i class="fas fa-trash"></i></button></td></tr>`;
        });
        document.getElementById('fin-vendas').innerText = `R$ ${totalVendas.toFixed(2)}`;
        document.getElementById('fin-custos').innerText = `R$ ${totalCustos.toFixed(2)}`;
        document.getElementById('fin-lucro').innerText = `R$ ${(totalVendas - totalCustos).toFixed(2)}`;
        if(totalVendas > 0 || totalCustos > 0) desenharGraficoLucro(totalVendas, totalCustos);
    }

    async function adicionarGasto() {
        const item = document.getElementById('insumo-nome').value;
        const valor = document.getElementById('insumo-valor').value;
        const lote_id = localStorage.getItem('loteAtivoId');
        if(!item || !valor) return;
        await fetch('/salvar_custo', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({lote_id, item, valor}) });
        document.getElementById('insumo-nome').value = ""; document.getElementById('insumo-valor').value = "";
        atualizarFinanceiroDetalhado();
    }

    async function excluirCusto(id) { await fetch('/excluir_custo', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id}) }); atualizarFinanceiroDetalhado(); }

    function desenharGraficoLucro(vendas, custos) {
        const ctx = document.getElementById('chartLucro').getContext('2d');
        if(chartLucro) chartLucro.destroy();
        chartLucro = new Chart(ctx, { type: 'pie', data: { labels: ['Lucro', 'Custos'], datasets: [{ data: [vendas-custos, custos], backgroundColor: ['#27ae60', '#d9534f'] }] }, options: { maintainAspectRatio: false, plugins: { legend: { labels: { color: 'white' } } } } });
    }

    function gerarPDFRelatorio() {
        const element = document.getElementById('area-pdf');
        html2pdf().set({ margin: 10, filename: 'Relatorio_Sabor.pdf', html2canvas: { scale: 2, backgroundColor: '#121212' }, jsPDF: { unit: 'mm', format: 'a4' } }).from(element).save();
    }

    function desenharGrafico(d) {
        const ctx = document.getElementById('meuGrafico').getContext('2d');
        if(chartInstance) chartInstance.destroy();
        if(Object.keys(d).length === 0) return;
        chartInstance = new Chart(ctx, { type: 'bar', data: { labels: Object.keys(d), datasets: [{ label: 'Preparar (Qtd Total)', data: Object.values(d), backgroundColor: '#d4af37' }] }, options: { maintainAspectRatio: false, scales: { y: { ticks: { color: 'white', stepSize: 1 } }, x: { ticks: { color: 'white' } } } } });
    }

    async function marcarPronto(id) { await fetch('/atualizar_producao', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id}) }); carregarPedidos(); }
    async function excluirPedido(id) { if(confirm("Excluir?")) { await fetch('/excluir_pedido', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id}) }); carregarPedidos(); } }
    async function carregarConfigsSalvas() {
        const res = await fetch('/listar_configs');
        const configs = await res.json();
        const div = document.getElementById('listaConfigsSalvas');
        div.innerHTML = configs.map(c => `<div class='card' style='display:flex; justify-content:space-between;'><span>${c.titulo}</span><div><button onclick="ativarLote('${c.id}')" class='btn-acao'>Ativar</button><button onclick="excluirConfig('${c.id}')" class='btn-acao' style='color:red'>Excluir</button></div></div>`).join('');
    }
    function ativarLote(id) { localStorage.setItem('loteAtivoId', id); location.reload(); }
    async function excluirConfig(id) { if(confirm("Excluir lote?")) { await fetch('/excluir_config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id}) }); carregarConfigsSalvas(); } }
    function toggleSecao(id) { const s = document.getElementById(id); s.style.display = s.style.display === 'block' ? 'none' : 'block'; }
    function addLinhaAdm(id) { const d = document.getElementById(id); const r = document.createElement('div'); r.className = 'row-item'; r.innerHTML = `<input type="text" placeholder="Nome"> <input type="number" style="width:80px;" placeholder="R$">`; d.appendChild(r); }
    async function salvarConfig() {
        const titulo = prompt("Nome do Lote:"); if(!titulo) return;
        const pratos = Array.from(document.getElementById('listaAdmPratos').children).map(r => ({nome: r.children[0].value, preco: r.children[1].value}));
        const sobremesas = Array.from(document.getElementById('listaAdmSobremesas').children).map(r => ({nome: r.children[0].value, preco: r.children[1].value}));
        await fetch('/salvar_config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({titulo, pratos, sobremesas}) });
        location.reload();
    }
    async function fimDeCiclo() { if(confirm("Limpar pedidos?")) { await fetch('/limpar_ciclo', { method: 'POST' }); location.reload(); } }
</script>
</body>
</html>

'''