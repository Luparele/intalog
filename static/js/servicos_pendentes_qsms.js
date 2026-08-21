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

    // --- MANIPULAÇÃO DE MODAIS (QSMS) ---
    const modalCriacao = document.getElementById('modal-criacao-qsms');
    const modalVisualizacao = document.getElementById('modal-visualizacao-qsms');

    // Modal de Criação
    if (document.getElementById('abrir-modal-criacao-qsms')) {
        document.getElementById('abrir-modal-criacao-qsms').addEventListener('click', () => {
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

    // --- LÓGICA DO KANBAN QSMS ---
    const kanbanBoard = document.getElementById('kanban-board-qsms');
    
    if (kanbanBoard) {
        kanbanBoard.addEventListener('click', async (event) => {
            const card = event.target.closest('.kanban-card');
            if (!card) return; 
    
            const taskId = card.dataset.taskId;
    
            // URL da API QSMS (Verificada no urls.py: api/qsm/servicos/detalhes/<int:pk>/)
            const response = await fetch(`/api/qsm/servicos/detalhes/${taskId}/`);
            
            if (response.ok) {
                const data = await response.json();
                populateAndShowModal(data);
            } else {
                console.error("Erro ao buscar detalhes da tarefa QSMS.");
            }
        });
    }

    function populateAndShowModal(data) {
        const modal = modalVisualizacao;
        if (!modal) return;
        
        // 1. Preenche o Título
        const tituloEl = modal.querySelector('.modal-title');
        if (tituloEl) tituloEl.textContent = data.titulo;

        // 2. Preenche a Descrição (ADAPTAÇÃO FEITA AQUI)
        // Busca pelo ID específico do QSMS que colocamos no HTML
        const descricaoEl = document.getElementById('modal-descricao-conteudo-qsms');
        if (descricaoEl) {
            descricaoEl.textContent = data.descricao; 
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

        // 5. Exibe painéis conforme status (IDs com sufixo -qsms)
        if (data.status === 'PENDENTE') {
            const panelPendente = modal.querySelector('#action-panel-pendente-qsms');
            if (panelPendente) panelPendente.style.display = 'block';
            
            const btnIniciar = modal.querySelector('#btn-iniciar-tratativa-qsms');
            if (btnIniciar) btnIniciar.dataset.taskId = data.id;

        } else if (data.status === 'INICIADO') {
            const panelIniciado = modal.querySelector('#action-panel-iniciado-qsms');
            const panelFooter = modal.querySelector('#action-panel-iniciado-footer-qsms');
            
            if (panelIniciado) {
                panelIniciado.style.display = 'block';
                const inputAcao = modal.querySelector('#form_acao_tomada_qsms');
                if (inputAcao) inputAcao.value = ''; 
            }
            
            if (panelFooter) {
                panelFooter.style.display = 'flex';
                
                const btnGravar = modal.querySelector('#btn-gravar-acao-qsms');
                if (btnGravar) btnGravar.dataset.taskId = data.id;
                
                const btnFinalizar = modal.querySelector('#btn-finalizar-qsms');
                if (btnFinalizar) btnFinalizar.dataset.taskId = data.id;
            }
        }

        modal.style.display = 'flex';
    }

    // Ações dos botões (QSMS)
    if (modalVisualizacao) {
        modalVisualizacao.addEventListener('click', async (event) => {
            const target = event.target;
            const taskId = target.dataset.taskId;
            
            if (!taskId) return;
    
            // URLs com prefixo /api/qsm/ conforme padrão QSMS
            if (target.id === 'btn-iniciar-tratativa-qsms') {
                await postAction(`/api/qsm/servicos/iniciar/${taskId}/`);
            }
            if (target.id === 'btn-gravar-acao-qsms') {
                const acaoInput = document.getElementById('form_acao_tomada_qsms');
                const acao = acaoInput ? acaoInput.value : '';
                
                if (!acao.trim()) {
                    alert("Por favor, descreva a ação tomada.");
                    return;
                }
                
                await postAction(`/api/qsm/servicos/atualizar-acao/${taskId}/`, { acao: acao });
            }
            if (target.id === 'btn-finalizar-qsms') {
                if(confirm("Tem certeza que deseja finalizar esta tarefa QSMS?")) {
                    await postAction(`/api/qsm/servicos/finalizar/${taskId}/`);
                }
            }
        });
    }

    const loadMoreBtn = document.getElementById('load-more-btn-qsms');
    const finalizadasList = document.getElementById('finalizadas-list-qsms');
    let currentPage = 1;

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', async () => {
            currentPage++;
            
            const response = await fetch(`/api/qsm/servicos/finalizadas/?page=${currentPage}`);
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
});