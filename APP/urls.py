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

    # ROTA QUE ESTAVA FALTANDO:
    path('downloads/', views.pagina_downloads, name='pagina_downloads'),

    path('mensagens/enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    path('mensagens/marcar-lida/<int:pk>/', views.marcar_como_lida, name='marcar_como_lida'),
    path('usuarios/cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
]