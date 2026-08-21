document.addEventListener('DOMContentLoaded', () => {
    // --- LÓGICA PARA MOSTRAR/OCULTAR O FORMULÁRIO ---
    const toggleBtn = document.getElementById('toggle-form-btn');
    const formContainer = document.getElementById('inline-form-container');

    if (toggleBtn && formContainer) {
        toggleBtn.addEventListener('click', () => {
            const isVisible = formContainer.style.display === 'block';

            if (isVisible) {
                formContainer.style.display = 'none';
                toggleBtn.textContent = '+ Adicionar GR';
                toggleBtn.classList.remove('btn-secondary'); // Volta a ser o botão principal
            } else {
                formContainer.style.display = 'block';
                toggleBtn.textContent = 'Ocultar Formulário';
                toggleBtn.classList.add('btn-secondary'); // Muda a cor para indicar "cancelar"
            }
        });
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

    // --- LÓGICA PARA MÁSCARA DE CNPJ NO MODAL (SE APLICÁVEL) ---
    // Se você tiver um campo CNPJ no formulário de Gerenciadora, essa lógica pode ser útil
    // const cnpjInput = document.querySelector('#modal-gr form #id_cnpj');
    // if (cnpjInput) { ... }
});