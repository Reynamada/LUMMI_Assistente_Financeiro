import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import os

def exibir_rastreador_metas(perfil):
    with st.expander("🎯 Rastreador de Metas", expanded=True):
        metas = perfil.get('metas', [])
        reserva_atual = perfil.get('reserva_emergencia_atual', 0.0)
        
        if metas:
            for m in metas:
                nome_meta = m.get('meta', 'Meta')
                valor_nec = m.get('valor_necessario', 1.0)
                
                if "reserva" in nome_meta.lower():
                    progresso = min(reserva_atual / valor_nec, 1.0)
                    st.write(f"🛡️ **{nome_meta}**")
                    st.write(f"R$ {reserva_atual:.2f} / R$ {valor_nec:.2f}")
                else:
                    patrimonio = perfil.get('patrimonio_total', 0.0)
                    progresso = min(patrimonio / valor_nec, 1.0)
                    st.write(f"🎯 **{nome_meta}**")
                    st.write(f"R$ {patrimonio:.2f} / R$ {valor_nec:.2f}")
                    
                st.progress(progresso)
                st.caption(f"Prazo: {m.get('prazo', 'N/A')}")
                st.markdown("---")
        else:
            st.info("Nenhuma meta definida no seu perfil.")

def exibir_diagnostico_financeiro(perfil, saidas_mes):
    with st.expander("⚠️ Diagnóstico Financeiro", expanded=True):
        renda = perfil.get('renda_mensal', 0.0)
        if renda > 0:
            pct_gasto = (saidas_mes / renda) * 100
            st.write(f"**Renda Mensal:** R$ {renda:.2f}")
            st.write(f"**Saídas do Mês:** R$ {saidas_mes:.2f}")
            st.progress(min(pct_gasto / 100.0, 1.0))
            if pct_gasto > 90:
                st.error(f"🚨 Alerta: Seus gastos atingiram {pct_gasto:.1f}% da sua renda! Risco de endividamento.")
            elif pct_gasto > 70:
                st.warning(f"⚠️ Atenção: Seus gastos estão em {pct_gasto:.1f}% da sua renda. Reveja o orçamento.")
            else:
                st.success(f"✅ Orçamento saudável! Seus gastos representam {pct_gasto:.1f}% da sua renda.")
        else:
            st.info("Informe sua renda mensal no perfil para ativar os alertas de orçamento.")

def exibir_simulador_investimentos(perfil, edu, suffix_id=""):
    with st.expander("📈 Simulador de Investimentos", expanded=True):
        st.write("Calcule quanto seu dinheiro pode render (Estimativa Didática).")
        perfil_risco = perfil.get('perfil_investidor', 'Conservador').lower()
        st.write(f"Seu Perfil de Risco: **{perfil_risco.capitalize()}**")
        
        # Usa sufixos unicos caso a funcao seja chamada mais de uma vez no chat
        valor_simulacao = st.number_input("Valor a investir (R$)", min_value=10.0, step=50.0, value=1000.0, key=f"val_sim_{suffix_id}")
        prazo_meses = st.slider("Prazo (meses)", min_value=1, max_value=60, value=12, key=f"prz_sim_{suffix_id}")
        
        if st.button("Simular Opções", key=f"btn_sim_{suffix_id}"):
            catalogo = edu.get('conteudo', {}).get('catalogo_produtos', {}).get('produtos', [])
            
            produtos_recomendados = []
            for p in catalogo:
                r = p.get('risco', '').lower()
                if perfil_risco == 'conservador' and r == 'baixo':
                    produtos_recomendados.append(p)
                elif perfil_risco == 'moderado' and r in ['baixo', 'médio', 'médio a alto']:
                    produtos_recomendados.append(p)
                elif perfil_risco == 'arrojado':
                    produtos_recomendados.append(p)
            
            vistos = set()
            unicos = []
            for p in produtos_recomendados:
                if p['nome'] not in vistos:
                    vistos.add(p['nome'])
                    unicos.append(p)
            
            if unicos:
                st.success(f"Top recomendações para o seu perfil:")
                for prod in unicos[:2]:
                    with st.container(border=True):
                        st.markdown(f"**{prod['nome']}**")
                        st.caption(f"Risco: {prod['risco'].capitalize()} | Aporte Mínimo: R$ {prod.get('aporte_minimo', 0)}")
                        
                        taxa_mensal = 0.0085 # ~10.6% a.a. padrao
                        if prod.get('risco', '') == 'alto':
                            taxa_mensal = 0.012 # ~15% a.a estimativa
                        elif prod.get('risco', '') == 'médio':
                            taxa_mensal = 0.01
                            
                        montante = valor_simulacao * ((1 + taxa_mensal) ** prazo_meses)
                        rendimento_bruto = montante - valor_simulacao
                        st.write(f"Projeção em {prazo_meses} meses:")
                        st.metric(label="Valor Bruto Estimado", value=f"R$ {montante:.2f}", delta=f"+R$ {rendimento_bruto:.2f}")
            else:
                st.warning("Não encontramos produtos específicos.")

def exibir_motivacao(perfil):
    nome = perfil.get('nome', 'Usuário')
    with st.container(border=True):
        st.markdown(f"### ✨ Vai dar tudo certo, {nome}!")
        st.write("A jornada financeira é como uma maratona, não uma corrida de 100 metros. Cada pequeno passo (como guardar R$ 10 ou registrar um gasto) é uma **vitória enorme**! 🚀")
        st.info("💡 **Dica do LUMMI:** Olhe para o que você já conquistou até aqui. Você tem o poder de mudar sua realidade financeira, um dia de cada vez. Estou aqui com você para o que der e vier! 💙")

def exibir_alertas_vencimento(df_transacoes):
    with st.expander("📅 Alertas de Vencimentos", expanded=True):
        hoje = datetime.now().date()
        mes_atual = hoje.strftime("%Y-%m")
        
        # 1. Obter faturas cadastradas (dívidas comuns que têm vencimento)
        if 'dia_vencimento' in df_transacoes.columns:
            df_faturas = df_transacoes[
                (df_transacoes['dia_vencimento'].notna()) & 
                (df_transacoes['valor'] > 0) &
                (df_transacoes['tipo'].str.contains("Divida", case=False, na=False))
            ].copy()
        else:
            df_faturas = pd.DataFrame()

        # 2. Obter gastos recorrentes pendentes no mês atual
        df_recorrentes = df_transacoes[df_transacoes['tipo'] == 'saida mensal'].copy() if not df_transacoes.empty and 'tipo' in df_transacoes.columns else pd.DataFrame()
        
        if not df_recorrentes.empty:
            gastos_rec_df = df_recorrentes.sort_values('data').drop_duplicates(subset=['descricao', 'categoria'], keep='last')
            gastos_rec = gastos_rec_df.to_dict('records')
        else:
            gastos_rec = []
            
        pendentes_rec = []
        
        # Para verificar pagamento no mês atual
        if not df_transacoes.empty and 'data' in df_transacoes.columns:
            # Garantir formato de data
            if not pd.api.types.is_datetime64_any_dtype(df_transacoes['data']):
                df_transacoes['data'] = pd.to_datetime(df_transacoes['data'], errors='coerce')
            df_mes_atual = df_transacoes[df_transacoes['data'].dt.to_period("M").astype(str) == mes_atual]
        else:
            df_mes_atual = pd.DataFrame()

        for g in gastos_rec:
            # Verifica se foi pago
            if not df_mes_atual.empty:
                pagos = df_mes_atual[
                    (df_mes_atual['descricao'] == g['descricao']) & 
                    (df_mes_atual['categoria'] == g['categoria']) & 
                    (df_mes_atual['tipo'] == 'saida mensal')
                ]
            else:
                pagos = pd.DataFrame()
                
            if pagos.empty:
                dia_v = int(g.get('dia_vencimento', 1)) if pd.notna(g.get('dia_vencimento')) else 1
                pendentes_rec.append({
                    'descricao': f"🔁 {g['descricao']} (Recorrente)",
                    'valor': g['valor'],
                    'dia_vencimento': dia_v
                })
                
        df_pendentes_rec = pd.DataFrame(pendentes_rec)
        
        # Juntar tudo
        df_venc = pd.concat([df_faturas, df_pendentes_rec], ignore_index=True)
        
        if df_venc.empty:
            st.success("Uhuul! 🎉 Nenhuma fatura ou gasto recorrente pendente com vencimento. Pode relaxar!")
            st.balloons()
            return
            
        # Calcular dias até o vencimento baseado no dia atual
        df_venc['dias_restantes'] = df_venc['dia_vencimento'].apply(lambda d: int(d) - hoje.day)
        
        # Ordenar pelos mais urgentes
        df_venc = df_venc.sort_values(by='dias_restantes')
        
        st.markdown("### Faturas e Contas programadas:")
        
        tem_urgente = False
        for _, row in df_venc.iterrows():
            dias = int(row['dias_restantes'])
            dia_str = f"Dia {int(row['dia_vencimento'])}"
            valor_str = f"R$ {row['valor']:.2f}"
            
            if dias < 0:
                st.error(f"\U0001f6a8 **VENCIDO HÁ {-dias} DIA(S)!** \u2022 {row['descricao']} ({valor_str}) - Vencimento: {dia_str}. Corre pagar!! \U0001f3c3\u200d\u2642\ufe0f\U0001f4a8")
                tem_urgente = True
            elif dias == 0:
                st.error(f"\u26a0\ufe0f **VENCE HOJE!** \u2022 {row['descricao']} ({valor_str}). Não deixa virar abóbora! \U0001f383")
                tem_urgente = True
            elif dias <= 3:
                st.warning(f"\u23f0 **VENCE EM {dias} DIA(S)!** \u2022 {row['descricao']} ({valor_str}) \u2014 Vencimento: {dia_str}. Já deixa o dinheiro separado! \U0001f4b8")
                tem_urgente = True
            elif dias <= 7:
                st.warning(f"\U0001f440 **Atenção:** \u2022 {row['descricao']} ({valor_str}) vence em {dias} dia(s) (Vencimento: {dia_str}).")
            else:
                st.info(f"\U0001f7e2 **Tranquilo ({dias} dias):** \u2022 {row['descricao']} ({valor_str}) (Vencimento: {dia_str}). Sussa! \U0001f60e")
        
        if not tem_urgente:
            st.success("Nenhuma conta estourando. Você está no controle da situação! \U0001f44f")


# ────────────────────────────────────────────────────────
# INDICADORES DE MERCADO (Banco Central + Câmbio em Tempo Real)
# ────────────────────────────────────────────────────────

# Códigos das séries SGS do Banco Central
_SGS = {
    "selic_meta": 432,        # Taxa SELIC meta (a.a.)
    "poupanca":   196,        # Rendimento da poupança (a.m.)
    "tr":         226,        # Taxa Referencial (TR)
    "ipca":       433,        # Inflação IPCA (a.m.)
    "igpm":       189,        # IGP-M (a.m.)
    "usd_ptax":   10813,      # Dólar comercial PTAX (BCB)
    "eur_ptax":   21619,      # Euro PTAX (BCB)
}

_BCB_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


@st.cache_data(ttl=3600)
def _buscar_historico_bcb(codigo: int, ultimos: int = 12) -> pd.DataFrame:
    """
    Busca os últimos N registros de uma série SGS do BCB.
    USA /ultimos/{N} — eficiente, NÃO baixa o histórico completo.
    Retorna DataFrame com colunas [data, valor] ou DataFrame vazio em caso de erro.
    """
    url = (
        f"https://api.bcb.gov.br/dados/serie/"
        f"bcdata.sgs.{codigo}/dados/ultimos/{ultimos}?formato=json"
    )
    try:
        resp = requests.get(url, headers=_BCB_HEADERS, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
        # Valida que a resposta é uma lista antes de converter
        if not isinstance(dados, list) or len(dados) == 0:
            return pd.DataFrame()
        df = pd.DataFrame(dados)
        if "data" not in df.columns or "valor" not in df.columns:
            return pd.DataFrame()
        df["data"] = pd.to_datetime(df["data"], dayfirst=True)
        df["valor"] = df["valor"].astype(float)
        return df[["data", "valor"]]
    except (requests.exceptions.RequestException, ValueError, TypeError, KeyError):
        return pd.DataFrame()


def _calcular_rendimento_poupanca(selic_aa: float, tr_am: float = 0.0) -> float:
    """
    Calcula o rendimento mensal da poupança conforme a regra do BCB:
      - Se SELIC > 8.5% a.a.: rendimento = 0.5% a.m. + TR
      - Se SELIC <= 8.5% a.a.: rendimento = 70% da SELIC/12 + TR
    """
    if selic_aa > 8.5:
        return round(0.5 + tr_am, 4)
    return round((selic_aa * 0.7 / 12) + tr_am, 4)


@st.cache_data(ttl=3600)
def _buscar_taxas_brasilapi() -> dict:
    """
    Fonte primária: BrasilAPI /taxas/v1
    CDN global, 1 única requisição, sem chave de API.
    Retorna SELIC, CDI e IPCA anual.
    """
    url = "https://brasilapi.com.br/api/taxas/v1"
    resultado = {}
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        dados = resp.json()
        # Valida que a resposta é uma lista antes de iterar
        if not isinstance(dados, list):
            return {}
        for item in dados:
            if not isinstance(item, dict):
                continue
            nome = item.get("nome", "").upper()
            valor = item.get("valor")
            if valor is None:
                continue
            if nome == "SELIC":
                resultado["selic_ano"] = f"{valor}% a.a."
                resultado["selic_raw"] = float(valor)
            elif nome == "CDI":
                resultado["cdi_ano"] = f"{valor}% a.a."
            elif nome == "IPCA":
                resultado["ipca_acumulado"] = f"{valor}%"
        resultado["fonte_taxas"] = "BrasilAPI"
        return resultado
    except (requests.exceptions.RequestException, ValueError, TypeError):
        return {}


@st.cache_data(ttl=3600)
def _buscar_taxas_bcb() -> dict:
    """
    Fonte de fallback: API SGS do Banco Central do Brasil.
    Inclui cálculo correto do rendimento da poupança.
    """
    resultado = {}
    df_selic = _buscar_historico_bcb(_SGS["selic_meta"], ultimos=1)
    selic_val = float(df_selic.iloc[-1]["valor"]) if not df_selic.empty else None

    if selic_val is not None:
        resultado["selic_ano"] = f"{selic_val}% a.a."
        resultado["selic_raw"] = selic_val

    df_tr = _buscar_historico_bcb(_SGS["tr"], ultimos=1)
    tr_val = float(df_tr.iloc[-1]["valor"]) if not df_tr.empty else 0.0

    df_poupanca = _buscar_historico_bcb(_SGS["poupanca"], ultimos=1)
    if not df_poupanca.empty:
        resultado["poupanca_mes"] = f"{df_poupanca.iloc[-1]['valor']}% a.m."
    elif selic_val is not None:
        calc = _calcular_rendimento_poupanca(selic_val, tr_val)
        resultado["poupanca_mes"] = f"{calc}% a.m. (calculado)"

    df_ipca = _buscar_historico_bcb(_SGS["ipca"], ultimos=1)
    if not df_ipca.empty:
        resultado["ipca_mes"] = f"{df_ipca.iloc[-1]['valor']}%"

    df_igpm = _buscar_historico_bcb(_SGS["igpm"], ultimos=1)
    if not df_igpm.empty:
        resultado["igpm_mes"] = f"{df_igpm.iloc[-1]['valor']}%"

    resultado["fonte_taxas"] = "Banco Central do Brasil (SGS)"
    return resultado


@st.cache_data(ttl=1800)
def _buscar_cambio_awesomeapi() -> dict:
    """Cotação de câmbio em tempo real via AwesomeAPI.
    Fallback automático para BCB PTAX se a AwesomeAPI falhar.
    """
    url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL"
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        dados = resp.json()
        # Valida que a resposta é um dict e contém as chaves esperadas
        if not isinstance(dados, dict) or "USDBRL" not in dados or "EURBRL" not in dados:
            raise ValueError("Resposta inesperada da AwesomeAPI")
        return {
            "dolar": f"R$ {float(dados['USDBRL']['bid']):.2f}",
            "euro":  f"R$ {float(dados['EURBRL']['bid']):.2f}",
            "atualizacao_dolar": dados["USDBRL"].get("create_date", "N/D"),
            "fonte_cambio": "AwesomeAPI",
        }
    except (requests.exceptions.RequestException, ValueError, TypeError, KeyError):
        pass
    # Fallback: câmbio PTAX direto do BCB/SGS
    try:
        df_usd = _buscar_historico_bcb(_SGS["usd_ptax"], ultimos=1)
        df_eur = _buscar_historico_bcb(_SGS["eur_ptax"], ultimos=1)
        if df_usd.empty and df_eur.empty:
            raise ValueError("BCB PTAX indisponível")
        return {
            "dolar": f"R$ {df_usd.iloc[-1]['valor']:.2f}" if not df_usd.empty else "Indisponível",
            "euro":  f"R$ {df_eur.iloc[-1]['valor']:.2f}" if not df_eur.empty else "Indisponível",
            "atualizacao_dolar": "PTAX / BCB",
            "fonte_cambio": "BCB/SGS (PTAX)",
        }
    except (ValueError, IndexError, KeyError):
        return {"dolar": "Indisponível", "euro": "Indisponível", "fonte_cambio": "Indisponível"}


def consultar_indicadores_economicos_br() -> dict:
    """
    Retorna taxas brasileiras (SELIC, CDI, IPCA, IGP-M, Poupança) e câmbio (USD, EUR)
    consolidados em um único dict. Cache de 1h via @st.cache_data nas funções internas.
    """
    taxas = _buscar_taxas_brasilapi()
    if not taxas.get("selic_ano"):
        taxas = _buscar_taxas_bcb()

    cambio = _buscar_cambio_awesomeapi()
    indicadores = {**taxas, **cambio}

    indicadores.setdefault("selic_ano",    "Indisponível")
    indicadores.setdefault("poupanca_mes", "Indisponível")
    indicadores.setdefault("ipca_mes",     "Indisponível")
    indicadores.setdefault("igpm_mes",     "Indisponível")
    indicadores["status"] = "Sucesso" if taxas.get("selic_ano") else "Parcial (apenas câmbio disponível)"
    return indicadores


def consultar_cambio_atual() -> dict:
    """Mantido por compatibilidade. Delega para _buscar_cambio_awesomeapi."""
    raw = _buscar_cambio_awesomeapi()
    return {
        "dolar": {"valor": raw.get("dolar", "N/D"), "atualizacao": raw.get("atualizacao_dolar", "N/D")},
        "euro": {"valor": raw.get("euro", "N/D"), "atualizacao": "N/D"},
        "status": "sucesso" if raw.get("fonte_cambio") == "AwesomeAPI" else "erro",
    }


def exibir_indicadores_mercado():
    """Exibe em tempo real os indicadores do Banco Central e cotações de câmbio."""
    with st.expander("📊 Indicadores de Mercado (tempo real)", expanded=True):
        with st.spinner("🔄 Consultando Banco Central e cotações..."):
            indicadores = consultar_indicadores_economicos_br()

        st.markdown("### 🏦 Indicadores Econômicos")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🎯 SELIC (taxa básica)", indicadores.get("selic_ano", "N/D"))
            st.metric("💰 IPCA (inflação)", indicadores.get("ipca_mes", indicadores.get("ipca_acumulado", "N/D")))
        with col2:
            st.metric("💳 Poupança (a.m.)", indicadores.get("poupanca_mes", "N/D"))
            st.metric("🏠 IGP-M (aluguel/atacado)", indicadores.get("igpm_mes", "N/D"))
        if indicadores.get("cdi_ano"):
            st.metric("🏦 CDI", indicadores["cdi_ano"])

        if indicadores.get("status") not in ("Sucesso", None):
            st.caption(f"⚠️ {indicadores.get('status', '')}")

        st.divider()
        st.markdown("### 💱 Câmbio Atual")
        col3, col4 = st.columns(2)
        with col3:
            st.metric("🇺🇸 Dólar (USD)", indicadores.get("dolar", "N/D"))
        with col4:
            st.metric("🇪🇺 Euro (EUR)", indicadores.get("euro", "N/D"))

        st.caption(
            f"🔗 Taxas: **{indicadores.get('fonte_taxas', '')}** | "
            f"Câmbio: **{indicadores.get('fonte_cambio', '')}** | "
            "[BCB/SGS](https://sgsweb.bcb.gov.br/sgspub/) | "
            "[AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas)"
        )




# ────────────────────────────────────────────────────────────────────────
# SKILL: GERADOR DE RELATÓRIO FINANCEIRO PDF (LUMMI)
# ────────────────────────────────────────────────────────────────────────

def gerar_relatorio_pdf(
    df_transacoes: pd.DataFrame,
    perfil: dict,
    mes_selecionado: str,
    saldo_do_mes: float,
    entradas_mes: float,
    saidas_mes: float,
    saldo_total: float,
    total_dividas: float,
    reserva_atual: float,
    logo_path: str = None,
) -> bytes:
    """
    Gera um relatório financeiro profissional em PDF com a identidade visual LUMMI.
    Retorna os bytes do PDF prontos para download.
    """
    # ── Auto-instalar reportlab se não estiver disponível ───────────────
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, Image as RLImage, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        import subprocess, sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "reportlab"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, Image as RLImage, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    # ── Paleta de cores LUMMI ───────────────────────────────────────────
    AZUL_LUMMI       = colors.HexColor("#1A73E8")   # azul primário
    AZUL_ESCURO      = colors.HexColor("#0D47A1")   # azul cabeçalho
    CINZA_CLARO      = colors.HexColor("#F5F7FA")   # fundo linhas pares
    VERDE_POSITIVO   = colors.HexColor("#1B8A4C")   # entradas / positivo
    VERMELHO_NEG     = colors.HexColor("#C62828")   # saídas / negativo
    AMARELO_ALERT    = colors.HexColor("#F57F17")   # dívidas / alertas
    BRANCO           = colors.white
    PRETO            = colors.HexColor("#212121")
    CINZA_TEXTO      = colors.HexColor("#555555")
    CINZA_BORDA      = colors.HexColor("#BDBDBD")

    # ── Buffer e documento ──────────────────────────────────────────────
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2.0 * cm,
    )
    PAGE_W = A4[0] - 3.6 * cm  # largura útil

    # ── Estilos de texto ────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "LummiTitulo",
        fontSize=22,
        leading=28,
        textColor=AZUL_ESCURO,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
    )
    estilo_subtitulo = ParagraphStyle(
        "LummiSubtitulo",
        fontSize=12,
        textColor=CINZA_TEXTO,
        fontName="Helvetica",
        alignment=TA_LEFT,
        leading=16,
    )
    estilo_secao = ParagraphStyle(
        "LummiSecao",
        fontSize=12,
        leading=16,
        textColor=BRANCO,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
        spaceAfter=2,
    )
    estilo_normal = ParagraphStyle(
        "LummiNormal",
        fontSize=9,
        leading=13,
        textColor=PRETO,
        fontName="Helvetica",
    )
    estilo_rodape = ParagraphStyle(
        "LummiRodape",
        fontSize=8,
        textColor=CINZA_TEXTO,
        fontName="Helvetica",
        alignment=TA_CENTER,
    )

    # ── Helper: cabeçalho de seção colorido ─────────────────────────────
    def secao(texto, cor_fundo=AZUL_LUMMI):
        """Retorna um bloco de cabeçalho de seção estilizado."""
        return [
            Spacer(1, 0.35 * cm),
            Table(
                [[Paragraph(texto, estilo_secao)]],
                colWidths=[PAGE_W],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), cor_fundo),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [cor_fundo]),
                    ("TOPPADDING",    (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                    ("ROUNDEDCORNERS", [4]),
                ]),
            ),
            Spacer(1, 0.2 * cm),
        ]

    # ── Helper: tabela genérica com cabeçalho bold ──────────────────────
    def tabela_formatada(dados, col_widths, header_bg=AZUL_ESCURO):
        """Cria uma Table estilizada com cabeçalho em negrito e linhas alternadas."""
        n_cols = len(dados[0])
        n_rows = len(dados)
        estilo = TableStyle([
            # Cabeçalho
            ("BACKGROUND",    (0, 0), (-1, 0),  header_bg),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  BRANCO),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  9),
            ("TOPPADDING",    (0, 0), (-1, 0),  7),
            ("BOTTOMPADDING", (0, 0), (-1, 0),  7),
            ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
            # Dados
            ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 1), (-1, -1), 8),
            ("TOPPADDING",    (0, 1), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            # Grid
            ("GRID",          (0, 0), (-1, -1), 0.4, CINZA_BORDA),
            ("LINEBELOW",     (0, 0), (-1, 0),  1.2, AZUL_LUMMI),
            # Linhas alternadas
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ])
        t = Table(dados, colWidths=col_widths)
        t.setStyle(estilo)
        return t

    # ── Montar conteúdo ─────────────────────────────────────────────────
    story = []

    # ─── CABEÇALHO: Logo + Título ───────────────────────────────────────
    logo_cell = ""
    if logo_path and os.path.exists(logo_path):
        try:
            logo_img = RLImage(logo_path, width=3.5 * cm, height=1.5 * cm)
            logo_img.hAlign = "LEFT"
            logo_cell = logo_img
        except Exception:
            logo_cell = Paragraph("<b>LUMMI</b>", estilo_titulo)
    else:
        logo_cell = Paragraph("<b>💰 LUMMI</b>", estilo_titulo)

    nome_usuario = perfil.get("nome", "Usuário")
    header_data = [[
        logo_cell,
        Paragraph(
            f"<b>Relatório Financeiro</b><br/>"
            f"<font size='10' color='#555555'>{nome_usuario} &nbsp;|&nbsp; Mês: {mes_selecionado}</font>",
            ParagraphStyle("H", fontSize=16, fontName="Helvetica-Bold",
                           textColor=AZUL_ESCURO, alignment=TA_RIGHT, leading=22)
        )
    ]]
    header_table = Table(
        header_data,
        colWidths=[PAGE_W * 0.35, PAGE_W * 0.65],
        style=TableStyle([
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",    (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",   (0, 0), (-1, -1), 0),
            ("TOPPADDING",     (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 0),
        ]),
    )
    story.append(header_table)
    story.append(HRFlowable(width=PAGE_W, thickness=2, color=AZUL_LUMMI, spaceAfter=6))
    story.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}  &nbsp;|&nbsp;  "
        f"Profissão: {perfil.get('profissao', '—')}  &nbsp;|&nbsp;  "
        f"Perfil Investidor: {perfil.get('perfil_investidor', '—').capitalize()}",
        estilo_subtitulo
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ─── SEÇÃO 1: Resumo do Mês ──────────────────────────────────────────
    story += secao("📊  RESUMO FINANCEIRO DO MÊS")

    kpi_data = [
        ["Indicador", "Valor"],
        ["💰  Entradas do Mês",        f"R$ {entradas_mes:,.2f}"],
        ["💸  Saídas do Mês",          f"R$ {saidas_mes:,.2f}"],
        ["📈  Saldo do Mês",           f"R$ {saldo_do_mes:,.2f}"],
        ["🏦  Saldo Total Acumulado",  f"R$ {saldo_total:,.2f}"],
        ["⚠️  Dívidas Pendentes",      f"R$ {total_dividas:,.2f}"],
        ["🛡️  Reserva de Emergência",  f"R$ {reserva_atual:,.2f}"],
    ]

    kpi_table = Table(
        kpi_data,
        colWidths=[PAGE_W * 0.55, PAGE_W * 0.45],
        style=TableStyle([
            # Cabeçalho
            ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_ESCURO),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  BRANCO),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  10),
            ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
            ("TOPPADDING",    (0, 0), (-1, 0),  8),
            ("BOTTOMPADDING", (0, 0), (-1, 0),  8),
            # Coluna de label (bold)
            ("FONTNAME",      (0, 1), (0, -1),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 1), (0, -1),  9),
            # Coluna de valor
            ("FONTNAME",      (1, 1), (1, -1),  "Helvetica"),
            ("FONTSIZE",      (1, 1), (1, -1),  9),
            ("ALIGN",         (1, 1), (1, -1),  "RIGHT"),
            # Cores condicional por linha
            ("TEXTCOLOR",     (1, 2), (1, 2),   VERDE_POSITIVO),  # entradas
            ("TEXTCOLOR",     (1, 3), (1, 3),   VERMELHO_NEG),    # saídas
            ("TEXTCOLOR",     (1, 4), (1, 4),
             VERDE_POSITIVO if saldo_do_mes >= 0 else VERMELHO_NEG),
            ("TEXTCOLOR",     (1, 5), (1, 5),
             VERDE_POSITIVO if saldo_total >= 0 else VERMELHO_NEG),
            ("TEXTCOLOR",     (1, 6), (1, 6),   AMARELO_ALERT),   # dívidas
            ("TEXTCOLOR",     (1, 7), (1, 7),   VERDE_POSITIVO),  # reserva (idx 7 if 7 rows)
            # Linhas
            ("GRID",          (0, 0), (-1, -1), 0.4, CINZA_BORDA),
            ("LINEBELOW",     (0, 0), (-1, 0),  1.2, AZUL_LUMMI),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRANCO, CINZA_CLARO]),
            ("TOPPADDING",    (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(KeepTogether(kpi_table))
    story.append(Spacer(1, 0.5 * cm))

    # ─── SEÇÃO 2: Resumo por Categoria ──────────────────────────────────
    if not df_transacoes.empty:
        story += secao("📂  RESUMO POR CATEGORIA (MÊS SELECIONADO)")

        df_mes = df_transacoes[
            df_transacoes["mes_ano"] == mes_selecionado
        ].copy() if "mes_ano" in df_transacoes.columns else df_transacoes.copy()

        if not df_mes.empty:
            resumo_cat = (
                df_mes.groupby(["tipo", "categoria"])["valor"]
                .sum()
                .reset_index()
                .sort_values(["tipo", "valor"], ascending=[True, False])
            )
            cat_data = [["Tipo", "Categoria", "Total (R$)"]]
            for _, row in resumo_cat.iterrows():
                cat_data.append([
                    row["tipo"].capitalize(),
                    row["categoria"],
                    f"R$ {row['valor']:,.2f}"
                ])
            t_cat = tabela_formatada(
                cat_data,
                col_widths=[PAGE_W * 0.30, PAGE_W * 0.45, PAGE_W * 0.25]
            )
            # Colorir coluna de valor por tipo
            estilo_cat = t_cat._argH  # acessa estilos internos
            story.append(t_cat)
        else:
            story.append(Paragraph("Nenhum lançamento neste mês.", estilo_normal))
        story.append(Spacer(1, 0.5 * cm))

    # ─── SEÇÃO 3: Dados do Perfil ────────────────────────────────────────
    story += secao("👤  PERFIL DO USUÁRIO", cor_fundo=AZUL_ESCURO)

    perfil_data = [
        ["Campo", "Informação"],
        ["Nome",               perfil.get("nome", "—")],
        ["Profissão",          perfil.get("profissao", "—")],
        ["Renda Mensal",       f"R$ {float(perfil.get('renda_mensal', 0)):,.2f}"],
        ["Perfil Investidor",  perfil.get("perfil_investidor", "—").capitalize()],
        ["Objetivo Principal", perfil.get("objetivo_principal", "—")],
        ["Patrimônio Total",   f"R$ {float(perfil.get('patrimonio_total', 0)):,.2f}"],
    ]
    t_perfil = tabela_formatada(
        perfil_data,
        col_widths=[PAGE_W * 0.35, PAGE_W * 0.65]
    )
    story.append(KeepTogether(t_perfil))
    story.append(Spacer(1, 0.5 * cm))

    # ─── SEÇÃO 4: Detalhamento de Transações ─────────────────────────────
    story += secao("📋  DETALHAMENTO DAS TRANSAÇÕES")

    if not df_transacoes.empty:
        # Ordenar por data descendente
        df_det = df_transacoes.sort_values("data", ascending=False).copy()

        colunas_exibir = ["data", "descricao", "categoria", "tipo", "valor"]
        colunas_exibir = [c for c in colunas_exibir if c in df_det.columns]

        tx_data = [["Data", "Descrição", "Categoria", "Tipo", "Valor (R$)"]]
        for _, row in df_det.iterrows():
            data_fmt = row["data"].strftime("%d/%m/%Y") if pd.notna(row.get("data")) else "—"
            tx_data.append([
                data_fmt,
                str(row.get("descricao", "—")),
                str(row.get("categoria", "—")),
                str(row.get("tipo", "—")).capitalize(),
                f"{float(row.get('valor', 0)):,.2f}",
            ])

        # Construir comandos de cor por linha antes de criar a tabela
        cor_cmds = []
        for i, row in enumerate(df_det.itertuples(), start=1):
            tipo_r = str(getattr(row, "tipo", "")).lower()
            if "entrada" in tipo_r:
                cor_cmds.append(("TEXTCOLOR", (4, i), (4, i), VERDE_POSITIVO))
                cor_cmds.append(("FONTNAME",  (4, i), (4, i), "Helvetica-Bold"))
            elif "divida" in tipo_r:
                cor_cmds.append(("TEXTCOLOR", (4, i), (4, i), AMARELO_ALERT))
            else:
                cor_cmds.append(("TEXTCOLOR", (4, i), (4, i), VERMELHO_NEG))

        t_tx = tabela_formatada(
            tx_data,
            col_widths=[
                PAGE_W * 0.13,
                PAGE_W * 0.30,
                PAGE_W * 0.22,
                PAGE_W * 0.18,
                PAGE_W * 0.17,
            ]
        )
        if cor_cmds:
            t_tx.setStyle(TableStyle(cor_cmds))

        story.append(t_tx)
    else:
        story.append(Paragraph("Nenhuma transação registrada.", estilo_normal))

    story.append(Spacer(1, 0.8 * cm))

    # ─── RODAPÉ ─────────────────────────────────────────────────────────
    story.append(HRFlowable(width=PAGE_W, thickness=1, color=CINZA_BORDA))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        "Relatório gerado automaticamente pelo Agente LUMMI — Inteligência Financeira Pessoal &nbsp;|&nbsp; "
        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} &nbsp;|&nbsp; "
        "Uso exclusivo do usuário. Não compartilhe.",
        estilo_rodape
    ))

    # ── Build ────────────────────────────────────────────────────────────
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def exibir_botao_download_pdf(
    df_transacoes: pd.DataFrame,
    perfil: dict,
    mes_selecionado: str,
    saldo_do_mes: float,
    entradas_mes: float,
    saidas_mes: float,
    saldo_total: float,
    total_dividas: float,
    reserva_atual: float,
    logo_path: str = None,
):
    """
    Renderiza na sidebar/tela o botão de download do PDF do relatório LUMMI.
    Adicione esta chamada em app.py dentro do bloco `with st.sidebar:`.
    """
    # Garante que a coluna mes_ano existe
    if "mes_ano" not in df_transacoes.columns and "data" in df_transacoes.columns:
        df_transacoes = df_transacoes.copy()
        df_transacoes["data"] = pd.to_datetime(df_transacoes["data"], errors="coerce")
        df_transacoes["mes_ano"] = df_transacoes["data"].dt.to_period("M").astype(str)

    if st.button("📄 Gerar Relatório PDF", use_container_width=True, key="btn_pdf_lummi"):
        with st.spinner("✍️ Gerando seu relatório profissional..."):
            try:
                pdf_bytes = gerar_relatorio_pdf(
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
                st.download_button(
                    label="⬇️  Baixar Relatório PDF",
                    data=pdf_bytes,
                    file_name=f"relatorio_lummi_{mes_selecionado}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_pdf_lummi",
                )
                st.success("✅ PDF gerado com sucesso! Clique acima para baixar.")
            except Exception as e:
                st.error(f"❌ Erro ao gerar PDF: {e}")
