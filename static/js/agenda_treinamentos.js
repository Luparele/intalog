// Em static/js/agenda_treinamentos.js

document.addEventListener('DOMContentLoaded', () => {
    // --- LÓGICA DO MODAL ---
    const modal = document.getElementById('modal-treinamento');
    const abrirBtn = document.getElementById('abrir-modal-btn');
    if (modal && abrirBtn) {
        const fecharBtns = modal.querySelectorAll('.close-modal, .close-modal-btn');
        abrirBtn.onclick = function() { modal.style.display = 'flex'; };
        fecharBtns.forEach(btn => {
            btn.onclick = function() { modal.style.display = 'none'; };
        });
        window.onclick = function(event) {
            if (event.target == modal) { modal.style.display = 'none'; }
        };
    }

    // --- LÓGICA DA LISTA EXPANSÍVEL (CLIQUE NO HEADER) ---
    const headers = document.querySelectorAll('.item-header');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const container = header.closest('.item-container');
            const detalhes = container.querySelector('.item-detalhes');
            const botao = container.querySelector('.btn-visualizar');
            const isVisible = detalhes.style.display === 'block';

            if (isVisible) {
                detalhes.style.display = 'none';
                botao.textContent = 'Visualizar';
            } else {
                detalhes.style.display = 'block';
                botao.textContent = 'Ocultar';
            }
        });
    });

    // --- LÓGICA PARA O BOTÃO DE OCULTAR DENTRO DOS DETALHES ---
    const ocultarBtns = document.querySelectorAll('.btn-ocultar-detalhes');
    ocultarBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const container = btn.closest('.item-container');
            const detalhes = container.querySelector('.item-detalhes');
            const botaoHeader = container.querySelector('.btn-visualizar');

            detalhes.style.display = 'none';
            botaoHeader.textContent = 'Visualizar';
        });
    });
});