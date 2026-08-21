from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm, CustomPasswordChangeForm

app_name = 'APP'

urlpatterns = [
    # --- Rotas de Autenticação ---
    path('', auth_views.LoginView.as_view(
        template_name='login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('alterar-senha/', auth_views.PasswordChangeView.as_view(
        template_name='alterar_senha.html',
        form_class=CustomPasswordChangeForm,
        success_url='/dashboard/'
    ), name='alterar_senha'),

    # --- Rotas de Redefinição de Senha ---
    path('reset_password/',
         auth_views.PasswordResetView.as_view(
             template_name="password_reset/password_reset_form.html",
             success_url=reverse_lazy('APP:password_reset_done')
         ),
         name="password_reset"),
    
    path('reset_password/sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="password_reset/password_reset_done.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="password_reset/password_reset_confirm.html",
             success_url=reverse_lazy('APP:password_reset_complete')
         ),
         name="password_reset_confirm"),
    
    path('reset_password/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="password_reset/password_reset_complete.html"),
         name="password_reset_complete"),

    # --- Rotas do Aplicativo ---
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('funcionarios/cadastrar/', views.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('funcionarios/listar/', views.listar_funcionarios, name='consultar_funcionarios'),
    path('funcionarios/editar/<int:pk>/', views.editar_funcionario, name='editar_funcionario'),
    path('funcionarios/excluir/<int:pk>/', views.excluir_funcionario, name='excluir_funcionario'),
    
    path('clientes/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('clientes/listar/', views.listar_clientes, name='consultar_clientes'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/excluir/<int:pk>/', views.excluir_cliente, name='excluir_cliente'),

    path('agenda/', views.agenda_contatos, name='agenda_contatos'),
    path('politica-de-privacidade/', views.politica_de_privacidade, name='politica_de_privacidade'),
    path('seguros/', views.gestao_seguros, name='gestao_seguros'),
    path('averbacoes/', views.gestao_averbacoes, name='gestao_averbacoes'),
    path('gerenciadoras/', views.gestao_gerenciadoras, name='gestao_gerenciadoras'),
    
    # Black-List
    path('gerenciamento/black-list/', views.blacklist_view, name='blacklist'),
    path('gerenciamento/black-list/novo/', views.add_blacklist, name='add_blacklist'),
    path('gerenciamento/black-list/editar/<int:pk>/', views.edit_blacklist, name='edit_blacklist'),
    path('gerenciamento/black-list/excluir/<int:pk>/', views.delete_blacklist, name='delete_blacklist'),

    # ROTA QUE ESTAVA FALTANDO:
    path('downloads/', views.pagina_downloads, name='pagina_downloads'),

    path('mensagens/enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    path('mensagens/marcar-lida/<int:pk>/', views.marcar_como_lida, name='marcar_como_lida'),
    path('usuarios/cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('sinistros/', views.gestao_sinistros, name='gestao_sinistros'),
    path('sinistros/editar/<int:pk>/', views.editar_sinistro, name='editar_sinistro'),
    path('rotogramas/', views.gestao_rotogramas, name='gestao_rotogramas'),
    path('rotogramas/editar/<int:pk>/', views.editar_rotograma, name='editar_rotograma'),
    path('checklist/', views.pagina_checklist, name='pagina_checklist'),
    path('agenda-treinamentos/', views.agenda_treinamentos, name='agenda_treinamentos'),
    path('api/treinamentos/', views.treinamentos_json, name='treinamentos_json'),
    path('treinamentos/editar/<int:pk>/', views.editar_treinamento, name='editar_treinamento'),
    path('certificados-qsm/', views.gestao_certificados, name='gestao_certificados'),
    path('certificados-qsm/editar/<int:pk>/', views.editar_certificado, name='editar_certificado'),
    path('calendario-eventos/', views.calendario_eventos, name='calendario_eventos'),
    path('eventos/editar/<int:pk>/', views.editar_evento, name='editar_evento'),
    path('api/eventos/', views.eventos_json, name='eventos_json'),
    path('contratos-diversos/', views.gestao_contratos, name='gestao_contratos'),
    path('servicos-pendentes/', views.servicos_pendentes, name='servicos_pendentes'),
    path('api/servicos/detalhes/<int:pk>/', views.detalhes_servico_json, name='detalhes_servico_json'),
    path('api/servicos/iniciar/<int:pk>/', views.iniciar_servico, name='iniciar_servico'),
    path('api/servicos/atualizar-acao/<int:pk>/', views.atualizar_acao_servico, name='atualizar_acao_servico'),
    path('api/servicos/finalizar/<int:pk>/', views.finalizar_servico, name='finalizar_servico'),
    path('api/servicos/finalizadas/', views.carregar_mais_finalizadas_gr, name='carregar_mais_finalizadas_gr'),
    path('qsm/servicos-pendentes/', views.servicos_pendentes_qsms, name='servicos_pendentes_qsms'),
    path('api/qsm/servicos/detalhes/<int:pk>/', views.detalhes_servico_qsms_json, name='detalhes_servico_qsms_json'),
    path('api/qsm/servicos/iniciar/<int:pk>/', views.iniciar_servico_qsms, name='iniciar_servico_qsms'),
    path('api/qsm/servicos/atualizar-acao/<int:pk>/', views.atualizar_acao_servico_qsms, name='atualizar_acao_servico_qsms'),
    path('api/qsm/servicos/finalizar/<int:pk>/', views.finalizar_servico_qsms, name='finalizar_servico_qsms'),
    path('api/qsm/servicos/finalizadas/', views.carregar_mais_finalizadas_qsms, name='carregar_mais_finalizadas_qsms'),
    path('veiculos-assegurados/', views.gestao_veiculos_assegurados, name='gestao_veiculos_assegurados'),
    path('veiculos-assegurados/editar/<int:pk>/', views.editar_veiculo_assegurado, name='editar_veiculo_assegurado'),
    path('api/servicos/editar/<int:pk>/', views.api_editar_servico, name='api_editar_servico'),
]