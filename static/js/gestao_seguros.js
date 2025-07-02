document.addEventListener('DOMContentLoaded', () => {
    // --- LÓGICA DO MODAL ---
    const modal = document.getElementById('modal-seguro');
    const abrirBtn = document.getElementById('abrir-modal-btn');
    const fecharBtns = document.querySelectorAll('.close-modal, .close-modal-btn');

    if (modal && abrirBtn && fecharBtns) {
        abrirBtn.onclick = function() {
            modal.style.display = 'flex';
        }

        fecharBtns.forEach(btn => {
            btn.onclick = function() {
                modal.style.display = 'none';
            }
        });

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }

    // --- LÓGICA DA LISTA EXPANSÍVEL ---
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
});