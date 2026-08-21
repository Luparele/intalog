// Arquivo: static/js/certificados_qsm.js

document.addEventListener('DOMContentLoaded', () => {
    // Lógica do Modal (sem alterações)
    const modal = document.getElementById('modal-certificado');
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

    // Lógica da Lista Expansível (sem alterações)
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

    // ALTERAÇÃO: Lógica para o botão de ocultar dentro dos detalhes
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