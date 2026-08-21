document.addEventListener('DOMContentLoaded', function() {
    const regrasContainer = document.querySelector('#regras-form-container');
    const addRegraBtn = document.querySelector('#add-regra-btn');
    const emptyFormTemplate = document.querySelector('#empty-form').innerHTML;
    const totalFormsInput = document.querySelector('#id_regras-TOTAL_FORMS');

    // --- LÓGICA PARA ADICIONAR NOVAS REGRAS ---
    addRegraBtn.addEventListener('click', function() {
        // Pega o número atual de formulários
        let formNum = parseInt(totalFormsInput.value);
        
        // Cria um novo elemento div para o formulário
        const newForm = document.createElement('div');
        // Substitui o prefixo "__prefix__" pelo novo número do formulário
        newForm.innerHTML = emptyFormTemplate.replace(/__prefix__/g, formNum);
        
        // Atualiza o título do novo formulário
        newForm.querySelector('h4').textContent = `Regra #${formNum + 1}`;
        
        // Adiciona o novo formulário ao contêiner
        regrasContainer.appendChild(newForm);
        
        // Incrementa o contador total de formulários
        totalFormsInput.value = formNum + 1;

        // Reativa os listeners de eventos para os novos campos criados
        attachEventListeners(newForm);
    });


    // --- LÓGICA PARA CAMPOS CONDICIONAIS ---

    function toggleIscaQuantidade(form) {
        const iscaMovelCheckbox = form.querySelector('input[type="checkbox"][name$="-isca_movel"]');
        const quantidadeField = form.querySelector('.isca-quantidade-field');
        if (iscaMovelCheckbox && quantidadeField) {
            quantidadeField.style.display = iscaMovelCheckbox.checked ? 'block' : 'none';
        }
    }

    function toggleDDRField() {
        const tipoSeguroSelect = document.querySelector('#id_tipo_seguro');
        const ddrField = document.querySelector('.ddr-field');
        if (tipoSeguroSelect && ddrField) {
            ddrField.style.display = tipoSeguroSelect.value === 'DDR' ? 'block' : 'none';
        }
    }

    // Função para anexar os listeners. Usada tanto no carregamento da página quanto ao adicionar novas regras.
    function attachEventListeners(context) {
        // Listener para o checkbox "Isca Móvel"
        const iscaMovelCheckboxes = context.querySelectorAll('input[type="checkbox"][name$="-isca_movel"]');
        iscaMovelCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => toggleIscaQuantidade(checkbox.closest('.regra-embarque-form')));
            // Chama a função uma vez para definir o estado inicial
            toggleIscaQuantidade(checkbox.closest('.regra-embarque-form'));
        });
    }

    // Anexa os listeners para os formulários que já existem na página
    attachEventListeners(document);
    
    // Listener para o select "Tipo de Seguro"
    const tipoSeguroSelect = document.querySelector('#id_tipo_seguro');
    if (tipoSeguroSelect) {
        tipoSeguroSelect.addEventListener('change', toggleDDRField);
        // Chama a função uma vez para definir o estado inicial do campo DDR
        toggleDDRField();
    }
});