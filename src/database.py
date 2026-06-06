import os
import json
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# URL de Conexão no Secrets
try:
    DATABASE_URL = st.secrets["DATABASE_URL"]
    # Algumas URLs podem precisar de um driver específico para o SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    st.error(f"Erro de conexão com o banco de dados. Verifique o secrets.toml. Erro: {e}")
    st.stop()

# ======= MODELOS =======

class Transacao(Base):
    __tablename__ = "transacoes"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(DateTime, default=datetime.now)
    descricao = Column(String)
    categoria = Column(String)
    valor = Column(Float)
    tipo = Column(String)
    data_vencimento = Column(DateTime, nullable=True)
    dia_vencimento = Column(Integer, nullable=True)

class Perfil(Base):
    __tablename__ = "perfil"
    id = Column(Integer, primary_key=True, index=True)
    dados_json = Column(Text) # Guardaremos o perfil inteiro como um texto JSON

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    content = Column(Text)
    skill = Column(String, nullable=True)
    data_hora = Column(DateTime, default=datetime.now)

class TipoTransacao(Base):
    __tablename__ = "tipo_transacao"
    id = Column(Integer, primary_key=True, index=True)
    chave = Column(String, unique=True, index=True)
    rotulo = Column(String)

# ======= FUNÇÕES DE BANCO =======

def init_db():
    # Cria as tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy import text
    
    # Migração simples para adicionar a coluna data_vencimento em bancos existentes
    try:
        with engine.begin() as conn:
            # Em PostgreSQL usa-se TIMESTAMP
            conn.execute(text("ALTER TABLE transacoes ADD COLUMN data_vencimento TIMESTAMP"))
    except Exception as e:
        if "DuplicateColumn" not in str(e):
            print("Aviso na migração do banco (data_vencimento):", e)
            
    # Migração para dia_vencimento
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transacoes ADD COLUMN dia_vencimento INTEGER"))
    except Exception as e:
        if "DuplicateColumn" not in str(e):
            print("Aviso na migração do banco (dia_vencimento):", e)
            
    # Inserir tipos padrão caso a tabela esteja vazia
    db = SessionLocal()
    try:
        if db.query(TipoTransacao).count() == 0:
            tipos_iniciais = [
                TipoTransacao(chave="saida", rotulo="💸 Gastos (Saídas)"),
                TipoTransacao(chave="saida mensal", rotulo="🔁 Gastos Recorrentes"),
                TipoTransacao(chave="Divida Banco", rotulo="🏦 Dívida Banco"),
                TipoTransacao(chave="Divida Loja", rotulo="🛒 Dívida Lojas"),
                TipoTransacao(chave="entrada", rotulo="🟢 Ingressos / Renda")
            ]
            db.add_all(tipos_iniciais)
            db.commit()
        else:
            # Migração: garante que 'saida mensal' exista mesmo em bancos já criados
            existe = db.query(TipoTransacao).filter(TipoTransacao.chave == "saida mensal").first()
            if not existe:
                db.add(TipoTransacao(chave="saida mensal", rotulo="🔁 Gastos Recorrentes"))
                db.commit()
            
            # Limpeza: remove qualquer tipo que NÃO seja um dos tipos padrão conhecidos
            tipos_validos = {"saida", "saida mensal", "entrada", "Divida Banco", "Divida Loja"}
            todos = db.query(TipoTransacao).all()
            removidos = False
            for t in todos:
                if t.chave not in tipos_validos:
                    print(f"Removendo tipo não-padrão: chave='{t.chave}' rotulo='{t.rotulo}'")
                    db.delete(t)
                    removidos = True
            if removidos:
                db.commit()
    except Exception as e:
        print("Aviso na inicialização dos tipos:", e)
    finally:
        db.close()
    
def get_session():
    return SessionLocal()

def migrar_dados_iniciais(caminho_csv, caminho_json):
    db = get_session()
    
    # Migrar Perfil se estiver vazio
    if db.query(Perfil).count() == 0:
        try:
            with open(caminho_json, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                novo_perfil = Perfil(dados_json=json.dumps(dados))
                db.add(novo_perfil)
                db.commit()
        except Exception as e:
            pass # Se o arquivo não existir, ignora
            
    # Migrar Transações se estiver vazio
    if db.query(Transacao).count() == 0:
        try:
            if os.path.exists(caminho_csv):
                df = pd.read_csv(caminho_csv)
                for _, row in df.iterrows():
                    nova_transacao = Transacao(
                        data=pd.to_datetime(row['data']),
                        descricao=row['descricao'],
                        categoria=row['categoria'],
                        valor=row['valor'],
                        tipo=row['tipo']
                    )
                    db.add(nova_transacao)
                db.commit()
        except Exception as e:
            pass
            
    db.close()
