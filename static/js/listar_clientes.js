document.addEventListener('DOMContentLoaded', () => {
    // Seleciona todos os cabeçalhos dos itens, pois o clique pode ser na área toda
    const headers = document.querySelectorAll('.item-header');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            // Encontra os detalhes e o botão correspondentes dentro do mesmo container
            const container = header.closest('.item-container');
            const detalhes = container.querySelector('.item-detalhes');
            const botao = container.querySelector('.btn-visualizar');

            // Verifica se está visível
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