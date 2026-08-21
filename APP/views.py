import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from django.contrib.auth.models import User, Permission
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDay
from datetime import date, timedelta, datetime
import holidays
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from django.template.loader import render_to_string

# Importa todos os formulários e modelos necessários
from .forms import (
    FuncionarioForm, ClienteForm, RegraDeEmbarqueFormSet, 
    SeguroForm, MensagemForm, CustomAuthenticationForm, CustomPasswordChangeForm,
    AverbacaoForm, GerenciadoraRiscoForm, CustomUserCreationForm, SinistroForm, EditarSinistroForm, RotogramaForm,
    VeiculoChecklistForm, GRChecklistForm, ChecklistForm, TreinamentoQSMSForm, CertificadoQSMSForm, EventoQSMSForm, 
    ContratoDiversoForm, ServicoPendenteForm, AcaoServicoPendenteForm, ServicoPendenteQSMSForm, AcaoServicoPendenteQSMSForm,
    VeiculoAsseguradoForm, BlackListForm
)
from .models import (
    Funcionario, Cliente, RegraDeEmbarque, Seguro, 
    Mensagem, Averbacao, GerenciadoraRisco, Sinistro, Rotograma,
    ChecklistVeiculo, ChecklistGR, Checklist, TreinamentoQSMS, Permissoes, CertificadoQSMS, EventoQSMS,
    ContratoDiverso, ServicoPendente, HistoricoAcao, ServicoPendenteQSMS, HistoricoAcaoQSMS,
    VeiculoAssegurado, BlackList
)


def is_superuser(user):
    return user.is_superuser


@login_required
@permission_required('APP.can_view_dashboard', raise_exception=True)
def dashboard(request):
    hoje = date.today()

    # --- BLOCO DE CONTAGENS GERAIS ---
    total_clientes = Cliente.objects.count()
    total_gerenciadoras = GerenciadoraRisco.objects.count()
    total_seguros = Seguro.objects.count()
    total_averbacoes = Averbacao.objects.count()
    downloads_pgr = Cliente.objects.exclude(pgr_arquivo='').count()
    downloads_ddr = Cliente.objects.exclude(ddr_arquivo='').count()
    downloads_apolices = Seguro.objects.exclude(apolice_anexo='').count()
    total_downloads = downloads_pgr + downloads_ddr + downloads_apolices
    sinistros_em_andamento = Sinistro.objects.filter(status='ANDAMENTO').count()
    total_rotogramas = Rotograma.objects.count()
    total_usuarios = User.objects.count()
    total_contratos = ContratoDiverso.objects.count()
    total_veiculos_assegurados = VeiculoAssegurado.objects.count()

    # --- BLOCO DE CONTAGENS QSMS ---
    treinamentos_pendentes = TreinamentoQSMS.objects.filter(concluido=False).count()
    limite_vencimento = hoje + timedelta(days=60)
    certificados_alerta = CertificadoQSMS.objects.filter(data_validade__lte=limite_vencimento).count()
    eventos_pendentes = EventoQSMS.objects.filter(concluido=False).count()
    tarefas_em_aberto_qsms = ServicoPendenteQSMS.objects.exclude(status='FINALIZADO').count()
    
    # --- BLOCO DE CONTAGENS GERENCIAMENTO DE RISCO ---
    todos_checklists_aprovados = Checklist.objects.filter(aprovado=True, data_aprovacao__isnull=False).select_related('gr')
    checklists_vencidos = 0
    for checklist in todos_checklists_aprovados:
        data_vencimento = checklist.data_aprovacao + timedelta(days=checklist.gr.validade_checklist)
        if data_vencimento < hoje:
            checklists_vencidos += 1
            
    tarefas_em_aberto = ServicoPendente.objects.exclude(status='FINALIZADO').count()

    # --- DADOS PARA GRÁFICOS E MENSAGENS ---
    mensagens_gerais = Mensagem.objects.filter(destinatario__isnull=True).order_by('-data_envio')[:5]
    mensagens_pessoais = Mensagem.objects.filter(destinatario=request.user).order_by('-data_envio')[:5]
    
    total_blacklist = BlackList.objects.count()

    # --- CONTEXTO FINAL ---
    context = {
        'total_clientes': total_clientes, 
        'total_gerenciadoras': total_gerenciadoras,
        'total_seguros': total_seguros, 
        'total_averbacoes': total_averbacoes,
        'total_downloads': total_downloads,
        'sinistros_em_andamento': sinistros_em_andamento,
        'total_rotogramas': total_rotogramas,
        'total_usuarios': total_usuarios,
        'total_contratos': total_contratos,
        'checklists_vencidos': checklists_vencidos,
        'treinamentos_pendentes': treinamentos_pendentes,
        'certificados_alerta': certificados_alerta,
        'eventos_pendentes': eventos_pendentes,
        'mensagens_gerais': mensagens_gerais,
        'mensagens_pessoais': mensagens_pessoais,
        'tarefas_em_aberto': tarefas_em_aberto,
        'tarefas_em_aberto_qsms': tarefas_em_aberto_qsms,
        'total_veiculos_assegurados': total_veiculos_assegurados,
        'total_blacklist': total_blacklist,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def enviar_mensagem(request):
    initial_data = {}
    reply_to_user_id = request.GET.get('responder_para')
    if reply_to_user_id:
        try:
            reply_user = User.objects.get(pk=reply_to_user_id)
            initial_data = {'tipo_destinatario': 'DIRECT', 'destinatario_usuario': reply_user}
        except User.DoesNotExist:
            pass
    if request.method == 'POST':
        form = MensagemForm(request.POST, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            destinatario = None
            if cd['tipo_destinatario'] == 'DIRECT':
                destinatario = cd['destinatario_usuario']
            Mensagem.objects.create(remetente=request.user, destinatario=destinatario, conteudo=cd['conteudo'], is_atencao=cd['is_atencao'])
            messages.success(request, 'Mensagem enviada com sucesso!')
            return redirect('APP:enviar_mensagem')
    else:
        form = MensagemForm(user=request.user, initial=initial_data)
    return render(request, 'enviar_mensagem.html', {'form': form})


@login_required
def marcar_como_lida(request, pk):
    if request.method == 'POST':
        try:
            mensagem = Mensagem.objects.get(pk=pk, destinatario=request.user)
            if not mensagem.lida:
                mensagem.lida = True
                mensagem.save()
            return JsonResponse({'status': 'success'})
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
    context = {'funcionarios': funcionarios, 'query': query}
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
        return redirect('APP:consultar_funcionarios')
    return render(request, 'excluir_funcionario.html', {'funcionario': funcionario})


@login_required
@permission_required('APP.can_add_pgr', raise_exception=True)
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
    context = {'form': form, 'formset': formset}
    return render(request, 'cadastrar_cliente.html', context)


@login_required
@permission_required('APP.can_view_pgr_list', raise_exception=True)
def listar_clientes(request):
    query = request.GET.get('q')
    clientes_list = Cliente.objects.all().order_by('vigencia_pgr')

    if query:
        clientes_list = clientes_list.filter(cliente__icontains=query)

    hoje = date.today()
    quatro_meses = hoje + timedelta(days=120)
    dois_meses = hoje + timedelta(days=60)

    for cliente in clientes_list:
        if cliente.vigencia_pgr:
            if cliente.vigencia_pgr < hoje:
                cliente.status_vencimento = 'vencido'
            elif hoje <= cliente.vigencia_pgr < dois_meses:
                cliente.status_vencimento = 'urgente'
            elif dois_meses <= cliente.vigencia_pgr < quatro_meses:
                cliente.status_vencimento = 'proximo'
            else:
                cliente.status_vencimento = 'ok'
        else:
            cliente.status_vencimento = ''

    context = {
        'clientes': clientes_list,
        'query': query,
    }
    return render(request, 'listar_clientes.html', context)


@login_required
@permission_required('APP.can_change_pgr', raise_exception=True)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        formset = RegraDeEmbarqueFormSet(request.POST, instance=cliente, prefix='regras')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Cadastro do cliente "{cliente.cliente}" atualizado com sucesso!')
            return redirect('APP:consultar_clientes')
    else:
        form = ClienteForm(instance=cliente)
        formset = RegraDeEmbarqueFormSet(instance=cliente, prefix='regras')
    context = {'form': form, 'formset': formset, 'cliente': cliente}
    return render(request, 'editar_cliente.html', context)


@login_required
@permission_required('APP.can_delete_pgr', raise_exception=True)
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        nome_cliente = cliente.cliente
        cliente.delete()
        messages.success(request, f'Cliente "{nome_cliente}" e todas as suas regras foram excluídos com sucesso.')
        return redirect('APP:consultar_clientes')
    return render(request, 'excluir_cliente.html', {'cliente': cliente})


@login_required
def agenda_contatos(request):
    query = request.GET.get('q')
    funcionarios_list = Funcionario.objects.all().order_by('nome')
    if query:
        funcionarios_list = funcionarios_list.filter(nome__icontains=query)
    context = {'funcionarios': funcionarios_list, 'query': query}
    return render(request, 'agenda_contatos.html', context)


@login_required
def politica_de_privacidade(request):
    return render(request, 'politica_de_privacidade.html')


@login_required
@permission_required('APP.can_view_seguros_list', raise_exception=True)
def gestao_seguros(request):
    if request.method == 'POST':
        form = SeguroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo seguro cadastrado com sucesso!')
            return redirect('APP:gestao_seguros')
    else:
        form = SeguroForm()

    seguros_list = Seguro.objects.all().order_by('vigencia')
    
    hoje = date.today()
    quatro_meses = hoje + timedelta(days=120)
    dois_meses = hoje + timedelta(days=60)

    for seguro in seguros_list:
        if seguro.vigencia < hoje:
            seguro.status_vencimento = 'vencido'
        elif hoje <= seguro.vigencia < dois_meses:
            seguro.status_vencimento = 'urgente'
        elif dois_meses <= seguro.vigencia < quatro_meses:
            seguro.status_vencimento = 'proximo'
        else:
            seguro.status_vencimento = 'ok'
            
    context = {
        'form': form,
        'seguros': seguros_list,
    }
    return render(request, 'gestao_seguros.html', context)


@login_required
@permission_required('APP.can_view_ddr_list', raise_exception=True)
def gestao_averbacoes(request):
    if request.method == 'POST':
        form = AverbacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Averbação cadastrada com sucesso!')
            return redirect('APP:gestao_averbacoes')
    form = AverbacaoForm()
    averbacoes = Averbacao.objects.all()
    total_count = averbacoes.count()
    ddr_count = averbacoes.filter(tipo_seguro='DDR').count()
    intalog_count = averbacoes.filter(tipo_seguro='INTALOG').count()
    chart_labels = ['DDR/Carta Conforto', 'Averbado Intalog']
    chart_data = [ddr_count, intalog_count]
    context = {
        'form': form, 'averbacoes': averbacoes, 'total_count': total_count,
        'ddr_count': ddr_count, 'intalog_count': intalog_count,
        'chart_labels': json.dumps(chart_labels), 'chart_data': json.dumps(chart_data)
    }
    return render(request, 'averbacoes.html', context)


@login_required
@permission_required('APP.can_view_gr_list', raise_exception=True)
def gestao_gerenciadoras(request):
    if request.method == 'POST':
        form = GerenciadoraRiscoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gerenciadora de Risco cadastrada com sucesso!')
            return redirect('APP:gestao_gerenciadoras')
    form = GerenciadoraRiscoForm()
    gerenciadoras = GerenciadoraRisco.objects.all()
    context = {'form': form, 'gerenciadoras': gerenciadoras}
    return render(request, 'gerenciadoras.html', context)


@login_required
@permission_required('APP.can_view_downloads', raise_exception=True)
def pagina_downloads(request):
    clientes_com_pgr = Cliente.objects.exclude(pgr_arquivo='').order_by('cliente')
    clientes_com_ddr = Cliente.objects.exclude(ddr_arquivo='').order_by('cliente')
    seguros_com_apolices = Seguro.objects.exclude(apolice_anexo='').order_by('cliente__cliente')
    seguros_com_certificados = Seguro.objects.exclude(certificado_anexo='').order_by('cliente__cliente')

    context = {
        'clientes_com_pgr': clientes_com_pgr,
        'clientes_com_ddr': clientes_com_ddr,
        'seguros_com_apolices': seguros_com_apolices,
        'seguros_com_certificados': seguros_com_certificados,
    }
    return render(request, 'downloads.html', context)


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
    
    context = {
        'form': form,
    }
    return render(request, 'cadastrar_usuario.html', context)


@login_required
@permission_required('APP.can_view_sinistros_list', raise_exception=True)
def gestao_sinistros(request):
    if request.method == 'POST':
        form = SinistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sinistro registrado com sucesso!')
            return redirect('APP:gestao_sinistros')

    form = SinistroForm()
    sinistros = Sinistro.objects.all()
    context = {
        'form': form,
        'sinistros': sinistros,
    }
    return render(request, 'sinistros.html', context)


@login_required
@permission_required('APP.can_change_sinistro', raise_exception=True)
def editar_sinistro(request, pk):
    sinistro = get_object_or_404(Sinistro, pk=pk)
    if request.method == 'POST':
        form = EditarSinistroForm(request.POST, instance=sinistro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de sinistro atualizado com sucesso!')
            return redirect('APP:gestao_sinistros')
    else:
        form = EditarSinistroForm(instance=sinistro)
            
    context = {
        'form': form,
        'sinistro': sinistro,
    }
    return render(request, 'editar_sinistro.html', context)


@login_required
@permission_required('APP.can_view_rotogramas_list', raise_exception=True)
def gestao_rotogramas(request):
    if request.method == 'POST':
        form = RotogramaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rotograma cadastrado com sucesso!')
            return redirect('APP:gestao_rotogramas')
    
    form = RotogramaForm()
    rotogramas = Rotograma.objects.all()
    return render(request, 'rotogramas.html', {'form': form, 'rotogramas': rotogramas})


@login_required
@permission_required('APP.can_add_rotograma', raise_exception=True)
def editar_rotograma(request, pk):
    rotograma = get_object_or_404(Rotograma, pk=pk)
    if request.method == 'POST':
        form = RotogramaForm(request.POST, request.FILES, instance=rotograma)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rotograma atualizado com sucesso!')
            return redirect('APP:gestao_rotogramas')
    else:
        form = RotogramaForm(instance=rotograma)
    
    context = {
        'form': form,
        'rotograma': rotograma
    }
    return render(request, 'editar_rotograma.html', context)


@login_required
@permission_required('APP.can_view_checklist_page', raise_exception=True)
def pagina_checklist(request):
    if request.method == 'POST':
        # ... (a lógica de POST permanece a mesma) ...
        if 'submit_veiculo' in request.POST:
            veiculo_form = VeiculoChecklistForm(request.POST)
            if veiculo_form.is_valid():
                veiculo_form.save()
                messages.success(request, 'Veículo adicionado com sucesso!')
                return redirect('APP:pagina_checklist')
        elif 'submit_gr' in request.POST:
            gr_form = GRChecklistForm(request.POST)
            if gr_form.is_valid():
                gr_form.save()
                messages.success(request, 'Gerenciadora de Risco adicionada com sucesso!')
                return redirect('APP:pagina_checklist')
        elif 'submit_checklist' in request.POST:
            instance = None
            veiculo_id = request.POST.get('veiculo')
            gr_id = request.POST.get('gr')
            if veiculo_id and gr_id:
                instance = Checklist.objects.filter(veiculo_id=veiculo_id, gr_id=gr_id).first()
            checklist_form = ChecklistForm(request.POST, instance=instance)
            if checklist_form.is_valid():
                checklist_instance = checklist_form.save(commit=False)
                checklist_instance.atualizado_por = request.user
                checklist_instance.save()
                messages.success(request, 'Checklist salvo com sucesso!')
                return redirect('APP:pagina_checklist')

    hoje = date.today()

    def preparar_dados_tabela(veiculos_qs, grs_qs, checklist_map):
        tabela_data = []
        for veiculo in veiculos_qs:
            linha = {'veiculo': veiculo, 'checklists_gr': []}
            for gr in grs_qs:
                checklist = checklist_map.get((veiculo.id, gr.id))
                celula = {
                    'gr_id': gr.id, 'gr_nome': gr.nome, 'aprovado': None, 
                    'data_aprovacao_str': '', 'motivo_reprovacao': '', 
                    'atualizado_por_nome': '', 'data_vencimento_str': ''
                }

                if checklist:
                    celula['aprovado'] = checklist.aprovado
                    celula['motivo_reprovacao'] = checklist.motivo_reprovacao
                    if checklist.atualizado_por:
                        celula['atualizado_por_nome'] = checklist.atualizado_por.username
                    
                    if checklist.aprovado:
                        data_vencimento = None
                        
                        # --- LÓGICA DE CÁLCULO ATUALIZADA ---
                        if checklist.data_validade_manual:
                            # Se a validade foi inserida, ela é a data de vencimento
                            data_vencimento = checklist.data_validade_manual
                            # E calculamos a data de realização
                            data_realizacao = data_vencimento - timedelta(days=gr.validade_checklist)
                            celula['data_aprovacao_str'] = data_realizacao.strftime('%d/%m/%Y')
                        
                        elif checklist.data_aprovacao:
                            # Se a aprovação foi inserida, ela é a data de realização
                            data_realizacao = checklist.data_aprovacao
                            celula['data_aprovacao_str'] = data_realizacao.strftime('%d/%m/%Y')
                            # E calculamos a data de vencimento
                            data_vencimento = data_realizacao + timedelta(days=gr.validade_checklist)
                        # --- FIM DA LÓGICA ATUALIZADA ---

                        if data_vencimento:
                            dias_restantes = (data_vencimento - hoje).days
                            celula['dias_restantes'] = dias_restantes
                            celula['data_vencimento_str'] = data_vencimento.strftime('%d/%m/%Y')
                            
                            if dias_restantes < 0: celula['status_cor'] = 'vermelho'
                            elif dias_restantes <= 10: celula['status_cor'] = 'vermelho'
                            elif dias_restantes <= 20: celula['status_cor'] = 'amarelo'
                            else: celula['status_cor'] = 'verde'
                        else:
                            celula['dias_restantes'] = "OK"
                            celula['status_cor'] = 'verde'
                    elif not checklist.aprovado:
                        celula['dias_restantes'] = "Reprovado"
                        celula['status_cor'] = 'vermelho'
                else:
                    celula['dias_restantes'] = "Inexistente"
                    celula['status_cor'] = 'cinza'
                linha['checklists_gr'].append(celula)
            tabela_data.append(linha)
        return tabela_data

    veiculos_cavalos = ChecklistVeiculo.objects.filter(tipo='CAVALO').order_by('placa')
    veiculos_carretas = ChecklistVeiculo.objects.filter(tipo='CARRETA').order_by('placa')
    
    grs = ChecklistGR.objects.all().order_by('nome')
    checklists = Checklist.objects.all().select_related('veiculo', 'gr', 'atualizado_por')
    checklist_map = {(c.veiculo.id, c.gr.id): c for c in checklists}

    tabela_cavalos_data = preparar_dados_tabela(veiculos_cavalos, grs, checklist_map)
    tabela_carretas_data = preparar_dados_tabela(veiculos_carretas, grs, checklist_map)

    checklists_vencidos = 0
    todos_checklists_aprovados = Checklist.objects.filter(aprovado=True, data_aprovacao__isnull=False).select_related('gr')
    for checklist in todos_checklists_aprovados:
        data_vencimento = checklist.data_aprovacao + timedelta(days=checklist.gr.validade_checklist)
        if data_vencimento < hoje:
            checklists_vencidos += 1

    context = {
        'veiculo_form': VeiculoChecklistForm(),
        'gr_form': GRChecklistForm(),
        'checklist_form': ChecklistForm(),
        'grs_header': grs,
        'tabela_cavalos_data': tabela_cavalos_data,
        'tabela_carretas_data': tabela_carretas_data,
        'checklists_vencidos': checklists_vencidos,
    }
    return render(request, 'checklist.html', context)


@login_required
@permission_required('APP.can_view_treinamentos_list', raise_exception=True)
def agenda_treinamentos(request):
    if request.method == 'POST':
        form = TreinamentoQSMSForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treinamento adicionado com sucesso!')
            return redirect('APP:agenda_treinamentos')
    
    form = TreinamentoQSMSForm()
    treinamentos = TreinamentoQSMS.objects.all()
    
    context = {
        'form': form,
        'treinamentos': treinamentos,
    }
    return render(request, 'agenda_treinamentos.html', context)


@login_required
@permission_required('APP.can_change_treinamento', raise_exception=True)
def editar_treinamento(request, pk):
    treinamento = get_object_or_404(TreinamentoQSMS, pk=pk)
    if request.method == 'POST':
        form = TreinamentoQSMSForm(request.POST, instance=treinamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treinamento atualizado com sucesso!')
            return redirect('APP:agenda_treinamentos')
    else:
        form = TreinamentoQSMSForm(instance=treinamento)
    
    context = {
        'form': form,
        'treinamento': treinamento
    }
    return render(request, 'editar_treinamento.html', context)

@login_required
def treinamentos_json(request):
    treinamentos = TreinamentoQSMS.objects.all()
    eventos = []
    for treinamento in treinamentos:
        # Combina a data e a hora para criar um objeto datetime completo
        start_datetime = datetime.combine(treinamento.data_evento, treinamento.hora_evento)
        eventos.append({
            'title': treinamento.assunto,
            'start': start_datetime.isoformat(), # Formato ISO 8601 (ex: '2025-09-03T10:30:00')
        })
    return JsonResponse(eventos, safe=False)

@login_required
@permission_required('APP.can_view_certificados_list', raise_exception=True)
def gestao_certificados(request):
    if request.method == 'POST' and request.user.has_perm('APP.can_add_certificado'):
        form = CertificadoQSMSForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certificado adicionado com sucesso!')
            return redirect('APP:gestao_certificados')
    
    form = CertificadoQSMSForm()
    certificados = CertificadoQSMS.objects.all()
    
    # Lógica de status de vencimento (igual à de seguros)
    hoje = date.today()
    quatro_meses = hoje + timedelta(days=120)
    dois_meses = hoje + timedelta(days=60)

    for cert in certificados:
        if cert.data_validade < hoje:
            cert.status_vencimento = 'vencido'
        elif hoje <= cert.data_validade < dois_meses:
            cert.status_vencimento = 'urgente'
        elif dois_meses <= cert.data_validade < quatro_meses:
            cert.status_vencimento = 'proximo'
        else:
            cert.status_vencimento = 'ok'
            
    context = {
        'form': form,
        'certificados': certificados,
    }
    return render(request, 'certificados_qsm.html', context)

@login_required
@permission_required('APP.can_change_certificado', raise_exception=True)
def editar_certificado(request, pk):
    certificado = get_object_or_404(CertificadoQSMS, pk=pk)
    if request.method == 'POST':
        form = CertificadoQSMSForm(request.POST, request.FILES, instance=certificado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certificado atualizado com sucesso!')
            return redirect('APP:gestao_certificados')
    else:
        form = CertificadoQSMSForm(instance=certificado)

    context = {
        'form': form,
        'certificado': certificado
    }
    return render(request, 'editar_certificado.html', context)

@login_required
@permission_required('APP.can_view_eventos_list', raise_exception=True)
def calendario_eventos(request):
    if request.method == 'POST' and request.user.has_perm('APP.can_add_evento'):
        form = EventoQSMSForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento adicionado com sucesso!')
            return redirect('APP:calendario_eventos')

    form = EventoQSMSForm()
    eventos = EventoQSMS.objects.all()

    context = { 'form': form, 'eventos': eventos }
    return render(request, 'calendario_eventos.html', context)

@login_required
@permission_required('APP.can_change_evento', raise_exception=True)
def editar_evento(request, pk):
    evento = get_object_or_404(EventoQSMS, pk=pk)
    if request.method == 'POST':
        form = EventoQSMSForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('APP:calendario_eventos')
    else:
        form = EventoQSMSForm(instance=evento)

    context = { 'form': form, 'evento': evento }
    return render(request, 'editar_evento.html', context)

@login_required
def eventos_json(request):
    eventos = EventoQSMS.objects.all()
    eventos_formatados = []
    for evento in eventos:
        start_datetime = datetime.combine(evento.data_evento, evento.hora_evento)
        eventos_formatados.append({
            'title': evento.titulo,
            'start': start_datetime.isoformat(),
        })
    return JsonResponse(eventos_formatados, safe=False)

@login_required
@permission_required('APP.can_view_contratos_list', raise_exception=True)
def gestao_contratos(request):
    if request.method == 'POST' and request.user.has_perm('APP.can_add_contrato'):
        form = ContratoDiversoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrato adicionado com sucesso!')
            return redirect('APP:gestao_contratos')

    form = ContratoDiversoForm()
    contratos = ContratoDiverso.objects.all()

    context = {
        'form': form,
        'contratos': contratos,
    }
    return render(request, 'contratos_diversos.html', context)

@login_required
@permission_required('APP.can_view_servicos_pendentes', raise_exception=True)
def servicos_pendentes(request):
    if request.method == 'POST' and request.user.has_perm('APP.can_add_servico_pendente'):
        form = ServicoPendenteForm(request.POST)
        if form.is_valid():
            servico = form.save(commit=False)
            servico.criado_por = request.user
            servico.save()
            messages.success(request, 'Nova tarefa adicionada com sucesso!')
            return redirect('APP:servicos_pendentes')

    # LÓGICA DE PAGINAÇÃO PARA OS FINALIZADOS
    finalizadas_list = ServicoPendente.objects.filter(
        status='FINALIZADO'
    ).select_related('criado_por', 'iniciado_por', 'finalizado_por').order_by('-data_finalizacao')

    paginator = Paginator(finalizadas_list, 10) # 10 itens por página
    page_obj = paginator.get_page(1) # Pega a primeira página

    context = {
        'form_criacao': ServicoPendenteForm(),
        'form_acao': AcaoServicoPendenteForm(),
        'tarefas_pendentes': ServicoPendente.objects.filter(status='PENDENTE').select_related('criado_por'),
        'tarefas_iniciadas': ServicoPendente.objects.filter(status='INICIADO').select_related('criado_por', 'iniciado_por'),
        'tarefas_finalizadas': page_obj, # Envia o objeto da página para o template
    }
    return render(request, 'servicos_pendentes.html', context)

@login_required
def carregar_mais_finalizadas_gr(request):
    page_number = request.GET.get('page', 1)
    finalizadas_list = ServicoPendente.objects.filter(status='FINALIZADO').select_related('finalizado_por').order_by('-data_finalizacao')
    paginator = Paginator(finalizadas_list, 10)
    page_obj = paginator.get_page(page_number)

    # Renderiza apenas os cards, sem a página inteira
    rendered_cards = render_to_string(
        'partials/_kanban_card_gr.html', 
        {'tarefas_finalizadas': page_obj}
    )

    return JsonResponse({
        'html': rendered_cards,
        'has_next': page_obj.has_next()
    })

@login_required
@require_POST
def api_editar_servico(request, pk):
    servico = get_object_or_404(ServicoPendente, pk=pk)
    
    # Verifica permissão
    if not request.user.has_perm('APP.can_add_servico_pendente'):
        return JsonResponse({'status': 'error', 'message': 'Sem permissão para editar.'}, status=403)

    try:
        data = json.loads(request.body)
        novo_titulo = data.get('titulo')
        nova_descricao = data.get('descricao')
    except json.JSONDecodeError:
        novo_titulo = request.POST.get('titulo')
        nova_descricao = request.POST.get('descricao')

    if not novo_titulo or not nova_descricao:
        return JsonResponse({'status': 'error', 'message': 'Título e Descrição são obrigatórios.'}, status=400)

    alteracoes = []
    if servico.titulo != novo_titulo:
        alteracoes.append(f"Título alterado de '{servico.titulo}' para '{novo_titulo}'")
        servico.titulo = novo_titulo
    
    if servico.descricao != nova_descricao:
        alteracoes.append("Descrição atualizada")
        servico.descricao = nova_descricao

    if alteracoes:
        servico.save()
        HistoricoAcao.objects.create(
            servico=servico,
            usuario=request.user,
            acao=f"EDIÇÃO DO SERVIÇO: {'; '.join(alteracoes)}"
        )
        return JsonResponse({'status': 'success', 'message': 'Serviço atualizado com sucesso!'})
    
    return JsonResponse({'status': 'info', 'message': 'Nenhuma alteração detectada.'})

@login_required
def detalhes_servico_json(request, pk):
    servico = get_object_or_404(ServicoPendente, pk=pk)
    
    # Busca o histórico de ações
    historico_acoes = servico.historico_acoes.order_by('data_acao')
    
    data = {
        'id': servico.pk,
        'titulo': servico.titulo,
        'descricao': servico.descricao,
        'status': servico.status,

        # CORREÇÃO: Usar timezone.localtime() para converter do UTC para o fuso local
        'criado_por': servico.criado_por.username if servico.criado_por else 'N/A',
        'data_criacao': timezone.localtime(servico.data_criacao).strftime('%d/%m/%Y às %H:%M'),
        
        'iniciado_por': servico.iniciado_por.username if servico.iniciado_por else 'N/A',
        'data_inicio_tratativa': timezone.localtime(servico.data_inicio_tratativa).strftime('%d/%m/%Y às %H:%M') if servico.data_inicio_tratativa else 'N/A',
        
        'historico_acoes': [
            {
                'usuario': acao.usuario.username if acao.usuario else 'N/A',
                'data': timezone.localtime(acao.data_acao).strftime('%d/%m/%Y às %H:%M'),
                'texto': acao.acao
            } 
            for acao in historico_acoes
        ],

        'finalizado_por': servico.finalizado_por.username if servico.finalizado_por else 'N/A',
        'data_finalizacao': timezone.localtime(servico.data_finalizacao).strftime('%d/%m/%Y às %H:%M') if servico.data_finalizacao else 'N/A',
    }
    return JsonResponse(data)

@require_POST
@permission_required('APP.can_start_servico_pendente', raise_exception=True)
def iniciar_servico(request, pk):
    servico = get_object_or_404(ServicoPendente, pk=pk, status='PENDENTE')
    servico.status = 'INICIADO'
    servico.iniciado_por = request.user
    servico.data_inicio_tratativa = timezone.now()
    servico.save()
    return JsonResponse({'status': 'success', 'message': 'Tarefa iniciada.'})

@require_POST
@permission_required('APP.can_update_action_servico_pendente', raise_exception=True)
def atualizar_acao_servico(request, pk):
    servico = get_object_or_404(ServicoPendente, pk=pk, status='INICIADO')
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido.'}, status=400)

    form = AcaoServicoPendenteForm(data)
    
    if form.is_valid():
        # Cria um novo registro de histórico com os dados validados
        HistoricoAcao.objects.create(
            servico=servico,
            usuario=request.user,
            acao=form.cleaned_data['acao']
        )
        return JsonResponse({'status': 'success', 'message': 'Ação gravada.'})
    
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@require_POST
@permission_required('APP.can_finalize_servico_pendente', raise_exception=True)
def finalizar_servico(request, pk):
    servico = get_object_or_404(ServicoPendente, pk=pk, status='INICIADO')
    servico.status = 'FINALIZADO'
    servico.finalizado_por = request.user
    servico.data_finalizacao = timezone.now()
    servico.save()
    return JsonResponse({'status': 'success', 'message': 'Tarefa finalizada.'})

@login_required
@permission_required('APP.can_view_servicos_pendentes_qsms', raise_exception=True)
def servicos_pendentes_qsms(request):
    if request.method == 'POST' and request.user.has_perm('APP.can_add_servico_pendente_qsms'):
        form = ServicoPendenteQSMSForm(request.POST)
        if form.is_valid():
            servico = form.save(commit=False)
            servico.criado_por = request.user
            servico.save()
            messages.success(request, 'Nova tarefa QSMS adicionada com sucesso!')
            return redirect('APP:servicos_pendentes_qsms')

    # LÓGICA DE PAGINAÇÃO PARA OS FINALIZADOS
    finalizadas_list = ServicoPendenteQSMS.objects.filter(
        status='FINALIZADO'
    ).select_related('criado_por', 'iniciado_por', 'finalizado_por').order_by('-data_finalizacao')

    paginator = Paginator(finalizadas_list, 10) # 10 itens por página
    page_obj = paginator.get_page(1) # Pega a primeira página

    context = {
        'form_criacao': ServicoPendenteQSMSForm(),
        'tarefas_pendentes': ServicoPendenteQSMS.objects.filter(status='PENDENTE').select_related('criado_por'),
        'tarefas_iniciadas': ServicoPendenteQSMS.objects.filter(status='INICIADO').select_related('criado_por', 'iniciado_por'),
        'tarefas_finalizadas': page_obj, # Envia o objeto da página para o template
    }
    return render(request, 'servicos_pendentes_qsms.html', context)

@login_required
def carregar_mais_finalizadas_qsms(request):
    page_number = request.GET.get('page', 1)
    finalizadas_list = ServicoPendenteQSMS.objects.filter(status='FINALIZADO').select_related('finalizado_por').order_by('-data_finalizacao')
    paginator = Paginator(finalizadas_list, 10)
    page_obj = paginator.get_page(page_number)

    # Renderiza apenas os cards, sem a página inteira
    rendered_cards = render_to_string(
        'partials/_kanban_card_qsms.html', 
        {'tarefas_finalizadas': page_obj}
    )

    return JsonResponse({
        'html': rendered_cards,
        'has_next': page_obj.has_next()
    })

@login_required
def detalhes_servico_qsms_json(request, pk):
    servico = get_object_or_404(ServicoPendenteQSMS, pk=pk)
    historico_acoes = servico.historico_acoes_qsms.order_by('data_acao')
    data = {
        'id': servico.pk, 'titulo': servico.titulo, 'descricao': servico.descricao, 'status': servico.status,
        'criado_por': servico.criado_por.username if servico.criado_por else 'N/A',
        'data_criacao': timezone.localtime(servico.data_criacao).strftime('%d/%m/%Y às %H:%M'),
        'iniciado_por': servico.iniciado_por.username if servico.iniciado_por else 'N/A',
        'data_inicio_tratativa': timezone.localtime(servico.data_inicio_tratativa).strftime('%d/%m/%Y às %H:%M') if servico.data_inicio_tratativa else 'N/A',
        'historico_acoes': [{'usuario': a.usuario.username if a.usuario else 'N/A', 'data': timezone.localtime(a.data_acao).strftime('%d/%m/%Y às %H:%M'), 'texto': a.acao} for a in historico_acoes],
        'finalizado_por': servico.finalizado_por.username if servico.finalizado_por else 'N/A',
        'data_finalizacao': timezone.localtime(servico.data_finalizacao).strftime('%d/%m/%Y às %H:%M') if servico.data_finalizacao else 'N/A',
    }
    return JsonResponse(data)

@require_POST
@permission_required('APP.can_start_servico_pendente_qsms', raise_exception=True)
def iniciar_servico_qsms(request, pk):
    servico = get_object_or_404(ServicoPendenteQSMS, pk=pk, status='PENDENTE')
    servico.status = 'INICIADO'
    servico.iniciado_por = request.user
    servico.data_inicio_tratativa = timezone.now()
    servico.save()
    return JsonResponse({'status': 'success'})

@require_POST
@permission_required('APP.can_update_action_servico_pendente_qsms', raise_exception=True)
def atualizar_acao_servico_qsms(request, pk):
    servico = get_object_or_404(ServicoPendenteQSMS, pk=pk, status='INICIADO')
    data = json.loads(request.body)
    form = AcaoServicoPendenteQSMSForm(data)
    if form.is_valid():
        HistoricoAcaoQSMS.objects.create(servico=servico, usuario=request.user, acao=form.cleaned_data['acao'])
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@require_POST
@permission_required('APP.can_finalize_servico_pendente_qsms', raise_exception=True)
def finalizar_servico_qsms(request, pk):
    servico = get_object_or_404(ServicoPendenteQSMS, pk=pk, status='INICIADO')
    servico.status = 'FINALIZADO'
    servico.finalizado_por = request.user
    servico.data_finalizacao = timezone.now()
    servico.save()
    return JsonResponse({'status': 'success'})

@login_required
@permission_required('APP.can_view_veiculos_assegurados', raise_exception=True)
def gestao_veiculos_assegurados(request):
    if request.method == 'POST' and request.user.has_perm('APP.can_add_veiculo_assegurado'):
        form = VeiculoAsseguradoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo assegurado adicionado com sucesso!')
            return redirect('APP:gestao_veiculos_assegurados')
    
    form = VeiculoAsseguradoForm()
    veiculos = VeiculoAssegurado.objects.all()

    # Lógica de status de vencimento
    hoje = date.today()
    quatro_meses = hoje + timedelta(days=120)
    dois_meses = hoje + timedelta(days=60)

    for veiculo in veiculos:
        if veiculo.vigencia < hoje:
            veiculo.status_vencimento = 'vencido'
        elif hoje <= veiculo.vigencia < dois_meses:
            veiculo.status_vencimento = 'urgente'
        elif dois_meses <= veiculo.vigencia < quatro_meses:
            veiculo.status_vencimento = 'proximo'
        else:
            veiculo.status_vencimento = 'ok'

    context = { 'form': form, 'veiculos': veiculos }
    return render(request, 'veiculos_assegurados.html', context)


@login_required
@permission_required('APP.can_change_veiculo_assegurado', raise_exception=True)
def editar_veiculo_assegurado(request, pk):
    veiculo = get_object_or_404(VeiculoAssegurado, pk=pk)
    if request.method == 'POST':
        form = VeiculoAsseguradoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo atualizado com sucesso!')
            return redirect('APP:gestao_veiculos_assegurados')
    else:
        form = VeiculoAsseguradoForm(instance=veiculo)
    context = { 'form': form, 'veiculo': veiculo }
    return render(request, 'editar_veiculo_assegurado.html', context)


# --- BLACK-LIST ---

def is_gr_or_admin(user):
    return user.is_superuser or user.groups.filter(name__in=['GR', 'GR - Admin']).exists()

@login_required
@permission_required('APP.can_view_blacklist', raise_exception=True)
def blacklist_view(request):
    registros = BlackList.objects.all()
    pode_editar = is_gr_or_admin(request.user)
    context = {
        'registros': registros,
        'pode_editar': pode_editar
    }
    return render(request, 'blacklist.html', context)

@login_required
@user_passes_test(is_gr_or_admin)
def add_blacklist(request):
    if request.method == 'POST':
        form = BlackListForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Motorista adicionado à Black-List com sucesso!')
            return redirect('APP:blacklist')
    else:
        form = BlackListForm()
    context = {'form': form, 'acao': 'Adicionar'}
    return render(request, 'cadastrar_blacklist.html', context)

@login_required
@user_passes_test(is_gr_or_admin)
def edit_blacklist(request, pk):
    registro = get_object_or_404(BlackList, pk=pk)
    if request.method == 'POST':
        form = BlackListForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro atualizado com sucesso!')
            return redirect('APP:blacklist')
    else:
        form = BlackListForm(instance=registro)
    context = {'form': form, 'acao': 'Editar'}
    return render(request, 'editar_blacklist.html', context)

@login_required
@user_passes_test(is_gr_or_admin)
def delete_blacklist(request, pk):
    registro = get_object_or_404(BlackList, pk=pk)
    if request.method == 'POST':
        registro.delete()
        messages.success(request, 'Registro removido da Black-List com sucesso!')
        return redirect('APP:blacklist')
    context = {'registro': registro}
    return render(request, 'excluir_blacklist.html', context)