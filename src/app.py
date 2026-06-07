import sys
import os
import time
import streamlit as st
import pandas as pd
import requests
import json
import importlib
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. CONFIGURACIÓN DE RUTAS E IMPORTACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    import config
    import agente
    import skills
    importlib.reload(config)
    importlib.reload(agente)
    importlib.reload(skills)
    from config import MODELO, OPENROUTER_API_KEY, CAMINHO_CSV
    from agente import carregar_dados_base, carregar_transacoes, salvar_nova_transacao, salvar_perfil, carregar_tipos, adicionar_tipo, renomear_tipo, remover_tipo
    from skills import exibir_rastreador_metas, exibir_diagnostico_financeiro, exibir_simulador_investimentos, exibir_motivacao, exibir_alertas_vencimento, exibir_botao_download_pdf
    from database import init_db, migrar_dados_iniciais, get_session, ChatHistory
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# --- 2. CONFIGURACIÓN DE PÁGINA Y ESTADOS ---
st.set_page_config(page_title="LUMMI", page_icon="💰", layout="wide")

config.verificar_autenticacao()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "form_version" not in st.session_state:
    st.session_state.form_version = 0

# ── Histórico de Chat: tela limpa a cada novo dia ──
_hoje_str = datetime.now().strftime("%Y-%m-%d")
if "chat_data_carga" not in st.session_state or st.session_state.chat_data_carga != _hoje_str:
    # Novo dia: começa com tela limpa (não carrega o histórico anterior)
    st.session_state.messages = []
    st.session_state.chat_data_carga = _hoje_str

# Mensaje de éxito persistente que se muestra tras un rerun
if "msg_sucesso" in st.session_state:
    st.success(st.session_state.msg_sucesso)
    del st.session_state.msg_sucesso

# --- 3. INICIALIZAÇÃO DO BANCO E CARGA DE DADOS ---
init_db()
migrar_dados_iniciais(config.CAMINHO_CSV, config.CAMINHO_PERFIL)

perfil, edu = carregar_dados_base()
df_transacoes = carregar_transacoes()

# Manejo del Logo
logo_path = os.path.normpath(os.path.join(BASE_DIR, "..", "assets", "screenshots", "LOGOlummi.jpg"))
logo_img = Image.open(logo_path) if os.path.exists(logo_path) else None

st.title("🌟 LUMMI - Inteligência Financeira")

# --- 4. SIDEBAR: CÁLCULO DE SALDO Y GESTIÓN ---
with st.sidebar:
    if logo_img:
        st.image(logo_img, width="stretch")
    st.header("📊 Gestão Mensal")
    
    # ── Carregar tipos diretamente do banco de dados ──
    st.session_state.tipos_labels = carregar_tipos()

    # Procesamiento de fechas para el filtro
    df_transacoes["data"] = pd.to_datetime(df_transacoes["data"], errors="coerce")
    df_transacoes["mes_ano"] = df_transacoes["data"].dt.to_period("M").astype(str)
    
    meses_disp = sorted(df_transacoes["mes_ano"].dropna().unique(), reverse=True)
    meses_disp = [m for m in meses_disp if m != "NaT"]
    mes_selecionado = st.selectbox("Selecione o mês:", meses_disp) if meses_disp else datetime.now().strftime('%Y-%m')

    # ── LÓGICA DO SALDO (recalculada com todos os movimentos) ──
    df_mes = df_transacoes[df_transacoes['mes_ano'] == mes_selecionado].copy()

    # Entradas = entrada (salário + renda extra)
    entradas_mes = df_mes[df_mes['tipo'] == 'entrada']['valor'].sum()
    # Saídas = saida + saida mensal (exclui depósitos na reserva para não duplicar)
    saidas_mes = df_mes[
        df_mes['tipo'].isin(['saida', 'saida mensal']) &
        ~df_mes['descricao'].str.contains('Depósito Reserva de Emergência', na=False)
    ]['valor'].sum()
    # Depósitos na reserva descontam do saldo mas não entram em 'saidas_mes' (têm categoria própria)
    depositos_reserva_mes = df_mes[df_mes['descricao'].str.contains('Depósito Reserva de Emergência', na=False)]['valor'].sum()
    saldo_do_mes = entradas_mes - saidas_mes - depositos_reserva_mes

    # Resumo financeiro agrupado por tipo e categoria
    resumo_financeiro = df_mes.groupby(['tipo', 'categoria'])['valor'].sum().reset_index().to_dict(orient='records')

    # Saldo Acumulado (histórico)
    df_anterior = df_transacoes[df_transacoes['mes_ano'] < mes_selecionado]
    saidas_ant = df_anterior[
        df_anterior['tipo'].isin(['saida', 'saida mensal']) &
        ~df_anterior['descricao'].str.contains('Depósito Reserva de Emergência', na=False)
    ]['valor'].sum()
    dep_res_ant = df_anterior[df_anterior['descricao'].str.contains('Depósito Reserva de Emergência', na=False)]['valor'].sum()
    saldo_anterior = df_anterior[df_anterior['tipo'] == 'entrada']['valor'].sum() - saidas_ant - dep_res_ant
    saldo_total = saldo_anterior + saldo_do_mes

    # Dívidas totais pendentes
    total_dividas = df_transacoes[
        (df_transacoes['tipo'].str.contains('Divida', case=False, na=False)) &
        (df_transacoes['valor'] > 0)
    ]['valor'].sum()

    # Reserva de emergência (lida do perfil)
    reserva_atual = perfil.get('reserva_emergencia_atual', 0.0)
    reserva_meta = perfil.get('metas', [])
    # Tentar pegar meta de reserva se existir
    reserva_objetivo = 0.0
    for m in reserva_meta:
        if 'reserva' in str(m.get('meta', '')).lower():
            reserva_objetivo = float(m.get('valor_necessario', 0.0))
            break

    # ── MÉTRICA DE SALDO ──
    st.metric(
        label="💰 Saldo Total Acumulado",
        value=f"R$ {saldo_total:.2f}",
        delta=f"-R$ {total_dividas:.2f} (Dívidas Pendentes)",
        delta_color="inverse"
    )

    # ── RESERVA DE EMERGÊNCIA ──
    st.divider()
    pct_reserva = min(int((reserva_atual / reserva_objetivo) * 100), 100) if reserva_objetivo > 0 else 0
    st.markdown(f"**🛡️ Reserva de Emergência**")
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric("Acumulado", f"R$ {reserva_atual:.2f}")
    with col_res2:
        if reserva_objetivo > 0:
            st.metric("Meta", f"R$ {reserva_objetivo:.2f}")
        else:
            st.metric("Meta", "Não definida")
    if reserva_objetivo > 0:
        st.progress(pct_reserva / 100, text=f"{pct_reserva}% da meta atingida")

    # Congratulações se meta atingida
    if reserva_objetivo > 0 and reserva_atual >= reserva_objetivo:
        st.success("🎉 **Parabéns! Meta atingida!** Defina uma nova meta para continuar crescendo!")

    col_dep, col_meta = st.columns(2)
    with col_dep:
        with st.popover("💰 Depositar", use_container_width=True):
            st.markdown("**Transferir do saldo para a Reserva**")
            st.info(f"Saldo disponível: R$ {saldo_total:.2f}")
            valor_dep = st.number_input("Valor (R$)", min_value=0.01, max_value=float(max(saldo_total, 0.01)), step=10.0, key="dep_reserva_sidebar")
            if st.button("✅ Confirmar Depósito", key="btn_dep_reserva", use_container_width=True):
                perfil['reserva_emergencia_atual'] = reserva_atual + valor_dep
                salvar_perfil(perfil)
                salvar_nova_transacao(
                    data=datetime.now(),
                    desc="Depósito Reserva de Emergência",
                    cat="Reserva de Emergência",
                    valor=valor_dep,
                    tipo="saida"
                )
                st.session_state.msg_sucesso = f"🛡️ R$ {valor_dep:.2f} depositados na Reserva!"
                st.rerun()

    with col_meta:
        with st.popover("🎯 Alterar Meta", use_container_width=True):
            st.markdown("**Defina uma nova meta para sua Reserva de Emergência**")
            if reserva_objetivo > 0:
                st.info(f"Meta atual: R$ {reserva_objetivo:.2f}")
            nova_meta_val = st.number_input("Nova Meta (R$)", min_value=0.01, step=500.0, value=float(reserva_objetivo) if reserva_objetivo > 0 else 15000.0, key="nova_meta_reserva")
            if st.button("✅ Salvar Nova Meta", key="btn_nova_meta_reserva", use_container_width=True):
                # Atualizar a meta nas metas do perfil
                metas = perfil.get('metas', [])
                meta_encontrada = False
                for meta_item in metas:
                    if 'reserva' in str(meta_item.get('meta', '')).lower():
                        meta_item['valor_necessario'] = nova_meta_val
                        meta_encontrada = True
                        break
                if not meta_encontrada:
                    metas.append({
                        "meta": "Completar reserva de emergência",
                        "valor_necessario": nova_meta_val,
                        "prazo": ""
                    })
                perfil['metas'] = metas
                salvar_perfil(perfil)
                st.session_state.msg_sucesso = f"🎯 Nova meta de R$ {nova_meta_val:.2f} salva!"
                st.rerun()

    # ── GESTÃO DE METAS ──
    st.divider()
    st.markdown("**🎯 Minhas Metas**")

    metas_atuais = perfil.get('metas', [])

    # ── Montar lista unificada: Reserva de Emergência + outras metas ──
    # A Reserva é representada virtualmente para entrar no selectbox
    META_RESERVA_KEY = "__reserva__"
    lista_metas_display = []

    # 1. Adicionar a Reserva de Emergência sempre primeiro
    lista_metas_display.append({
        "__key__": META_RESERVA_KEY,
        "meta": "🛡️ Reserva de Emergência",
        "valor_necessario": reserva_objetivo,
        "valor_atual": reserva_atual,
        "prazo": next((m.get('prazo', '') for m in metas_atuais if 'reserva' in str(m.get('meta', '')).lower()), ''),
    })

    # 2. Adicionar as demais metas (excluindo a Reserva para não duplicar)
    for m in metas_atuais:
        if 'reserva' not in str(m.get('meta', '')).lower():
            lista_metas_display.append({**m, "__key__": None})

    # ── Selectbox unificado ──
    idx_meta_sel = st.selectbox(
        "Selecione uma meta:",
        range(len(lista_metas_display)),
        format_func=lambda i: (
            f"{lista_metas_display[i].get('meta', 'Sem nome')} — R$ {float(lista_metas_display[i].get('valor_necessario', 0)):.2f}"
        ),
        key="sel_meta_ativa"
    )
    meta_sel     = lista_metas_display[idx_meta_sel]
    eh_reserva   = meta_sel["__key__"] == META_RESERVA_KEY

    # Valores da meta selecionada
    meta_desc   = meta_sel.get('meta', 'Sem nome')
    meta_alvo   = float(meta_sel.get('valor_necessario', 0.0))
    meta_prazo  = meta_sel.get('prazo', '')
    meta_atual  = float(meta_sel.get('valor_atual', 0.0))
    pct_meta    = min(int((meta_atual / meta_alvo) * 100), 100) if meta_alvo > 0 else 0

    # ── Card da meta selecionada ──
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("💰 Acumulado", f"R$ {meta_atual:.2f}")
    with col_m2:
        st.metric("🏆 Objetivo", f"R$ {meta_alvo:.2f}" if meta_alvo > 0 else "Não definida")
    if meta_prazo:
        st.caption(f"📅 Prazo: {meta_prazo}")
    if meta_alvo > 0:
        st.progress(pct_meta / 100, text=f"{pct_meta}% da meta atingida")
    if meta_alvo > 0 and meta_atual >= meta_alvo:
        st.success(f"🎉 **Meta '{meta_desc}' conquistada!** Hora de sonhar mais alto!")

    # ── Botões de ação ──
    col_dep_m, col_edit_m, col_del_m = st.columns(3)

    # ─ Depositar ─
    with col_dep_m:
        with st.popover("💰 Depositar", use_container_width=True):
            st.markdown(f"**Depositar em: {meta_desc}**")
            st.info(f"Saldo disponível: R$ {saldo_total:.2f}")
            valor_dep_meta = st.number_input(
                "Valor (R$)", min_value=0.01,
                max_value=float(max(saldo_total, 0.01)),
                step=10.0, key="dep_meta_val"
            )
            if st.button("✅ Confirmar Depósito", key="btn_dep_meta", use_container_width=True):
                if eh_reserva:
                    # Lógica original da Reserva de Emergência
                    perfil['reserva_emergencia_atual'] = reserva_atual + valor_dep_meta
                    salvar_perfil(perfil)
                    salvar_nova_transacao(
                        data=datetime.now(),
                        desc="Depósito Reserva de Emergência",
                        cat="Reserva de Emergência",
                        valor=valor_dep_meta,
                        tipo="saida"
                    )
                    st.session_state.msg_sucesso = f"🛡️ R$ {valor_dep_meta:.2f} depositados na Reserva!"
                else:
                    # Lógica para metas comuns — credita em valor_atual
                    idx_real = next(
                        (i for i, m in enumerate(metas_atuais)
                         if m.get('meta') == meta_sel.get('meta')
                         and 'reserva' not in str(m.get('meta', '')).lower()),
                        None
                    )
                    if idx_real is not None:
                        metas_atuais[idx_real]['valor_atual'] = meta_atual + valor_dep_meta
                        perfil['metas'] = metas_atuais
                        salvar_perfil(perfil)
                    salvar_nova_transacao(
                        data=datetime.now(),
                        desc=f"Depósito Meta: {meta_desc}",
                        cat="Metas",
                        valor=valor_dep_meta,
                        tipo="saida"
                    )
                    st.session_state.msg_sucesso = f"🎯 R$ {valor_dep_meta:.2f} depositados em '{meta_desc}'!"
                st.rerun()

    # ─ Editar ─
    with col_edit_m:
        with st.popover("✏️ Editar", use_container_width=True):
            st.markdown(f"**Editar: {meta_desc}**")
            nova_desc_meta  = st.text_input(
                "Descrição", value=meta_desc,
                key=f"edit_meta_desc_{idx_meta_sel}",
                disabled=eh_reserva
            )
            novo_alvo_meta  = st.number_input(
                "Valor objetivo (R$)", min_value=0.01,
                value=float(meta_alvo) if meta_alvo > 0 else 1000.0,
                step=100.0,
                key=f"edit_meta_alvo_{idx_meta_sel}"
            )
            novo_prazo_meta = st.text_input(
                "Prazo (ex: 2027-06)", value=meta_prazo,
                key=f"edit_meta_prazo_{idx_meta_sel}"
            )
            if st.button("💾 Salvar Edição", key="btn_edit_meta", use_container_width=True):
                if eh_reserva:
                    # Atualiza na lista de metas (cria se não existir)
                    idx_res = next(
                        (i for i, m in enumerate(metas_atuais)
                         if 'reserva' in str(m.get('meta', '')).lower()), None
                    )
                    if idx_res is not None:
                        metas_atuais[idx_res]['valor_necessario'] = novo_alvo_meta
                        metas_atuais[idx_res]['prazo']           = novo_prazo_meta
                    else:
                        metas_atuais.append({
                            "meta": "Completar reserva de emergência",
                            "valor_necessario": novo_alvo_meta,
                            "prazo": novo_prazo_meta
                        })
                    perfil['metas'] = metas_atuais
                else:
                    idx_real = next(
                        (i for i, m in enumerate(metas_atuais)
                         if m.get('meta') == meta_sel.get('meta')
                         and 'reserva' not in str(m.get('meta', '')).lower()),
                        None
                    )
                    if idx_real is not None:
                        metas_atuais[idx_real]['meta']            = nova_desc_meta
                        metas_atuais[idx_real]['valor_necessario'] = novo_alvo_meta
                        metas_atuais[idx_real]['prazo']           = novo_prazo_meta
                        perfil['metas'] = metas_atuais
                salvar_perfil(perfil)
                st.session_state.msg_sucesso = f"✏️ Meta atualizada!"
                st.rerun()

    # ─ Eliminar ─
    with col_del_m:
        with st.popover("🗑️ Eliminar", use_container_width=True):
            if eh_reserva:
                st.info("🛡️ A Reserva de Emergência não pode ser eliminada — apenas editada.")
            else:
                st.warning(f"Tem certeza que deseja eliminar **'{meta_desc}'**?")
                if st.button("🗑️ Sim, eliminar", key="btn_del_meta", use_container_width=True):
                    idx_real = next(
                        (i for i, m in enumerate(metas_atuais)
                         if m.get('meta') == meta_sel.get('meta')
                         and 'reserva' not in str(m.get('meta', '')).lower()),
                        None
                    )
                    if idx_real is not None:
                        metas_atuais.pop(idx_real)
                        perfil['metas'] = metas_atuais
                        salvar_perfil(perfil)
                    st.session_state.msg_sucesso = f"🗑️ Meta '{meta_desc}' eliminada."
                    st.rerun()

    # ─ Adicionar nova meta ─
    st.markdown("---")
    with st.expander("➕ Adicionar Nova Meta", expanded=False):
        with st.form("form_nova_meta", clear_on_submit=True):
            nm_desc  = st.text_input("Descrição da meta", placeholder="Ex: Viagem à Europa, Notebook novo...")
            nm_alvo  = st.number_input("Valor para alcançar (R$)", min_value=1.0, step=100.0)
            nm_prazo = st.text_input("Prazo para alcançar", placeholder="Ex: 2027-12")
            if st.form_submit_button("🎯 Salvar Meta", use_container_width=True):
                if not nm_desc:
                    st.warning("Preencha a descrição da meta.")
                elif nm_alvo <= 0:
                    st.warning("O valor objetivo deve ser maior que zero.")
                else:
                    nova_meta = {
                        "meta": nm_desc,
                        "valor_necessario": nm_alvo,
                        "valor_atual": 0.0,
                        "prazo": nm_prazo
                    }
                    metas_atuais.append(nova_meta)
                    perfil['metas'] = metas_atuais
                    salvar_perfil(perfil)
                    st.session_state.msg_sucesso = f"🎯 Meta '{nm_desc}' adicionada com sucesso!"
                    st.rerun()

    # ── PERFIL DO USUÁRIO ──
    st.divider()
    with st.expander("👤 Meu Perfil", expanded=False):

        from datetime import date
        # Calcular idade a partir da data de nascimento
        nascimento_str = perfil.get('data_nascimento', '')
        idade_calc = perfil.get('idade', 0)
        try:
            if nascimento_str:
                dn = datetime.strptime(nascimento_str, "%Y-%m-%d").date()
                hoje_d = date.today()
                idade_calc = hoje_d.year - dn.year - ((hoje_d.month, hoje_d.day) < (dn.month, dn.day))
        except:
            pass

        with st.form("form_perfil_sidebar", clear_on_submit=False):
            p_nome = st.text_input("Nome", value=perfil.get('nome', ''), key="p_nome")
            p_nasc = st.text_input("Data de Nascimento (AAAA-MM-DD)", value=nascimento_str, placeholder="Ex: 1980-05-15", key="p_nasc")
            if nascimento_str:
                st.caption(f"🎂 Idade calculada automaticamente: **{idade_calc} anos**")
            p_profissao = st.text_input("Profissão", value=perfil.get('profissao', ''), key="p_prof")
            p_renda = st.number_input("Renda Mensal (R$)", value=float(perfil.get('renda_mensal', 0.0)), min_value=0.0, step=100.0, key="p_renda")
            p_perfil = st.selectbox("Perfil de Investidor", ["conservador", "moderado", "arrojado"],
                index=["conservador", "moderado", "arrojado"].index(perfil.get('perfil_investidor', 'moderado')) if perfil.get('perfil_investidor', 'moderado') in ["conservador", "moderado", "arrojado"] else 1,
                key="p_perf")
            p_objetivo = st.text_input("Objetivo Principal", value=perfil.get('objetivo_principal', ''), key="p_obj")
            p_patrimonio = st.number_input("Patrimônio Total (R$)", value=float(perfil.get('patrimonio_total', 0.0)), min_value=0.0, step=500.0, key="p_pat")

            if st.form_submit_button("💾 Salvar Perfil", use_container_width=True):
                # Calcular idade nova
                nova_idade = idade_calc
                try:
                    if p_nasc.strip():
                        dn2 = datetime.strptime(p_nasc.strip(), "%Y-%m-%d").date()
                        hoje_d2 = date.today()
                        nova_idade = hoje_d2.year - dn2.year - ((hoje_d2.month, hoje_d2.day) < (dn2.month, dn2.day))
                except:
                    st.error("⚠️ Formato de data inválido. Use AAAA-MM-DD (ex: 1980-05-15).")
                    st.stop()
                perfil.update({
                    'nome': p_nome,
                    'data_nascimento': p_nasc.strip(),
                    'idade': nova_idade,
                    'profissao': p_profissao,
                    'renda_mensal': p_renda,
                    'perfil_investidor': p_perfil,
                    'objetivo_principal': p_objetivo,
                    'patrimonio_total': p_patrimonio,
                })
                salvar_perfil(perfil)
                st.session_state.msg_sucesso = "✅ Perfil atualizado com sucesso!"
                st.rerun()

    # ── RESUMO FINANCEIRO ──────────────────────────────────────────────────
    st.divider()
    st.subheader("📈 Resumo Financeiro")

    # Tipos de agrupamento: gerado dinamicamente a partir dos tipos cadastrados
    # Exclui "entrada" pois são ingressos, não gastos/dívidas
    GRUPOS_RESUMO = []
    for chave, rotulo in st.session_state.tipos_labels.items():
        if chave == "entrada":
            continue
        # Extrair ícone do rótulo (primeiro caractere se for emoji) ou usar 📌
        partes = rotulo.split(" ", 1)
        icone = partes[0] if len(partes) > 1 else "📌"
        label = partes[1] if len(partes) > 1 else rotulo
        GRUPOS_RESUMO.append((chave, icone, label))

    # Pré-calcular saldo líquido das dívidas (original - pagamentos já efetuados)
    def saldo_liquido_divida(tipo_divida_key):
        """Retorna o valor restante da dívida: registros de dívida - pagamentos já feitos."""
        # Total registrado como dívida (todos os meses, valor original)
        total_divida = df_transacoes[
            df_transacoes['tipo'].str.lower() == tipo_divida_key.lower()
        ]['valor'].sum()
        # Total já pago (saídas cujo tipo foi reduzido via pagar_divida — o valor na linha JÁ foi subtraído)
        # Como pagar_divida subtrai direto no registro, o valor atual da linha JÁ é o saldo restante.
        saldo = total_divida  # já é o valor líquido (pagar_divida subtrai in-place)
        return max(saldo, 0.0)

    # Mês completo para o resumo
    df_resumo_mes = df_transacoes[df_transacoes['mes_ano'] == mes_selecionado].copy()

    for tipo_key, icone, label_default in GRUPOS_RESUMO:
        # Label customizável (salvo no session_state)
        label_atual = st.session_state.tipos_labels.get(tipo_key, label_default)

        # Filtra linhas deste tipo
        if tipo_key in ("Divida Banco", "Divida Loja"):
            # Para dívidas: usa o valor ATUAL do registro (já descontado por pagar_divida)
            # Mostra saldo líquido acumulado em TODOS os meses (dívida não some ao mudar de mês)
            mask_all = df_transacoes['tipo'].str.lower() == tipo_key.lower()
            df_grupo_all = df_transacoes[mask_all]
            total_grupo = max(df_grupo_all['valor'].sum(), 0.0)
            # Para detalhe do mês selecionado
            mask = df_resumo_mes['tipo'].str.lower() == tipo_key.lower()
            df_grupo = df_resumo_mes[mask]
        else:
            mask = df_resumo_mes['tipo'] == tipo_key
            df_grupo = df_resumo_mes[mask]
            total_grupo = df_grupo['valor'].sum()

        # Badge de status para dívidas e gastos recorrentes
        if tipo_key in ("Divida Banco", "Divida Loja"):
            status_badge = "✅ QUITADA" if total_grupo <= 0 else f"Saldo: R$ {total_grupo:.2f}"
            titulo_expander = f"{icone} **{label_atual}** — {status_badge}"
        elif tipo_key == 'saida mensal':
            # Contar pendentes vs efetuados no mês
            df_rec_all = df_transacoes[df_transacoes['tipo'] == 'saida mensal'].copy()
            if not df_rec_all.empty:
                nomes_recorrentes = df_rec_all.drop_duplicates(subset=['descricao', 'categoria'])[['descricao', 'categoria']]
                n_total = len(nomes_recorrentes)
                n_pagos = sum(
                    1 for _, r in nomes_recorrentes.iterrows()
                    if not df_grupo[(df_grupo['descricao'] == r['descricao']) & (df_grupo['categoria'] == r['categoria'])].empty
                )
                n_pendentes = n_total - n_pagos
                badge_rec = f"🔴 {n_pendentes} Pendente(s) · 🔵 {n_pagos} Efetuado(s)" if n_total > 0 else "Sem registros"
            else:
                badge_rec = "Sem registros"
            titulo_expander = f"{icone} **{label_atual}** — {badge_rec}"
        else:
            titulo_expander = f"{icone} **{label_atual}** — R$ {total_grupo:.2f}"

        with st.expander(titulo_expander, expanded=False):
            if tipo_key in ("Divida Banco", "Divida Loja"):
                # Exibe saldo restante com barra de progresso
                if total_grupo <= 0:
                    st.success("🎉 Dívida totalmente quitada!")
                else:
                    st.write(f"💳 **Saldo restante:** R$ {total_grupo:.2f}")
                    # Detalhe por item de dívida
                    st.markdown("**Itens pendentes:**")
                    for _, row in df_grupo_all[df_grupo_all['valor'] > 0].iterrows():
                        data_str = row['data'].strftime('%d/%m/%Y')
                        venc_str = ""
                        if 'dia_vencimento' in row.index and pd.notna(row.get('dia_vencimento')):
                            venc_str = f" | 📅 Dia {int(row['dia_vencimento'])}"
                        st.write(f"  • {data_str} - {row['descricao']} ({row['categoria']}): R$ {row['valor']:.2f}{venc_str}")
            elif tipo_key == 'saida mensal':
                st.markdown(f"**Mês: {mes_selecionado}**")
                df_recorrentes = df_transacoes[df_transacoes['tipo'] == 'saida mensal'].copy()
                if not df_recorrentes.empty:
                    gastos_rec_df = df_recorrentes.sort_values('data').drop_duplicates(subset=['descricao', 'categoria'], keep='last')
                    gastos_rec = gastos_rec_df.to_dict('records')
                else:
                    gastos_rec = []

                if not gastos_rec:
                    st.info("Nenhum lançamento recorrente configurado. Adicione um registro com tipo 'saida mensal'.")
                else:
                    hoje_dia = datetime.now().day
                    for i, g in enumerate(gastos_rec):
                        pagos_mes = df_grupo[
                            (df_grupo['descricao'] == g['descricao']) &
                            (df_grupo['categoria'] == g['categoria'])
                        ]
                        dia_v = int(g.get('dia_vencimento', 1)) if pd.notna(g.get('dia_vencimento')) else 1

                        col_info, col_btn = st.columns([3, 1])
                        with col_info:
                            if not pagos_mes.empty:
                                data_pag = pagos_mes.iloc[0]['data'].strftime('%d/%m/%Y')
                                st.markdown(
                                    f"🔵 **{g['descricao']}** &nbsp;|&nbsp; "
                                    f"R$ {g['valor']:.2f} &nbsp;|&nbsp; "
                                    f"📅 Dia {dia_v} &nbsp;|&nbsp; "
                                    f"<span style='color:#2196F3;font-weight:bold'>Pagamento Efetuado ✔ em {data_pag}</span>",
                                    unsafe_allow_html=True
                                )
                            else:
                                # Verifica urgência baseada no dia de vencimento
                                if hoje_dia > dia_v:
                                    aviso = f"⚠️ Vencido há {hoje_dia - dia_v} dia(s)!"
                                    cor = "#B71C1C"  # vermelho escuro
                                elif hoje_dia == dia_v:
                                    aviso = "⚠️ Vence HOJE!"
                                    cor = "#e53935"  # vermelho
                                elif dia_v - hoje_dia <= 3:
                                    faltam = dia_v - hoje_dia
                                    aviso = f"⏰ Vence em {faltam} dia(s)! Já separa o dinheiro!"
                                    cor = "#FF6F00"  # laranja urgente
                                else:
                                    faltam = dia_v - hoje_dia
                                    aviso = f"Faltam {faltam} dia(s)"
                                    cor = "#c62828"  # vermelho padrão pendente
                                
                                st.markdown(
                                    f"🔴 **{g['descricao']}** &nbsp;|&nbsp; "
                                    f"R$ {g['valor']:.2f} &nbsp;|&nbsp; "
                                    f"📅 Dia {dia_v} &nbsp;|&nbsp; "
                                    f"<span style='color:{cor};font-weight:bold'>Pagamento Pendente ⏳ — {aviso}</span>",
                                    unsafe_allow_html=True
                                )

                        with col_btn:
                            if pagos_mes.empty:
                                if st.button("💳 Pagar", key=f"pay_resumo_{i}_{mes_selecionado}", use_container_width=True):
                                    import calendar
                                    ano_sel, mes_sel = map(int, mes_selecionado.split("-"))
                                    hoje = datetime.now()
                                    if ano_sel == hoje.year and mes_sel == hoje.month:
                                        data_pagamento = hoje
                                    else:
                                        ultimo_dia = calendar.monthrange(ano_sel, mes_sel)[1]
                                        data_pagamento = datetime(ano_sel, mes_sel, min(dia_v, ultimo_dia))
                                    salvar_nova_transacao(
                                        data=data_pagamento,
                                        desc=g['descricao'],
                                        cat=g['categoria'],
                                        valor=g['valor'],
                                        tipo='saida mensal',
                                        dia_vencimento=dia_v
                                    )
                                    st.session_state.msg_sucesso = f"✅ {g['descricao']} pago em {data_pagamento.strftime('%d/%m/%Y')}!"
                                    st.rerun()
                            else:
                                st.markdown("<span style='color:#2196F3'>✔ Efetuado</span>", unsafe_allow_html=True)
                        st.divider()
            else:
                # Detalhe do mês selecionado
                st.markdown(f"**Mês: {mes_selecionado}**")
                if df_grupo.empty:
                    st.info("Nenhum lançamento neste mês.")
                else:
                    for _, row in df_grupo.iterrows():
                        data_str = row['data'].strftime('%d/%m/%Y')
                        venc_str = ""
                        if 'dia_vencimento' in row.index and pd.notna(row.get('dia_vencimento')):
                            venc_str = f" | 📅 Dia {int(row['dia_vencimento'])}"
                        st.write(f"  • {data_str} - {row['descricao']} ({row['categoria']}): R$ {row['valor']:.2f}{venc_str}")

                # Histórico de todos os meses
                st.markdown("---")
                st.markdown("📅 **Histórico Mensal**")
                for mes in sorted(df_transacoes['mes_ano'].dropna().unique()):
                    if mes == "NaT":
                        continue
                    df_m = df_transacoes[df_transacoes['mes_ano'] == mes]
                    mask_m = df_m['tipo'] == tipo_key

                    total_m = df_m[mask_m]['valor'].sum()
                    if total_m > 0:
                        st.write(f"  🗓️ {mes}: R$ {total_m:.2f}")

            # ── Editar nome do tipo ──
            st.markdown("---")
            novo_label = st.text_input(
                "✏️ Renomear este tipo",
                value=label_atual,
                key=f"label_{tipo_key}"
            )
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 Salvar", key=f"save_{tipo_key}"):
                    renomear_tipo(tipo_key, novo_label)
                    st.session_state.tipos_labels = carregar_tipos()
                    st.rerun()

    # ── Alteração do Tipo de Transação ──
    with st.expander("⚙️ Alteração do Tipo de Transação"):
        tab_add, tab_edit, tab_del = st.tabs(["➕ Adicionar", "✏️ Editar", "🗑️ Eliminar"])

        with tab_add:
            with st.form("novo_tipo_form", clear_on_submit=True):
                novo_tipo_label = st.text_input("Rótulo de exibição (ex: Dívida Financeira)")
                if st.form_submit_button("➕ Adicionar Tipo"):
                    if novo_tipo_label:
                        # Gera chave interna automaticamente
                        import re
                        chave_auto = re.sub(r'[^\w\s]', '', novo_tipo_label).strip().replace(' ', '_').lower()
                        # Garantir que não seja duplicada
                        if chave_auto in st.session_state.tipos_labels:
                            st.warning(f"⚠️ Já existe um tipo com essa chave: '{chave_auto}'.")
                        else:
                            adicionar_tipo(chave_auto, f"📌 {novo_tipo_label}")
                            st.session_state.tipos_labels = carregar_tipos()
                            st.session_state.msg_sucesso = f"✅ Tipo '{novo_tipo_label}' adicionado!"
                            st.rerun()
                    else:
                        st.warning("Preencha o rótulo.")

        with tab_edit:
            tipos_editaveis = list(st.session_state.tipos_labels.keys())
            if tipos_editaveis:
                tipo_para_editar = st.selectbox("Selecione o tipo:", tipos_editaveis,
                    format_func=lambda k: st.session_state.tipos_labels[k],
                    key="edit_tipo_sel"
                )
                with st.form("editar_tipo_form", clear_on_submit=True):
                    label_editado = st.text_input("Novo rótulo", value=st.session_state.tipos_labels[tipo_para_editar])
                    if st.form_submit_button("💾 Salvar Alteração"):
                        renomear_tipo(tipo_para_editar, label_editado)
                        st.session_state.tipos_labels = carregar_tipos()
                        st.session_state.msg_sucesso = f"✏️ Tipo renomeado para '{label_editado}'!"
                        st.rerun()
            else:
                st.info("Nenhum tipo disponível para editar.")

        with tab_del:
            # Só mostrar tipos que NÃO têm registros associados
            tipos_sem_registros = []
            for k, v in st.session_state.tipos_labels.items():
                # Verificar se existem registros com esse tipo
                n_registros = len(df_transacoes[df_transacoes['tipo'].str.lower() == k.lower()])
                if n_registros == 0:
                    tipos_sem_registros.append(k)

            if tipos_sem_registros:
                tipo_del = st.selectbox("Tipo a eliminar (sem registros):", tipos_sem_registros,
                    format_func=lambda k: f"{st.session_state.tipos_labels[k]} (0 registros)",
                    key="del_tipo_sel"
                )
                if st.button("🗑️ Confirmar Exclusão"):
                    remover_tipo(tipo_del)
                    st.session_state.tipos_labels = carregar_tipos()
                    st.session_state.msg_sucesso = f"🗑️ Tipo excluído com sucesso!"
                    st.rerun()
            else:
                st.info("Todos os tipos têm registros associados. Não é possível eliminar nenhum.")

    # ── Exportar Planilha ──
    st.divider()
    st.markdown("**📥 Exportar Relatório**")
    import io
    buffer = io.BytesIO()
    # Preparar dados com dia_vencimento formatada para Excel
    df_export = df_transacoes.copy()
    if 'dia_vencimento' in df_export.columns:
        df_export['dia_vencimento'] = df_export['dia_vencimento'].apply(
            lambda x: f"Dia {int(x)}" if pd.notna(x) else ''
        )
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Transacoes', index=False)
        resumo_df = pd.DataFrame(resumo_financeiro)
        if not resumo_df.empty:
            resumo_df.to_excel(writer, sheet_name='Resumo_Mes', index=False)
    st.download_button(
        label="📊 Baixar Planilha (Excel)",
        data=buffer.getvalue(),
        file_name=f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # ── Exportar PDF Profissional ──
    exibir_botao_download_pdf(
        df_transacoes=df_transacoes,
        perfil=perfil,
        mes_selecionado=mes_selecionado,
        saldo_do_mes=saldo_do_mes,
        entradas_mes=entradas_mes,
        saidas_mes=saidas_mes,
        saldo_total=saldo_total,
        total_dividas=total_dividas,
        reserva_atual=reserva_atual,
        logo_path=logo_path,
    )

    st.divider()

    # ── OPERAÇÕES DE REGISTROS ──
    st.subheader("📋 Alterações de Registros")

    with st.expander("➕ Adicionar Registro"):
        categorias_existentes = sorted(df_transacoes['categoria'].unique().tolist())

        # Construir lista de tipos SEMPRE a partir do session_state atual
        # A chave do selectbox inclui o tamanho da lista para forçar rerender quando um tipo é adicionado
        _tipos_base = ["entrada", "saida", "saida mensal"]
        _tipos_custom = [k for k in st.session_state.tipos_labels.keys() if k not in _tipos_base]
        tipos_disponiveis = _tipos_base + _tipos_custom
        _tipos_key = f"tipo_sel_{len(tipos_disponiveis)}"  # muda quando novos tipos são adicionados

        with st.form("nova_transacao", clear_on_submit=True):
            nova_data = st.date_input("Data", datetime.now())
            nova_desc = st.text_input("Descrição")
            col1, col2 = st.columns(2)
            with col1:
                cat_sel = st.selectbox("Categoria Existente", ["Nova..."] + categorias_existentes)
            with col2:
                cat_nova = st.text_input("Ou Digite Nova")
            nova_cat = cat_nova if cat_nova else cat_sel
            novo_valor = st.number_input("Valor", min_value=0.0, step=0.01)
            novo_tipo = st.selectbox("Tipo", tipos_disponiveis, key=_tipos_key)
            st.caption(f"📂 {len(tipos_disponiveis)} tipos disponíveis")
            tem_vencimento = st.checkbox("📅 Tem dia de vencimento fixo no mês?")
            novo_dia_venc = st.number_input("Dia do Vencimento", min_value=1, max_value=31, value=15, step=1, key="venc_add")

            if st.form_submit_button("Salvar e Atualizar"):
                if nova_cat == "Nova..." and not cat_nova:
                    st.warning("Selecione ou digite uma categoria.")
                else:
                    dia_venc_final = novo_dia_venc if tem_vencimento else None
                    df_transacoes = salvar_nova_transacao(nova_data, nova_desc, nova_cat, novo_valor, novo_tipo, data_vencimento=None, dia_vencimento=dia_venc_final)
                    st.session_state.msg_sucesso = "✅ Atualização realizada com sucesso!"
                    st.rerun()

    with st.expander("📝 Editar Registro"):
        if not df_mes.empty:
            idx_mod = st.selectbox(
                "Item:", df_mes.index,
                format_func=lambda x: f"{df_mes.loc[x, 'descricao']}  —  R$ {df_mes.loc[x, 'valor']:.2f}" + (
                    f" | Dia {int(df_mes.loc[x, 'dia_vencimento'])}" 
                    if 'dia_vencimento' in df_mes.columns and pd.notna(df_mes.loc[x, 'dia_vencimento']) else ""
                ),
                key=f"m_{st.session_state.form_version}"
            )
            with st.form("form_edit", clear_on_submit=True):
                n_desc = st.text_input("Nova Descrição", value=df_mes.loc[idx_mod, 'descricao'])
                n_val = st.number_input("Novo Valor", value=float(df_mes.loc[idx_mod, 'valor']))
                
                tipo_atual = df_mes.loc[idx_mod, 'tipo']
                idx_tipo_atual = tipos_disponiveis.index(tipo_atual) if tipo_atual in tipos_disponiveis else 0
                n_tipo = st.selectbox("Novo Tipo", tipos_disponiveis, index=idx_tipo_atual, key=f"tipo_edit_{st.session_state.form_version}")
                
                venc_atual = df_mes.loc[idx_mod, 'dia_vencimento'] if 'dia_vencimento' in df_mes.columns else None
                tem_venc_atual = pd.notna(venc_atual)
                st.markdown("---")
                n_tem_venc = st.checkbox("📅 Tem dia de vencimento fixo no mês?", value=tem_venc_atual)
                venc_default = int(venc_atual) if tem_venc_atual else 15
                n_dia_venc = st.number_input("Dia do Vencimento", min_value=1, max_value=31, value=venc_default, key="venc_edit")

                if st.form_submit_button("Atualizar"):
                    import agente
                    db_id = int(df_mes.loc[idx_mod, 'id'])
                    dia_venc_edit = n_dia_venc if n_tem_venc else None
                    agente.atualizar_transacao(db_id, n_desc, n_val, nova_data_vencimento=None, novo_tipo=n_tipo, novo_dia_vencimento=dia_venc_edit)
                    st.session_state.msg_sucesso = "📝 Alteração realizada!"
                    st.session_state.form_version += 1
                    st.rerun()
        else:
            st.info("Nenhum registro neste mês.")
            
        st.divider()
        st.info("💡 Para depositar na Reserva de Emergência, use o botão no menu lateral.")

    with st.expander("🗑️ Remover Registro"):
        if not df_mes.empty:
            idx_del = st.selectbox(
                "Item:", df_mes.index,
                format_func=lambda x: f"{df_mes.loc[x, 'descricao']}  —  R$ {df_mes.loc[x, 'valor']:.2f}" + (
                    f" | Dia {int(df_mes.loc[x, 'dia_vencimento'])}" 
                    if 'dia_vencimento' in df_mes.columns and pd.notna(df_mes.loc[x, 'dia_vencimento']) else ""
                ),
                key=f"d_{st.session_state.form_version}"
            )
               # ── PAGAMENTOS ──────────────────────────────────────────────────
    with st.expander("💸 Pagamentos"):
        st.markdown("**Selecione o tipo de transação:**")

        # Construir dinamicamente a partir dos tipos que têm registros com valor > 0
        _df_pend = df_transacoes[df_transacoes['valor'] > 0].copy()
        _tipos_com_saldo = sorted(_df_pend['tipo'].dropna().unique().tolist())

        # Excluir tipos de ingresso puro ('entrada') pois não fazem sentido em pagamentos
        _tipos_pagamento = [t for t in _tipos_com_saldo if t.lower() not in ('entrada',)]

        if not _tipos_pagamento:
            st.info("Nenhum registro com saldo pendente encontrado.")
        else:
            # Obter rótulo amigável do tipo (usa tipos_labels se existir, senão usa a própria chave)
            def _rotulo_tipo(t):
                return st.session_state.tipos_labels.get(t, t.capitalize())

            tipo_pag_sel = st.selectbox(
                "Tipo de Transação",
                _tipos_pagamento,
                format_func=_rotulo_tipo,
                key=f"tipo_pag_sel_{len(_tipos_pagamento)}"
            )

            # Filtrar registros do tipo selecionado com valor > 0
            df_cat_positivo = _df_pend[_df_pend['tipo'] == tipo_pag_sel]

            if df_cat_positivo.empty:
                st.info(f"Nenhum débito pendente em '{_rotulo_tipo(tipo_pag_sel)}'.")
            else:
                opcoes_pag = df_cat_positivo.apply(
                    lambda r: (
                        f"{r['descricao']} — R$ {r['valor']:.2f}"
                        + (f" | 📅 Dia {int(r['dia_vencimento'])}"
                           if 'dia_vencimento' in r.index and pd.notna(r.get('dia_vencimento')) else "")
                    ), axis=1
                ).tolist()

                idx_pag = st.selectbox(
                    "Item para pagar:",
                    range(len(opcoes_pag)),
                    format_func=lambda i: opcoes_pag[i],
                    key=f"sel_pag_item_{tipo_pag_sel}"
                )

                row_pag = df_cat_positivo.iloc[idx_pag]
                valor_disponivel = float(row_pag['valor'])

                st.write(f"💰 **Valor pendente:** R$ {valor_disponivel:.2f}")
                valor_pagar = st.number_input(
                    "Valor a pagar (R$)",
                    min_value=0.01,
                    max_value=valor_disponivel,
                    step=0.01,
                    key=f"val_pagar_{tipo_pag_sel}"
                )

                if st.button("✅ Confirmar Pagamento", key="btn_confirmar_pag"):
                    import agente
                    db_id = int(row_pag['id'])
                    tipo_pag = row_pag['tipo']
                    cat_pag = row_pag['categoria']

                    # Reduzir o valor da dívida no registro original
                    agente.pagar_divida(db_id, valor_pagar)

                    # Registrar saída (atualiza o saldo automaticamente)
                    salvar_nova_transacao(
                        datetime.now(),
                        f"Pagamento: {row_pag['descricao']}",
                        cat_pag,
                        valor_pagar,
                        "saida"
                    )
                    st.session_state.msg_sucesso = (
                        f"✅ Pagamento de R$ {valor_pagar:.2f} em '{_rotulo_tipo(tipo_pag_sel)}' registrado! "
                        f"Saldo atualizado."
                    )
                    st.rerun()

    #===========GLOSSARIO============
    st.divider()
    st.subheader("📚 Glossário")
    for termo in edu['conteudo']['investimentos']['termos']:
        with st.expander(f"{termo['sigla']}"):
            st.write(termo['descricao'])

    #===========CONFIGURAÇÕES============
    st.divider()
    st.subheader("⚙️ Configurações")
    with st.expander("🔑 Alterar Senha"):
        with st.form("form_senha", clear_on_submit=True):
            nova_senha = st.text_input("Nova Senha", type="password")
            confirmar_senha = st.text_input("Confirmar Nova Senha", type="password")
            if st.form_submit_button("Salvar Nova Senha"):
                if nova_senha and nova_senha == confirmar_senha:
                    try:
                        with open(config.AUTH_FILE, "w") as f:
                            json.dump({"pwd_hash": config.hash_password(nova_senha)}, f)
                        st.session_state.msg_sucesso = "✅ Senha atualizada com sucesso!"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar senha: {e}")
                else:
                    st.error("As senhas não coincidem ou estão vazias.")

# --- 5. CHAT LUMMI ---
st.subheader("💬 Assistente LUMMI")

# Botão para ver histórico de dias anteriores
with st.expander("📂 Ver Histórico de Atendimentos Anteriores", expanded=False):
    try:
        db_h = get_session()
        _hoje_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        hist_anterior = db_h.query(ChatHistory).filter(
            ChatHistory.data_hora < _hoje_inicio
        ).order_by(ChatHistory.data_hora.desc()).all()
        db_h.close()

        if not hist_anterior:
            st.info("Nenhum atendimento anterior encontrado.")
        else:
            # Agrupar por data
            from collections import defaultdict
            por_dia = defaultdict(list)
            for h in hist_anterior:
                dia = h.data_hora.strftime("%d/%m/%Y")
                por_dia[dia].append(h)

            for dia, msgs in sorted(por_dia.items(), reverse=True):
                with st.expander(f"📅 Conversa de {dia} ({len(msgs)} mensagens)", expanded=False):
                    for h in reversed(msgs):
                        icon = "🧑" if h.role == "user" else "🤖"
                        st.markdown(f"**{icon} {h.role.capitalize()}** &nbsp; `{h.data_hora.strftime('%H:%M')}`")
                        st.markdown(h.content)
                        st.divider()
    except Exception as e:
        st.warning(f"Não foi possível carregar o histórico: {e}")

# Boas-vindas diárias (apenas se a conversa de hoje estiver vazia)
if not st.session_state.messages:
    nome_usuario = perfil.get('nome', 'Usuário')
    saludo = (
        f"Oi, {nome_usuario}! 🌟 Sou o LUMMI, seu assistente de Inteligência Financeira. "
        f"Pronto para um novo dia de conquistas! Em que posso te ajudar hoje? 🚀"
    )
    st.session_state.messages.append({"role": "assistant", "content": saludo})
    try:
        db = get_session()
        db.add(ChatHistory(role="assistant", content=saludo))
        db.commit()
        db.close()
    except:
        pass

# Exibir mensagens do dia atual
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "skill" in msg and msg["skill"]:
            if msg["skill"] == "metas":
                exibir_rastreador_metas(perfil)
            elif msg["skill"] == "diagnostico":
                exibir_diagnostico_financeiro(perfil, saidas_mes)
            elif msg["skill"] == "simulador":
                exibir_simulador_investimentos(perfil, edu, suffix_id=str(i))
            elif msg["skill"] == "motivacao":
                exibir_motivacao(perfil)
            elif msg["skill"] == "vencimentos":
                exibir_alertas_vencimento(df_transacoes)

if prompt := st.chat_input("Pergunte algo ao LUMMI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        db = get_session()
        db.add(ChatHistory(role="user", content=prompt))
        db.commit()
        db.close()
    except:
        pass

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("LUMMI analisando..."):
            p_lower = prompt.lower()
            skill_detectada = None
            if any(w in p_lower for w in ["meta", "metas", "objetivo", "rastreador"]):
                skill_detectada = "metas"
            elif any(w in p_lower for w in ["simular", "simulação", "simulador", "investir", "rendimento"]):
                skill_detectada = "simulador"
            elif any(w in p_lower for w in ["orçamento", "diagnóstico", "alerta", "gasto", "saída", "saida"]):
                skill_detectada = "diagnostico"
            elif any(w in p_lower for w in ["motiva", "desanimad", "difícil", "triste", "ajuda", "dica", "inspir"]):
                skill_detectada = "motivacao"
            elif any(w in p_lower for w in ["vencimento", "fatura", "pagar", "lembrete"]):
                skill_detectada = "vencimentos"
            elif any(w in p_lower for w in ["indicador", "selic", "poupança", "poupanca", "inflação", "inflacao", "ipca", "igpm", "taxa"]):
                skill_detectada = "indicadores"
                
            try:
                # Preparar datos para el prompt (evitar problemas con {} en f-strings)
                conteudo = edu.get('conteudo', {})
                termos_investimentos = conteudo.get('investimentos', {}).get('termos', [])
                alertas_educacionais = conteudo.get('alertas_educacionais', {})

                # Formatear histórico como texto legible
                historico_texto = df_mes[['data', 'descricao', 'categoria', 'valor', 'tipo']].to_string(index=False)
                
                # Fetch indicadores if needed
                dados_mercado_str = ""
                palavras_mercado = [
                    "selic", "poupança", "poupanca", "ipca", "igpm", "igp-m",
                    "dólar", "dolar", "euro", "câmbio", "cambio", "cotação", "cotacao",
                    "taxa", "juros", "taxa de juros", "rendimento", "mercado",
                    "inflação", "inflacao", "rende", "quanto rende"
                ]
                if skill_detectada == "indicadores" or any(w in p_lower for w in palavras_mercado):
                    from skills import consultar_indicadores_economicos_br
                    indicadores = consultar_indicadores_economicos_br()
                    dados_mercado_str = f"\n\n4. DADOS REAIS DE MERCADO (HOJE):\nO usuário perguntou sobre o mercado. Use EXATAMENTE os dados oficiais do Banco Central abaixo para responder.\n{json.dumps(indicadores, ensure_ascii=False)}\nNunca invente as taxas. Use os números exatos fornecidos."

                # System Prompt
                SYSTEM_PROMPT = f"""
                Você é o LUMMI, o assistente financeiro de {perfil.get('nome', 'Usuário')}.

                1. DADOS DO MÊS SELECIONADO ({mes_selecionado}):
                - Saldo Atual: R$ {saldo_do_mes:.2f}
                - Resumo Completo (Tipo/Categoria): {json.dumps(resumo_financeiro, ensure_ascii=False)}
                - Histórico Detalhado:
                {historico_texto}

                2. MATERIAL EDUCATIVO (JSON):
                {json.dumps(termos_investimentos, ensure_ascii=False)}

                3. ALERTAS EDUCATIVOS:
                {json.dumps(alertas_educacionais, ensure_ascii=False)}{dados_mercado_str}

                ### PERFIL DO USUÁRIO (CONTEXTO ATUAL)
                - Nome: {perfil.get('nome', 'Usuário')}
                - Profissão: {perfil.get('profissao', 'Não informada')}
                - Renda Mensal: R$ {perfil.get('renda_mensal', 0.0):.2f}
                - Perfil: {perfil.get('perfil_investidor', 'Não definido')}
                - Reserva de Emergência Atual: R$ {perfil.get('reserva_emergencia_atual', 0.0):.2f}
                - Metas: {json.dumps(perfil.get('metas', []), ensure_ascii=False)}

                REGRAS OBRIGATÓRIAS (COMPORTAMENTO E TOM DE VOZ):
                - PERSONALIDADE: Seja extremamente amigável, divertido, sempre respeitoso e altamente motivador! Você não é apenas um sistema de contabilidade, é um treinador financeiro entusiasmado.
                - HUMOR E EMPATIA: Use emojis, faça elogios sinceros pelas pequenas vitórias (como registrar um gasto ou perguntar sobre investimentos), e encoraje muito quando houver frustração.
                - NUNCA julgue ou dê bronca se as contas estiverem ruins. Pelo contrário, mostre que o primeiro passo já foi dado e que tudo tem solução.
                - SAUDAÇÃO: Ao início de CADA resposta, receba o usuário com alegria: "Oi, {perfil.get('nome', 'Usuário')}!! 🌟"
                - SÍNTESE E CLAREZA: Responda de forma sucinta e direta (máx 10 parágrafos curtos). Explique termos de forma didática e simples.
                - FOCO: Priorize 1) Quitar dívidas, 2) Construir reserva (6x a renda mensal), 3) Investir. Sempre termine com próximos passos práticos!
                - LIMITES: Nunca recomende ativos de alto risco (ex: Criptomoedas, Ações Específicas). Se pedirem dicas diretas de onde investir, diga: "Oi, Reyna! 😃 Como seu parceiro de finanças, meu papel é te ajudar a entender as opções — não escolher um investimento específico por você. Vamos ver juntos o que faz mais sentido para o seu perfil!"* — O agente não faz indicação direta, mas explica as opções compatíveis com o perfil do cliente.
                - USE o material educativo para embasar suas falas e nunca invente dados. Use exemplos em reais (R$).
                - GROUNDING OBRIGATÓRIO (REGRA DE OURO): Quando o usuário perguntar sobre taxas financeiras, rendimentos ou cotações de moedas (ex: "quanto rende a poupança", "qual é a SELIC hoje", "cotação do dólar", "taxa de juros", "IPCA", "IGP-M", "euro"), você OBRIGATORIAMENTE deve usar SOMENTE os dados reais injetados na seção "DADOS REAIS DE MERCADO (HOJE)" deste prompt, buscados em tempo real da API oficial do Banco Central do Brasil e da AwesomeAPI. É TERMINANTEMENTE PROIBIDO inventar, estimar ou usar valores de memória para taxas e cotações. Se os dados de mercado não estiverem disponíveis no contexto, informe o usuário que não foi possível obter os dados em tempo real neste momento e oriente-o a consultar o site do Banco Central (bcb.gov.br).
                """

                mensagens_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
                modelos = [
                    MODELO,                                    # nvidia/nemotron-3-super-120b (principal)
                    "nvidia/nemotron-3-nano-30b-a3b:free",     # fallback gratuito menor/mais rápido
                ]
                
                dados_resposta = None
                modelo_usado = None
                for modelo in modelos:
                    for tentativa in range(2):  # 2 tentativas por modelo
                        response = requests.post(
                            url="https://openrouter.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                            json={"model": modelo, "messages": mensagens_api},
                            timeout=60
                        )
                        dados_resposta = response.json()
                        if "choices" in dados_resposta:
                            modelo_usado = modelo
                            break
                        # Si es 429 (rate limit), esperar antes de reintentar
                        if response.status_code == 429 and tentativa == 0:
                            time.sleep(10)
                            continue
                        break  # Otro error, probar siguiente modelo
                    if modelo_usado:
                        break

                if dados_resposta and "choices" in dados_resposta:
                    res_ia = dados_resposta['choices'][0]['message']['content']
                    st.markdown(res_ia)
                    
                    novo_msg = {"role": "assistant", "content": res_ia}
                    if skill_detectada:
                        novo_msg["skill"] = skill_detectada
                        if skill_detectada == "metas":
                            exibir_rastreador_metas(perfil)
                        elif skill_detectada == "diagnostico":
                            exibir_diagnostico_financeiro(perfil, saidas_mes)
                        elif skill_detectada == "simulador":
                            idx = len(st.session_state.messages)
                            exibir_simulador_investimentos(perfil, edu, suffix_id=str(idx))
                        elif skill_detectada == "motivacao":
                            exibir_motivacao(perfil)
                        elif skill_detectada == "vencimentos":
                            exibir_alertas_vencimento(df_transacoes)

                    st.session_state.messages.append(novo_msg)
                    try:
                        db = get_session()
                        db.add(ChatHistory(role="assistant", content=res_ia, skill=skill_detectada))
                        db.commit()
                        db.close()
                    except:
                        pass
                    
                    if modelo_usado != MODELO:
                        st.caption(f"ℹ️ Resposta via modelo alternativo: {modelo_usado}")
                else:
                    erro_api = dados_resposta.get("error", {}) if dados_resposta else {}
                    msg_erro = erro_api.get("message", "Erro desconhecido")
                    codigo = erro_api.get("code", getattr(response, 'status_code', '?'))
                    if codigo == 429:
                        st.warning("⏳ Limite de uso atingido (rate limit). Aguarde 1-2 minutos e tente novamente.")
                    else:
                        st.error(f"⚠️ Erro da API ({codigo}): {msg_erro}")
            except requests.exceptions.Timeout:
                st.error("⏳ A API demorou demais para responder. Tente novamente.")
            except Exception as e:
                st.error(f"Ops! Erro: {type(e).__name__}: {e}")