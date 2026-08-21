document.addEventListener('DOMContentLoaded', () => {
    // Lógica do Modal
    const modal = document.getElementById('modal-rotograma');
    const abrirBtn = document.getElementById('abrir-modal-btn');
    const fecharBtns = document.querySelectorAll('.close-modal, .close-modal-btn');

    if (modal && abrirBtn) {
        abrirBtn.onclick = () => { modal.style.display = 'flex'; };
    }
    if (modal && fecharBtns) {
        fecharBtns.forEach(btn => {
            btn.onclick = () => { modal.style.display = 'none'; };
        });
    }
    window.onclick = (event) => {
        if (event.target == modal) { modal.style.display = 'none'; }
    };

    // Lógica da Lista Expansível
    const headers = document.querySelectorAll('.item-header');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const container = header.closest('.item-container');
            const detalhes = container.querySelector('.item-detalhes');
            const botao = container.querySelector('.btn-visualizar');
            const isVisible = getComputedStyle(detalhes).display === 'block';

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