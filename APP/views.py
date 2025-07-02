from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDay
from datetime import date, timedelta
import holidays
import json

# Importa todos os formulários e modelos necessários
from .forms import (
    FuncionarioForm, ClienteForm, RegraDeEmbarqueFormSet, 
    SeguroForm, MensagemForm, CustomAuthenticationForm, CustomPasswordChangeForm,
    AverbacaoForm, GerenciadoraRiscoForm, CustomUserCreationForm # <- Importação adicionada
)
from .models import (
    Funcionario, Cliente, RegraDeEmbarque, Seguro, 
    Mensagem, Averbacao, GerenciadoraRisco
)


def is_superuser(user):
    return user.is_superuser

@login_required
def dashboard(request):
    # --- Lógica para os Cards de Contagem ---
    total_clientes = Cliente.objects.count()
    total_gerenciadoras = GerenciadoraRisco.objects.count()
    total_seguros = Seguro.objects.count()
    total_averbacoes = Averbacao.objects.count()
    downloads_pgr = Cliente.objects.exclude(pgr_arquivo='').count()
    downloads_ddr = Cliente.objects.exclude(ddr_arquivo='').count()
    downloads_apolices = Seguro.objects.exclude(apolice_anexo='').count()
    total_downloads = downloads_pgr + downloads_ddr + downloads_apolices

    # --- Lógica das Mensagens ---
    mensagens_gerais = Mensagem.objects.filter(destinatario__isnull=True).order_by('-data_envio')[:5]
    mensagens_pessoais = Mensagem.objects.filter(destinatario=request.user).order_by('-data_envio')[:5]

    # --- Lógica para o Gráfico de Crescimento (Linhas) ---
    hoje = date.today()
    sete_dias_atras = hoje - timedelta(days=6)
    datas = [(sete_dias_atras + timedelta(days=i)) for i in range(7)]
    cadastros_por_dia = {dia.strftime("%d/%m"): 0 for dia in datas}
    modelos_para_contar = [Cliente, Funcionario, Seguro, Averbacao, GerenciadoraRisco]
    for modelo in modelos_para_contar:
        q = modelo.objects.filter(data_cadastro__date__gte=sete_dias_atras).annotate(dia=TruncDay('data_cadastro')).values('dia').annotate(total=Count('id')).order_by('dia')
        for item in q:
            dia_str = item['dia'].strftime("%d/%m")
            if dia_str in cadastros_por_dia:
                cadastros_por_dia[dia_str] += item['total']
    growth_chart_labels = list(cadastros_por_dia.keys())
    growth_chart_data = list(cadastros_por_dia.values())
    
    # --- Lógica para o Gráfico de Averbações (Barras) ---
    ddr_count = Averbacao.objects.filter(tipo_seguro='DDR').count()
    intalog_count = Averbacao.objects.filter(tipo_seguro='INTALOG').count()
    bar_chart_labels = ['DDR/Carta Conforto', 'Averbado Intalog']
    bar_chart_data = [ddr_count, intalog_count]
    
    # --- Lógica para o Gráfico de Downloads (Pizza) ---
    downloads_chart_labels = ['Arquivos PGR', 'Arquivos DDR', 'Apólices de Seguro']
    downloads_chart_data = [downloads_pgr, downloads_ddr, downloads_apolices]

    context = {
        'total_clientes': total_clientes, 'total_gerenciadoras': total_gerenciadoras,
        'total_seguros': total_seguros, 'total_averbacoes': total_averbacoes,
        'total_downloads': total_downloads,
        'mensagens_gerais': mensagens_gerais,
        'mensagens_pessoais': mensagens_pessoais,
        'growth_chart_labels': json.dumps(growth_chart_labels),
        'growth_chart_data': json.dumps(growth_chart_data),
        'bar_chart_labels': json.dumps(bar_chart_labels),
        'bar_chart_data': json.dumps(bar_chart_data),
        'downloads_chart_labels': json.dumps(downloads_chart_labels),
        'downloads_chart_data': json.dumps(downloads_chart_data),
    }
    return render(request, 'dashboard.html', context)

@login_required
def enviar_mensagem(request):
    initial_data = {}
    reply_to_user_id = request.GET.get('responder_para')
    if reply_to_user_id:
        try:
            reply_user = User.objects.get(pk=reply_to_user_id)
            initial_data = {
                'tipo_destinatario': 'DIRECT',
                'destinatario_usuario': reply_user
            }
        except User.DoesNotExist:
            pass

    if request.method == 'POST':
        form = MensagemForm(request.POST, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            destinatario = None
            if cd['tipo_destinatario'] == 'DIRECT':
                destinatario = cd['destinatario_usuario']
            
            Mensagem.objects.create(
                remetente=request.user,
                destinatario=destinatario,
                conteudo=cd['conteudo'],
                is_atencao=cd['is_atencao']
            )
            messages.success(request, 'Mensagem enviada com sucesso!')
            return redirect('APP:enviar_mensagem')
    else:
        form = MensagemForm(user=request.user, initial=initial_data)
        
    return render(request, 'enviar_mensagem.html', {'form': form})

# NOVA VIEW PARA MARCAR MENSAGEM COMO LIDA
@login_required
def marcar_como_lida(request, pk):
    # Apenas requisições POST são permitidas para segurança
    if request.method == 'POST':
        try:
            # Garante que a mensagem pertence ao usuário logado e não foi lida
            mensagem = Mensagem.objects.get(pk=pk, destinatario=request.user, lida=False)
            mensagem.lida = True
            mensagem.save()
            return JsonResponse({'status': 'success', 'message': 'Mensagem marcada como lida.'})
        except Mensagem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mensagem não encontrada ou já lida.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


@login_required
def cadastrar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('APP:cadastrar_funcionario')
    else:
        form = FuncionarioForm()
    return render(request, 'cadastro_funcionario.html', {'form': form})

@login_required
def listar_funcionarios(request):
    query = request.GET.get('q')
    if query:
        funcionarios = Funcionario.objects.filter(nome__icontains=query).order_by('nome')
    else:
        funcionarios = Funcionario.objects.all().order_by('nome')
    context = {
        'funcionarios': funcionarios,
        'query': query,
    }
    return render(request, 'listar_funcionarios.html', context)

@login_required
def editar_funcionario(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES, instance=funcionario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro de funcionário atualizado com sucesso!')
            return redirect('APP:consultar_funcionarios')
    else:
        form = FuncionarioForm(instance=funcionario)
    return render(request, 'editar_funcionario.html', {'form': form})

@login_required
def excluir_funcionario(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        nome_funcionario = funcionario.nome
        funcionario.delete()
        messages.success(request, f'Cadastro de "{nome_funcionario}" excluído com sucesso.')
        return redirect('APP:listar_funcionarios')
    return render(request, 'excluir_funcionario.html', {'funcionario': funcionario})

@login_required
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        formset = RegraDeEmbarqueFormSet(request.POST, prefix='regras')
        if form.is_valid() and formset.is_valid():
            cliente = form.save()
            formset.instance = cliente
            formset.save()
            messages.success(request, f'Cliente "{cliente.cliente}" cadastrado com sucesso!')
            return redirect('APP:cadastrar_cliente')
    else:
        form = ClienteForm()
        formset = RegraDeEmbarqueFormSet(prefix='regras')
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'cadastrar_cliente.html', context)

@login_required
def listar_clientes(request):
    query = request.GET.get('q')
    if query:
        clientes = Cliente.objects.filter(cliente__icontains=query).order_by('cliente')
    else:
        clientes = Cliente.objects.all().order_by('cliente')
    context = {
        'clientes': clientes,
        'query': query,
    }
    return render(request, 'listar_clientes.html', context)

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        formset = RegraDeEmbarqueFormSet(request.POST, instance=cliente, prefix='regras')
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Cadastro do cliente "{cliente.cliente}" atualizado com sucesso!')
            # CORREÇÃO APLICADA AQUI
            return redirect('APP:consultar_clientes') 
    else:
        form = ClienteForm(instance=cliente)
        formset = RegraDeEmbarqueFormSet(instance=cliente, prefix='regras')

    context = {
        'form': form,
        'formset': formset,
        'cliente': cliente,
    }
    return render(request, 'editar_cliente.html', context)

@login_required
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        nome_cliente = cliente.cliente
        cliente.delete()
        messages.success(request, f'Cliente "{nome_cliente}" e todas as suas regras foram excluídos com sucesso.')
        # CORREÇÃO APLICADA AQUI
        return redirect('APP:consultar_clientes')
    
    return render(request, 'excluir_cliente.html', {'cliente': cliente})

@login_required
def agenda_contatos(request):
    query = request.GET.get('q')
    funcionarios_list = Funcionario.objects.all().order_by('nome')
    if query:
        funcionarios_list = funcionarios_list.filter(nome__icontains=query)
    context = {
        'funcionarios': funcionarios_list,
        'query': query,
    }
    return render(request, 'agenda_contatos.html', context)

@login_required
def politica_de_privacidade(request):
    return render(request, 'politica_de_privacidade.html')

@login_required
def gestao_seguros(request):
    if request.method == 'POST':
        form = SeguroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo seguro adicionado com sucesso!')
            return redirect('APP:gestao_seguros')
    else:
        form = SeguroForm()

    # CORREÇÃO APLICADA AQUI
    seguros = Seguro.objects.all().order_by('cliente__cliente')

    context = {
        'form': form,
        'seguros': seguros,
    }
    return render(request, 'gestao_seguros.html', context)

# página para download de documentos e apólices
# Em APP/views.py

@login_required
def pagina_downloads(request):
    # Busca clientes que tenham arquivos PGR ou DDR
    clientes_com_pgr = Cliente.objects.exclude(pgr_arquivo='').order_by('cliente')
    clientes_com_ddr = Cliente.objects.exclude(ddr_arquivo='').order_by('cliente')
    
    # CORREÇÃO AQUI: Busca todos os seguros que têm o campo 'apolice_anexo' preenchido
    seguros_com_apolices = Seguro.objects.exclude(apolice_anexo='').order_by('cliente__cliente')

    context = {
        'clientes_com_pgr': clientes_com_pgr,
        'clientes_com_ddr': clientes_com_ddr,
        'seguros_com_apolices': seguros_com_apolices,
    }
    return render(request, 'downloads.html', context)

@login_required
def gestao_averbacoes(request):
    if request.method == 'POST':
        form = AverbacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Averbação cadastrada com sucesso!')
            return redirect('APP:gestao_averbacoes')
    
    form = AverbacaoForm()
    averbacoes = Averbacao.objects.all()

    # Lógica para os cards de estatísticas
    total_count = averbacoes.count()
    ddr_count = averbacoes.filter(tipo_seguro='DDR').count()
    intalog_count = averbacoes.filter(tipo_seguro='INTALOG').count()
    
    # --- NOVA LÓGICA PARA O GRÁFICO ---
    chart_labels = ['DDR/Carta Conforto', 'Averbado Intalog']
    chart_data = [ddr_count, intalog_count]

    context = {
        'form': form,
        'averbacoes': averbacoes,
        'total_count': total_count,
        'ddr_count': ddr_count,
        'intalog_count': intalog_count,
        # Adiciona os dados do gráfico ao contexto, convertidos para JSON
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'averbacoes.html', context)

@login_required
def gestao_gerenciadoras(request):
    if request.method == 'POST':
        form = GerenciadoraRiscoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gerenciadora de Risco cadastrada com sucesso!')
            return redirect('APP:gestao_gerenciadoras')

    form = GerenciadoraRiscoForm()
    gerenciadoras = GerenciadoraRisco.objects.all()

    context = {
        'form': form,
        'gerenciadoras': gerenciadoras
    }
    return render(request, 'gerenciadoras.html', context)

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def cadastrar_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo usuário cadastrado com sucesso!')
            return redirect('APP:cadastrar_usuario')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'cadastrar_usuario.html', {'form': form})