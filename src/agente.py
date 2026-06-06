import json
import pandas as pd
import os
from config import CAMINHO_EDU, DATA_DIR
from database import get_session, Perfil, Transacao, TipoTransacao

# --- CRUD Tipos de Transação ---

def carregar_tipos():
    try:
        db = get_session()
        tipos = db.query(TipoTransacao).all()
        tipos_dict = {t.chave: t.rotulo for t in tipos}
        db.close()
        return tipos_dict
    except Exception as e:
        return {}

def adicionar_tipo(chave, rotulo):
    try:
        db = get_session()
        if not db.query(TipoTransacao).filter(TipoTransacao.chave == chave).first():
            novo_tipo = TipoTransacao(chave=chave, rotulo=rotulo)
            db.add(novo_tipo)
            db.commit()
        db.close()
    except Exception as e:
        pass

def renomear_tipo(chave, novo_rotulo):
    try:
        db = get_session()
        t = db.query(TipoTransacao).filter(TipoTransacao.chave == chave).first()
        if t:
            t.rotulo = novo_rotulo
            db.commit()
        db.close()
    except Exception as e:
        pass

def remover_tipo(chave):
    try:
        db = get_session()
        t = db.query(TipoTransacao).filter(TipoTransacao.chave == chave).first()
        if t:
            db.delete(t)
            db.commit()
        db.close()
    except Exception as e:
        pass

def carregar_dados_base():
    perfil = {
        "nome": "Usuário", "profissao": "Não informada", "renda_mensal": 0.0, 
        "perfil_investidor": "Conservador", "reserva_emergencia_atual": 0.0, "metas": []
    }
    
    try:
        db = get_session()
        perfil_db = db.query(Perfil).first()
        if perfil_db and perfil_db.dados_json:
            perfil = json.loads(perfil_db.dados_json)
        db.close()
    except Exception as e:
        pass

    try:
        with open(CAMINHO_EDU, 'r', encoding='utf-8') as f:
            edu = json.load(f)
    except Exception as e:
        edu = {"conteudo": {"investimentos": {"termos": []}, "alertas_educacionais": []}}
        
    return perfil, edu

def carregar_transacoes():
    try:
        db = get_session()
        transacoes = db.query(Transacao).all()
        db.close()
        
        dados = []
        for t in transacoes:
            dados.append({
                'id': t.id,
                'data': t.data,
                'descricao': t.descricao,
                'categoria': t.categoria,
                'valor': t.valor,
                'tipo': t.tipo,
                'data_vencimento': t.data_vencimento,
                'dia_vencimento': t.dia_vencimento
            })
        
        df = pd.DataFrame(dados)
        if not df.empty:
            df['data'] = pd.to_datetime(df['data'])
            # Assegurar que data_vencimento também seja datetime
            if 'data_vencimento' in df.columns:
                df['data_vencimento'] = pd.to_datetime(df['data_vencimento'])
            return df
    except Exception as e:
        pass
        
    return pd.DataFrame(columns=['id', 'data', 'descricao', 'categoria', 'valor', 'tipo', 'data_vencimento', 'dia_vencimento'])

def salvar_nova_transacao(data, desc, cat, valor, tipo, data_vencimento=None, dia_vencimento=None):
    try:
        db = get_session()
        nova_transacao = Transacao(
            data=data,
            descricao=desc,
            categoria=cat,
            valor=valor,
            tipo=tipo,
            data_vencimento=pd.to_datetime(data_vencimento) if data_vencimento else None,
            dia_vencimento=int(dia_vencimento) if dia_vencimento else None
        )
        db.add(nova_transacao)
        db.commit()
        db.close()
    except Exception as e:
        pass
    
    return carregar_transacoes()

def atualizar_transacao(transacao_id, nova_desc, novo_valor, nova_data_vencimento=None, novo_tipo=None, novo_dia_vencimento=None):
    try:
        db = get_session()
        t = db.query(Transacao).filter(Transacao.id == transacao_id).first()
        if t:
            t.descricao = nova_desc
            t.valor = novo_valor
            if nova_data_vencimento is not None:
                t.data_vencimento = pd.to_datetime(nova_data_vencimento)
            if novo_tipo is not None:
                t.tipo = novo_tipo
            if novo_dia_vencimento is not None:
                t.dia_vencimento = int(novo_dia_vencimento)
            db.commit()
        db.close()
    except Exception as e:
        pass

def remover_transacao(transacao_id):
    try:
        db = get_session()
        t = db.query(Transacao).filter(Transacao.id == transacao_id).first()
        if t:
            db.delete(t)
            db.commit()
        db.close()
    except Exception as e:
        pass

def pagar_divida(transacao_id, valor_pago):
    try:
        db = get_session()
        t = db.query(Transacao).filter(Transacao.id == transacao_id).first()
        if t:
            t.valor -= valor_pago
            db.commit()
        db.close()
    except Exception as e:
        pass

def salvar_perfil(perfil_dict):
    try:
        db = get_session()
        perfil_db = db.query(Perfil).first()
        if perfil_db:
            perfil_db.dados_json = json.dumps(perfil_dict, ensure_ascii=False)
        else:
            novo_perfil = Perfil(dados_json=json.dumps(perfil_dict, ensure_ascii=False))
            db.add(novo_perfil)
        db.commit()
        db.close()
    except Exception as e:
        pass