document.addEventListener('DOMContentLoaded', () => {

    // --- MANIPULAÇÃO DE MODAIS (LÓGICA GERAL) ---
    const modalChecklist = document.getElementById('modal-checklist');
    const veiculoSelect = modalChecklist ? modalChecklist.querySelector('#id_veiculo') : null;
    const grSelect = modalChecklist ? modalChecklist.querySelector('#id_gr') : null;
    const checklistForm = modalChecklist ? modalChecklist.querySelector('form') : null;

    function setupModal(buttonId, modalId) {
        const modal = document.getElementById(modalId);
        const abrirBtn = document.getElementById(buttonId);
        if (modal) {
            const fecharBtns = modal.querySelectorAll('.close-modal, .close-modal-btn');
            if (abrirBtn) {
                abrirBtn.onclick = () => { modal.style.display = 'flex'; };
            }
            if (fecharBtns) {
                fecharBtns.forEach(btn => {
                    btn.onclick = () => {
                        modal.style.display = 'none';
                        if (modal.id === 'modal-checklist' && veiculoSelect && grSelect) {
                            veiculoSelect.disabled = false;
                            grSelect.disabled = false;
                        }
                    };
                });
            }
            window.addEventListener('click', (event) => {
                if (event.target == modal) {
                    modal.style.display = 'none';
                    if (modal.id === 'modal-checklist' && veiculoSelect && grSelect) {
                        veiculoSelect.disabled = false;
                        grSelect.disabled = false;
                    }
                }
            });
        }
    }
    setupModal('abrir-modal-veiculo', 'modal-veiculo');
    setupModal('abrir-modal-gr', 'modal-gr');
    setupModal('abrir-modal-checklist', 'modal-checklist');


    // --- LÓGICA DO FORMULÁRIO DE CHECKLIST (COM CAMPOS DE DATA ALTERNATIVOS) ---
    if (modalChecklist) {
        const aprovadoCheckbox = modalChecklist.querySelector('#id_aprovado');
        const camposDataAprovado = modalChecklist.querySelector('#campos-data-aprovado');
        const campoReprovado = modalChecklist.querySelector('#campo-reprovado');
        const dataAprovacaoInput = modalChecklist.querySelector('#id_data_aprovacao');
        const dataValidadeInput = modalChecklist.querySelector('#id_data_validade_manual');

        function toggleChecklistFields() {
            if (aprovadoCheckbox.checked) {
                camposDataAprovado.style.display = 'block';
                campoReprovado.style.display = 'none';
            } else {
                camposDataAprovado.style.display = 'none';
                campoReprovado.style.display = 'block';
                // Limpa e habilita os campos de data se desmarcar "Aprovado"
                dataAprovacaoInput.value = '';
                dataValidadeInput.value = '';
                dataAprovacaoInput.disabled = false;
                dataValidadeInput.disabled = false;
            }
        }

        dataAprovacaoInput.addEventListener('input', () => {
            if (dataAprovacaoInput.value) {
                dataValidadeInput.value = ''; // Limpa o outro campo
                dataValidadeInput.disabled = true;
            } else {
                dataValidadeInput.disabled = false;
            }
        });

        dataValidadeInput.addEventListener('input', () => {
            if (dataValidadeInput.value) {
                dataAprovacaoInput.value = ''; // Limpa o outro campo
                dataAprovacaoInput.disabled = true;
            } else {
                dataAprovacaoInput.disabled = false;
            }
        });

        aprovadoCheckbox.addEventListener('change', toggleChecklistFields);
        toggleChecklistFields(); // Roda a função uma vez para o estado inicial
    }

    // --- LÓGICA DE HOVER NA TABELA ---
    const tabelas = document.querySelectorAll('.tabela-checklist');
    tabelas.forEach(tabela => {
        tabela.querySelectorAll('tbody tr').forEach(row => {
            row.addEventListener('mouseover', () => { row.classList.add('linha-hover'); });
            row.addEventListener('mouseout', () => { row.classList.remove('linha-hover'); });
        });
    });

    // --- LÓGICA DE DUPLO CLIQUE ---
    document.querySelectorAll('.checklist-cell').forEach(cell => {
        cell.addEventListener('dblclick', function() {
            const veiculoId = this.closest('tr').dataset.veiculoId;
            const grId = this.dataset.grId;
            if (veiculoSelect && grSelect) {
                veiculoSelect.value = veiculoId;
                grSelect.value = grId;
                veiculoSelect.disabled = true;
                grSelect.disabled = true;
            }
            if (modalChecklist) {
                modalChecklist.style.display = 'flex';
            }
        });
    });

    // --- LÓGICA DE SUBMIT DO FORMULÁRIO ---
    if (checklistForm) {
        checklistForm.addEventListener('submit', function() {
            if (veiculoSelect) veiculoSelect.disabled = false;
            if (grSelect) grSelect.disabled = false;
        });
    }
});