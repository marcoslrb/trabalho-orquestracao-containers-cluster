// ── Config ──
const API = '/api';

// ── Helpers ──
function showToast(msg, type = 'success') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

async function request(path, opts = {}) {
    try {
        const res = await fetch(`${API}${path}`, {
            headers: { 'Content-Type': 'application/json' },
            ...opts,
        });
        if (res.status === 204) return null;
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Erro ${res.status}`);
        }
        return res.json();
    } catch (e) {
        showToast(e.message, 'error');
        throw e;
    }
}

// ══════════════════════════════════════════════
// ── CATEGORIAS ──
// ══════════════════════════════════════════════

let categoriasCache = [];

async function carregarCategorias() {
    try {
        categoriasCache = await request('/categorias/');
        renderCategorias();
        atualizarSelectCategorias();
    } catch {
        document.getElementById('categorias-list').innerHTML =
            '<p class="empty">Erro ao carregar categorias.</p>';
    }
}

function renderCategorias() {
    const container = document.getElementById('categorias-list');
    if (!categoriasCache.length) {
        container.innerHTML = '<p class="empty">Nenhuma categoria cadastrada.</p>';
        return;
    }
    container.innerHTML = categoriasCache.map(c => `
        <div class="card">
            <h4>${escapeHtml(c.nome)}</h4>
            <p>${escapeHtml(c.descricao || 'Sem descrição')}</p>
            <div class="card-actions">
                <button class="btn btn-edit" onclick="editarCategoria(${c.id})">✏️ Editar</button>
                <button class="btn btn-danger" onclick="deletarCategoria(${c.id})">🗑️ Excluir</button>
            </div>
        </div>
    `).join('');
}

function atualizarSelectCategorias() {
    const sel = document.getElementById('produto-categoria');
    const valorAtual = sel.value;
    sel.innerHTML = '<option value="">Selecione...</option>' +
        categoriasCache.map(c =>
            `<option value="${c.id}">${escapeHtml(c.nome)}</option>`
        ).join('');
    sel.value = valorAtual;
}

// ── Form Categoria ──
const formCat = document.getElementById('form-categoria');
const btnCancelCat = document.getElementById('btn-cancelar-categoria');

formCat.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('categoria-id').value;
    const body = {
        nome: document.getElementById('categoria-nome').value.trim(),
        descricao: document.getElementById('categoria-descricao').value.trim() || null,
    };

    if (id) {
        await request(`/categorias/${id}`, { method: 'PUT', body: JSON.stringify(body) });
        showToast('Categoria atualizada!');
    } else {
        await request('/categorias/', { method: 'POST', body: JSON.stringify(body) });
        showToast('Categoria criada!');
    }
    resetFormCategoria();
    carregarCategorias();
    carregarProdutos();
});

function editarCategoria(id) {
    const cat = categoriasCache.find(c => c.id === id);
    if (!cat) return;
    document.getElementById('categoria-id').value = cat.id;
    document.getElementById('categoria-nome').value = cat.nome;
    document.getElementById('categoria-descricao').value = cat.descricao || '';
    document.getElementById('form-categoria-title').textContent = 'Editar Categoria';
    btnCancelCat.style.display = 'inline-block';
    formCat.scrollIntoView({ behavior: 'smooth' });
}

async function deletarCategoria(id) {
    if (!confirm('Excluir esta categoria e todos os seus produtos?')) return;
    await request(`/categorias/${id}`, { method: 'DELETE' });
    showToast('Categoria excluída!');
    carregarCategorias();
    carregarProdutos();
}

function resetFormCategoria() {
    formCat.reset();
    document.getElementById('categoria-id').value = '';
    document.getElementById('form-categoria-title').textContent = 'Nova Categoria';
    btnCancelCat.style.display = 'none';
}

btnCancelCat.addEventListener('click', resetFormCategoria);

// ══════════════════════════════════════════════
// ── PRODUTOS ──
// ══════════════════════════════════════════════

let produtosCache = [];

async function carregarProdutos() {
    try {
        produtosCache = await request('/produtos/');
        renderProdutos();
    } catch {
        document.getElementById('produtos-list').innerHTML =
            '<p class="empty">Erro ao carregar produtos.</p>';
    }
}

function renderProdutos() {
    const container = document.getElementById('produtos-list');
    if (!produtosCache.length) {
        container.innerHTML = '<p class="empty">Nenhum produto cadastrado.</p>';
        return;
    }
    container.innerHTML = produtosCache.map(p => {
        const cat = categoriasCache.find(c => c.id === p.categoria_id);
        return `
        <div class="card">
            <h4>${escapeHtml(p.nome)}</h4>
            <p>${escapeHtml(p.descricao || 'Sem descrição')}</p>
            <div class="card-meta">
                <span>R$ ${p.preco.toFixed(2)}</span>
                <span>Qtd: ${p.quantidade}</span>
                <span>📁 ${escapeHtml(cat ? cat.nome : 'N/A')}</span>
            </div>
            <div class="card-actions">
                <button class="btn btn-edit" onclick="editarProduto(${p.id})">✏️ Editar</button>
                <button class="btn btn-danger" onclick="deletarProduto(${p.id})">🗑️ Excluir</button>
            </div>
        </div>
    `}).join('');
}

// ── Form Produto ──
const formProd = document.getElementById('form-produto');
const btnCancelProd = document.getElementById('btn-cancelar-produto');

formProd.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('produto-id').value;
    const body = {
        nome: document.getElementById('produto-nome').value.trim(),
        descricao: document.getElementById('produto-descricao').value.trim() || null,
        preco: parseFloat(document.getElementById('produto-preco').value),
        quantidade: parseInt(document.getElementById('produto-quantidade').value),
        categoria_id: parseInt(document.getElementById('produto-categoria').value),
    };

    if (id) {
        await request(`/produtos/${id}`, { method: 'PUT', body: JSON.stringify(body) });
        showToast('Produto atualizado!');
    } else {
        await request('/produtos/', { method: 'POST', body: JSON.stringify(body) });
        showToast('Produto criado!');
    }
    resetFormProduto();
    carregarProdutos();
});

function editarProduto(id) {
    const prod = produtosCache.find(p => p.id === id);
    if (!prod) return;
    document.getElementById('produto-id').value = prod.id;
    document.getElementById('produto-nome').value = prod.nome;
    document.getElementById('produto-descricao').value = prod.descricao || '';
    document.getElementById('produto-preco').value = prod.preco;
    document.getElementById('produto-quantidade').value = prod.quantidade;
    document.getElementById('produto-categoria').value = prod.categoria_id;
    document.getElementById('form-produto-title').textContent = 'Editar Produto';
    btnCancelProd.style.display = 'inline-block';
    formProd.scrollIntoView({ behavior: 'smooth' });
}

async function deletarProduto(id) {
    if (!confirm('Excluir este produto?')) return;
    await request(`/produtos/${id}`, { method: 'DELETE' });
    showToast('Produto excluído!');
    carregarProdutos();
}

function resetFormProduto() {
    formProd.reset();
    document.getElementById('produto-id').value = '';
    document.getElementById('form-produto-title').textContent = 'Novo Produto';
    btnCancelProd.style.display = 'none';
}

btnCancelProd.addEventListener('click', resetFormProduto);

// ── Utils ──
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
    carregarCategorias();
    carregarProdutos();
});
