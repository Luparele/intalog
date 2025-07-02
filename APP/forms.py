from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Funcionario, Cliente, RegraDeEmbarque, Seguro, Mensagem, Averbacao, GerenciadoraRisco

# Formulário de Funcionário
class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'data_expedicao': forms.DateInput(attrs={'type': 'date'}),
            'telefone_pessoal': forms.TextInput(attrs={'value': '+5521'}),
            'telefone_corporativo': forms.TextInput(attrs={'value': '+5521'}),
        }

# Formulário de Cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'vigencia_pgr': forms.DateInput(attrs={'type': 'date'}),
        }

# FormSet para Regras de Embarque
RegraDeEmbarqueFormSet = inlineformset_factory(
    Cliente,
    RegraDeEmbarque,
    fields='__all__',
    extra=1,
    can_delete=True,
    widgets={
        'valor_min': forms.NumberInput(attrs={'placeholder': 'Ex: 10000.00'}),
        'valor_max': forms.NumberInput(attrs={'placeholder': 'Ex: 50000.00'}),
    }
)

# Formulário de Seguro (VERSÃO CORRIGIDA)
class SeguroForm(forms.ModelForm):
    class Meta:
        model = Seguro
        # Trocamos 'fields' por 'exclude' para remover o campo 'cliente' do formulário
        exclude = ['cliente']
        widgets = {
            'vigencia': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulário de Mensagem
class MensagemForm(forms.Form):
    TIPO_DESTINATARIO_CHOICES = [
        ('GERAL', 'Todos os Usuários (Geral)'),
        ('DIRECT', 'Usuário Específico (Direct)'),
    ]
    tipo_destinatario = forms.ChoiceField(choices=TIPO_DESTINATARIO_CHOICES)
    destinatario_usuario = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False, 
        label="Destinatário"
    )
    conteudo = forms.CharField(widget=forms.Textarea, label="Mensagem")
    is_atencao = forms.BooleanField(required=False, label="Marcar como 'Atenção'")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['destinatario_usuario'].queryset = User.objects.exclude(pk=user.pk)


# Formulários de Autenticação
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de Usuário', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'}))

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Senha Antiga", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha atual', 'autofocus': True}))
    new_password1 = forms.CharField(label="Nova Senha", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite a nova senha'}))
    new_password2 = forms.CharField(label="Confirmação da Nova Senha", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme a nova senha'}))

# Formulário de Averbacao
class AverbacaoForm(forms.ModelForm):
    class Meta:
        model = Averbacao
        fields = '__all__'

# Formulário de Gerenciadora de Risco
class GerenciadoraRiscoForm(forms.ModelForm):
    class Meta:
        model = GerenciadoraRisco
        fields = '__all__'
        # Adicionamos widgets para customizar os campos
        widgets = {
            'validade_condutor_clt': forms.NumberInput(attrs={'placeholder': 'em meses'}),
            'validade_condutor_agregado': forms.NumberInput(attrs={'placeholder': 'em meses'}),
            
            'validade_veiculo_frota': forms.NumberInput(attrs={'placeholder': 'em meses'}),
            'validade_veiculo_agregado': forms.NumberInput(attrs={'placeholder': 'em meses'}),

            'validade_checklist_frota': forms.NumberInput(attrs={'placeholder': 'em dias'}),
            'validade_checklist_agregado': forms.NumberInput(attrs={'placeholder': 'em dias'}),
        }

# FORMULÁRIO DE CRIAÇÃO DE USUÁRIO
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text='Obrigatório. Um endereço de e-mail válido.'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # Adiciona o email aos campos do formulário