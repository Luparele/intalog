document.addEventListener('DOMContentLoaded', () => {

    // --- FUNÇÃO PARA PEGAR O CSRF TOKEN ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // --- MANIPULAÇÃO DE MODAIS ---
    const modalCriacao = document.getElementById('modal-criacao');
    const modalVisualizacao = document.getElementById('modal-visualizacao');

    // Modal de Criação
    if (document.getElementById('abrir-modal-criacao')) {
        document.getElementById('abrir-modal-criacao').addEventListener('click', () => {
            if (modalCriacao) modalCriacao.style.display = 'flex';
        });
    }

    // Fechar modais
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        if (!modal) return;
        const closeButton = modal.querySelector('.close-modal');
        const closeButtonBtn = modal.querySelector('.close-modal-btn');

        if (closeButton) {
            closeButton.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }
        if (closeButtonBtn) {
            closeButtonBtn.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }
        window.addEventListener('click', (event) => {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        });
    });

    // --- LÓGICA DO KANBAN ---
    const kanbanBoard = document.getElementById('kanban-board');

    if (kanbanBoard) {
        kanbanBoard.addEventListener('click', async (event) => {
            const card = event.target.closest('.kanban-card');
            if (!card) return;

            const taskId = card.dataset.taskId;

            // CORREÇÃO AQUI: Removido o prefixo '/app' que causava o erro
            // Antes: fetch(`/app/api/servicos/detalhes/${taskId}/`)
            // Agora:
            const response = await fetch(`/api/servicos/detalhes/${taskId}/`);

            if (response.ok) {
                const data = await response.json();
                populateAndShowModal(data);
            } else {
                console.error("Erro ao buscar detalhes da tarefa. Verifique se a URL está correta.");
            }
        });
    }

    function populateAndShowModal(data) {
        const modal = modalVisualizacao;
        if (!modal) return;

        // Garante que o modo de edição esteja desativado ao abrir
        toggleEditMode(false);

        // 1. Preenche o Título
        const tituloEl = modal.querySelector('.modal-title');
        if (tituloEl) tituloEl.textContent = data.titulo;

        // 2. Preenche a Descrição
        // Certifique-se que no HTML você colocou id="modal-descricao-conteudo"
        const descricaoEl = document.getElementById('modal-descricao-conteudo');
        if (descricaoEl) {
            descricaoEl.innerHTML = data.descricao;
        }

        // 3. Constrói o histórico
        let historyHtml = `<p><strong>Criado por:</strong> ${data.criado_por} em ${data.data_criacao}</p>`;
        if (data.status !== 'PENDENTE') {
            historyHtml += `<p><strong>Tratativa Iniciada por:</strong> ${data.iniciado_por} em ${data.data_inicio_tratativa}</p>`;
        }

        if (data.historico_acoes && data.historico_acoes.length > 0) {
            historyHtml += '<p><strong>Ações Registradas:</strong></p>';
            let acoesHtml = '<ul style="list-style-type: disc; padding-left: 20px;">';
            data.historico_acoes.forEach(acao => {
                acoesHtml += `<li style="margin-bottom: 0.5rem;">"${acao.texto}"<br><small><em> - por ${acao.usuario} em ${acao.data}</em></small></li>`;
            });
            acoesHtml += '</ul>';
            historyHtml += acoesHtml;
        }

        if (data.status === 'FINALIZADO') {
            historyHtml += `<p><strong>Finalizado por:</strong> ${data.finalizado_por} em ${data.data_finalizacao}</p>`;
        }

        const historyContainer = modal.querySelector('.modal-body-history');
        if (historyContainer) historyContainer.innerHTML = historyHtml;

        // 4. Reset dos painéis
        modal.querySelectorAll('.action-panel').forEach(panel => panel.style.display = 'none');

        // 5. Exibe painéis conforme status
        if (data.status === 'PENDENTE') {
            const panelPendente = modal.querySelector('#action-panel-pendente');
            if (panelPendente) panelPendente.style.display = 'block';

            const btnIniciar = modal.querySelector('#btn-iniciar-tratativa');
            if (btnIniciar) btnIniciar.dataset.taskId = data.id;

        } else if (data.status === 'INICIADO') {
            const panelIniciado = modal.querySelector('#action-panel-iniciado');
            const panelFooter = modal.querySelector('#action-panel-iniciado-footer');

            if (panelIniciado) {
                panelIniciado.style.display = 'block';
                const inputAcao = modal.querySelector('#form_acao_tomada');
                if (inputAcao) inputAcao.value = '';
                // Inicializa CKEditor ação
                initActionCKEditor();
            }

            if (panelFooter) {
                panelFooter.style.display = 'flex';

                const btnGravar = modal.querySelector('#btn-gravar-acao');
                if (btnGravar) btnGravar.dataset.taskId = data.id;

                const btnFinalizar = modal.querySelector('#btn-finalizar');
                if (btnFinalizar) btnFinalizar.dataset.taskId = data.id;
            }
        }

        // Atribui ID para editar/salvar (independente do status)
        const btnEditar = modal.querySelector('#btn-editar-servico');
        if (btnEditar) {
            btnEditar.dataset.taskId = data.id;
            // Oculta botão de editar se estiver finalizado
            if (data.status === 'FINALIZADO') {
                btnEditar.style.display = 'none';
            } else {
                btnEditar.style.display = 'block'; // Garante que apareça para outros status
            }
        }

        const btnSalvarEdicao = modal.querySelector('#btn-salvar-edicao');
        if (btnSalvarEdicao) btnSalvarEdicao.dataset.taskId = data.id;

        modal.style.display = 'flex';
    }

    // Ações dos botões
    if (modalVisualizacao) {
        modalVisualizacao.addEventListener('click', async (event) => {
            const target = event.target;
            // Tenta pegar o ID do dataset do alvo ou do parent (caso clique num icone dentro do botao)
            let taskId = target.dataset.taskId;
            if (!taskId && target.closest('[data-task-id]')) {
                taskId = target.closest('[data-task-id]').dataset.taskId;
            }

            // Permite continuar se for botão cancelar (que não precisa de ID) ou se achou ID
            // Mas cuidado: btn-editar e btn-salvar PRECISAM do ID.
            // O check global `if (!taskId) return` era agressivo demais para botões que não tinham ID setado ainda ou não precisavam.
            // Vamos remover o return global e checar localmente por ação.

            // URLS CORRIGIDAS AQUI TAMBÉM (sem /app)
            if (target.id === 'btn-iniciar-tratativa') {
                await postAction(`/api/servicos/iniciar/${taskId}/`);
            }
            if (target.id === 'btn-gravar-acao') {
                const acaoInput = document.getElementById('form_acao_tomada');
                let acao = acaoInput ? acaoInput.value : '';

                // Verifica se temos CKEditor para este campo
                if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances['form_acao_tomada']) {
                    acao = CKEDITOR.instances['form_acao_tomada'].getData();
                }

                if (!acao.trim()) {
                    alert("Por favor, descreva a ação tomada.");
                    return;
                }

                await postAction(`/api/servicos/atualizar-acao/${taskId}/`, { acao: acao });
            }
            if (target.id === 'btn-finalizar') {
                if (confirm("Tem certeza que deseja finalizar esta tarefa?")) {
                    await postAction(`/api/servicos/finalizar/${taskId}/`);
                }
            }

            // --- Lógica de Edição ---
            if (target.id === 'btn-editar-servico' || target.closest('#btn-editar-servico')) {
                console.log("Botão editar clicado");
                toggleEditMode(true);
            }
            if (target.id === 'btn-cancelar-edicao') {
                toggleEditMode(false);
            }
            if (target.id === 'btn-salvar-edicao') {
                const titulo = document.getElementById('edit-titulo').value;
                let descricao = document.getElementById('edit-descricao').value;

                // Se o CKEditor estiver ativo, pega o valor dele
                if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances['edit-descricao']) {
                    descricao = CKEDITOR.instances['edit-descricao'].getData();
                }

                await postAction(`/api/servicos/editar/${taskId}/`, {
                    titulo: titulo,
                    descricao: descricao
                });
            }
        });
    }

    function toggleEditMode(enable) {
        const viewContainer = document.getElementById('view-mode-container');
        const editContainer = document.getElementById('edit-mode-container');
        const btnEditar = document.getElementById('btn-editar-servico');

        if (enable) {
            // Preenche os campos de edição com os valores atuais
            document.getElementById('edit-titulo').value = document.getElementById('modal-titulo-tarefa').textContent;

            const currentDesc = document.getElementById('modal-descricao-conteudo').innerHTML;
            document.getElementById('edit-descricao').value = currentDesc;

            // Inicializa ou atualiza o CKEditor
            if (typeof CKEDITOR !== 'undefined') {
                if (CKEDITOR.instances['edit-descricao']) {
                    CKEDITOR.instances['edit-descricao'].setData(currentDesc);
                } else {
                    CKEDITOR.replace('edit-descricao', {
                        toolbar: [
                            { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                            { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'] },
                            { name: 'insert', items: ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar'] },
                            { name: 'links', items: ['Link', 'Unlink', 'Anchor'] },
                            { name: 'styles', items: ['Format', 'Font', 'FontSize'] },
                            { name: 'colors', items: ['TextColor', 'BGColor'] },
                            { name: 'tools', items: ['Maximize'] }
                        ],
                        height: 200, // Aumentei um pouco a altura para acomodar conteúdo rico como imagens
                        removePlugins: 'elementspath',
                        resize_enabled: false,
                        // Permite conteúdo extra para evitar que o CKEditor remova tags
                        extraAllowedContent: 'img[alt,border,width,height,align,vspace,hspace,!src];'
                    });
                }
            }

            viewContainer.style.display = 'none';
            editContainer.style.display = 'block';
            if (btnEditar) btnEditar.style.display = 'none';
        } else {
            viewContainer.style.display = 'block';
            editContainer.style.display = 'none';
            if (btnEditar) btnEditar.style.display = 'block';
        }
    }

    const loadMoreBtn = document.getElementById('load-more-btn-gr');
    const finalizadasList = document.getElementById('finalizadas-list-gr');
    let currentPage = 1;

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', async () => {
            currentPage++;
            const response = await fetch(`/api/servicos/finalizadas/?page=${currentPage}`);
            if (response.ok) {
                const data = await response.json();
                finalizadasList.insertAdjacentHTML('beforeend', data.html);
                if (!data.has_next) {
                    loadMoreBtn.style.display = 'none';
                }
            }
        });
    }

    async function postAction(url, body = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(body)
            });
            if (response.ok) {
                location.reload();
            } else {
                const errorData = await response.json();
                alert(errorData.message || 'Ocorreu um erro.');
            }
        } catch (error) {
            console.error("Erro:", error);
            alert("Erro de conexão.");
        }
    }

    // Inicializa CKEditor para o campo de Ação
    function initActionCKEditor() {
        if (typeof CKEDITOR !== 'undefined' && document.getElementById('form_acao_tomada')) {
            const ckActionConfig = {
                toolbar: [
                    { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                    { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'] },
                    { name: 'insert', items: ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar'] },
                    { name: 'links', items: ['Link', 'Unlink', 'Anchor'] },
                    { name: 'styles', items: ['Format', 'Font', 'FontSize'] },
                    { name: 'colors', items: ['TextColor', 'BGColor'] },
                    { name: 'tools', items: ['Maximize'] }
                ],
                height: 150,
                removePlugins: 'elementspath',
                resize_enabled: false,
                extraAllowedContent: 'img[alt,border,width,height,align,vspace,hspace,!src];'
            };

            if (!CKEDITOR.instances['form_acao_tomada']) {
                CKEDITOR.replace('form_acao_tomada', ckActionConfig);
            } else {
                CKEDITOR.instances['form_acao_tomada'].setData('');
            }
        }
    }
});