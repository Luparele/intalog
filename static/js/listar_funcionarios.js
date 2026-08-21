document.addEventListener('DOMContentLoaded', () => {
    const botoes = document.querySelectorAll('.btn-visualizar');

    botoes.forEach(botao => {
        botao.addEventListener('click', () => {
            // Encontra o container do detalhe correspondente ao botão clicado
            const detalhes = botao.closest('.funcionario-item').querySelector('.funcionario-detalhes');

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