from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User, Group
from .models import (
    Funcionario, Cliente, RegraDeEmbarque, Seguro, Mensagem, Averbacao, 
    GerenciadoraRisco, Sinistro, Rotograma, ChecklistVeiculo, ChecklistGR, 
    Checklist, TreinamentoQSMS, CertificadoQSMS, EventoQSMS, ContratoDiverso,
    ServicoPendente, ServicoPendenteQSMS, VeiculoAssegurado, BlackList
)
from django.core.exceptions import ValidationError

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

# Formulário de Seguro
class SeguroForm(forms.ModelForm):
    class Meta:
        model = Seguro
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
        widgets = {
            'validade_condutor_clt': forms.NumberInput(attrs={'placeholder': 'em meses'}),
            'validade_condutor_agregado': forms.NumberInput(attrs={'placeholder': 'em meses'}),
            'validade_veiculo_frota': forms.NumberInput(attrs={'placeholder': 'em meses'}),
            'validade_veiculo_agregado': forms.NumberInput(attrs={'placeholder': 'em meses'}),
            'validade_checklist_frota': forms.NumberInput(attrs={'placeholder': 'em dias'}),
            'validade_checklist_agregado': forms.NumberInput(attrs={'placeholder': 'em dias'}),
        }

# FORMULÁRIO DE CRIAÇÃO DE USUÁRIO - VERSÃO ATUALIZADA COM GRUPOS
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text='Obrigatório. Um endereço de e-mail válido.'
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Grupos de Permissão",
        help_text="Selecione os grupos aos quais este usuário pertencerá. Ele herdará todas as permissões dos grupos selecionados."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['groups'])
        return user

class SinistroForm(forms.ModelForm):
    class Meta:
        model = Sinistro
        fields = '__all__'
        widgets = {
            'data_hora_sinistro': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class EditarSinistroForm(forms.ModelForm):
    class Meta:
        model = Sinistro
        fields = '__all__'
        widgets = {
            'data_hora_sinistro': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_hora_sinistro'].disabled = True
        self.fields['veiculo_assegurado'].disabled = True
        self.fields['seguradora'].disabled = True

class RotogramaForm(forms.ModelForm):
    class Meta:
        model = Rotograma
        fields = '__all__'

class VeiculoChecklistForm(forms.ModelForm):
    class Meta:
        model = ChecklistVeiculo
        fields = '__all__'

class GRChecklistForm(forms.ModelForm):
    class Meta:
        model = ChecklistGR
        fields = '__all__'

class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        # Adicione o novo campo à lista de fields
        fields = ['veiculo', 'gr', 'aprovado', 'data_aprovacao', 'data_validade_manual', 'motivo_reprovacao']
        widgets = {
            'data_aprovacao': forms.DateInput(attrs={'type': 'date'}),
            'data_validade_manual': forms.DateInput(attrs={'type': 'date'}),
        }

    # Adicione este método de validação
    def clean(self):
        cleaned_data = super().clean()
        aprovado = cleaned_data.get("aprovado")
        data_aprovacao = cleaned_data.get("data_aprovacao")
        data_validade_manual = cleaned_data.get("data_validade_manual")

        if aprovado:
            if data_aprovacao and data_validade_manual:
                raise ValidationError("Preencha apenas um dos campos de data: 'Data de Aprovação' OU 'Data de Validade'.")
            if not data_aprovacao and not data_validade_manual:
                raise ValidationError("Se aprovado, um dos campos de data ('Aprovação' ou 'Validade') deve ser preenchido.")
        
        return cleaned_data

class TreinamentoQSMSForm(forms.ModelForm):
    class Meta:
        model = TreinamentoQSMS
        fields = ['assunto', 'data_evento', 'hora_evento', 'detalhes', 'concluido']
        widgets = {
            'data_evento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora_evento': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }

class CertificadoQSMSForm(forms.ModelForm):
    class Meta:
        model = CertificadoQSMS
        fields = [
            'nome_certificado', 
            'orgao_competente', 
            'link_orgao', 
            'data_validade', 
            'anexo',
            'descricao'
        ]
        widgets = {
            'data_validade': forms.DateInput(attrs={'type': 'date'}),
            # Adiciona um placeholder como exemplo dentro do campo de link
            'link_orgao': forms.URLInput(attrs={'placeholder': 'https://www.gov.br/exemplo'}),
        }
        # Adiciona um texto de ajuda abaixo do campo de link
        help_texts = {
            'link_orgao': 'O link deve começar com http:// ou https://',
        }

class EventoQSMSForm(forms.ModelForm):
    class Meta:
        model = EventoQSMS
        fields = ['titulo', 'data_evento', 'hora_evento', 'descricao', 'concluido']
        widgets = {
            'data_evento': forms.DateInput(attrs={'type': 'date'}),
            'hora_evento': forms.TimeInput(attrs={'type': 'time'}),
        }

class ContratoDiversoForm(forms.ModelForm):
    class Meta:
        model = ContratoDiverso
        fields = '__all__'
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }

class ServicoPendenteForm(forms.ModelForm):
    class Meta:
        model = ServicoPendente
        fields = ['titulo', 'descricao']

class AcaoServicoPendenteForm(forms.Form):
    acao = forms.CharField(widget=forms.Textarea, label="Ação a ser Tomada")

class ServicoPendenteQSMSForm(forms.ModelForm):
    class Meta:
        model = ServicoPendenteQSMS
        fields = ['titulo', 'descricao']

class AcaoServicoPendenteQSMSForm(forms.Form):
    acao = forms.CharField(widget=forms.Textarea, label="Ação a ser Tomada")

class VeiculoAsseguradoForm(forms.ModelForm):
    class Meta:
        model = VeiculoAssegurado
        fields = '__all__'
        widgets = {
            'vigencia': forms.DateInput(attrs={'type': 'date'}),
            'valor_fipe': forms.NumberInput(attrs={'placeholder': 'Ex: 100'}),
            'franquia': forms.NumberInput(attrs={'placeholder': 'Ex: 2500.00'}),
            'danos_materiais': forms.NumberInput(attrs={'placeholder': 'Ex: 100000.00'}),
            'danos_corporais': forms.NumberInput(attrs={'placeholder': 'Ex: 100000.00'}),
            'danos_morais': forms.NumberInput(attrs={'placeholder': 'Ex: 50000.00'}),
            'app_morte': forms.NumberInput(attrs={'placeholder': 'Ex: 50000.00'}),
            'app_invalidez': forms.NumberInput(attrs={'placeholder': 'Ex: 50000.00'}),
        }

class BlackListForm(forms.ModelForm):
    class Meta:
        model = BlackList
        fields = ['nome_completo', 'cpf', 'motivo_bloqueio']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'placeholder': 'Nome Completo'}),
            'cpf': forms.TextInput(attrs={'class': 'cpf-mask', 'placeholder': '000.000.000-00'}),
            'motivo_bloqueio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Motivo do bloqueio...'}),
        }