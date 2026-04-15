"""
Conexao com Oracle Autonomous Database (OCI).
Usa oracledb (thin mode — sem Oracle Client instalado).
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import oracledb
    ORACLEDB_AVAILABLE = True
except ImportError:
    ORACLEDB_AVAILABLE = False

logger = logging.getLogger("aria.db")

# ── Configuracao ─────────────────────────────────────────────
# Lidas de variáveis de ambiente ou .env para não expor credenciais
DB_USER     = os.getenv("ARIA_DB_USER",     "ADMIN")
DB_PASSWORD = os.getenv("ARIA_DB_PASSWORD", "")
DB_DSN      = os.getenv("ARIA_DB_DSN",      "")   # host:port/service_name
WALLET_DIR  = os.getenv("ARIA_WALLET_DIR",  "")   # pasta com wallet baixado do OCI


def _get_connection():
    """Abre uma conexao com o ADB. Retorna None se credenciais nao configuradas."""
    if not ORACLEDB_AVAILABLE:
        logger.warning("oracledb nao instalado — modo offline")
        return None
    if not DB_PASSWORD or not DB_DSN:
        logger.warning("Credenciais DB nao configuradas (ARIA_DB_USER / ARIA_DB_PASSWORD / ARIA_DB_DSN)")
        return None

    try:
        if WALLET_DIR and Path(WALLET_DIR).exists():
            conn = oracledb.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                dsn=DB_DSN,
                config_dir=WALLET_DIR,
                wallet_location=WALLET_DIR,
                wallet_password=os.getenv("ARIA_WALLET_PASSWORD", DB_PASSWORD),
            )
        else:
            conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        return conn
    except Exception as exc:
        logger.error("Falha ao conectar ao Oracle ADB: %s", exc)
        return None


def check_connection() -> bool:
    """Retorna True se a conexao estiver disponivel."""
    conn = _get_connection()
    if conn:
        conn.close()
        return True
    return False


def ensure_tables():
    """Cria tabelas necessarias se nao existirem."""
    conn = _get_connection()
    if not conn:
        return

    ddl_ola = """
        CREATE TABLE aria_ola_predictions (
            id               NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            numero           VARCHAR2(50),
            prio_num         NUMBER(1),
            hora_abertura    NUMBER(2),
            dia_semana       NUMBER(1),
            is_monitoring    NUMBER(1),
            descricao        VARCHAR2(500),
            grupo            VARCHAR2(200),
            probabilidade    NUMBER(6,4),
            nivel_risco      VARCHAR2(10),
            criado_em        TIMESTAMP DEFAULT SYSTIMESTAMP
        )
    """
    ddl_prio = """
        CREATE TABLE aria_priority_predictions (
            id                  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            numero              VARCHAR2(50),
            prio_num_entrada    NUMBER(1),
            prioridade_predita  NUMBER(1),
            descricao           VARCHAR2(500),
            grupo               VARCHAR2(200),
            criado_em           TIMESTAMP DEFAULT SYSTIMESTAMP
        )
    """

    cur = conn.cursor()
    for ddl in (ddl_ola, ddl_prio):
        try:
            cur.execute(ddl)
            conn.commit()
        except oracledb.DatabaseError as e:
            # ORA-00955 = tabela ja existe
            if "ORA-00955" not in str(e):
                logger.warning("DDL error: %s", e)
    cur.close()
    conn.close()


def insert_ola_prediction(
    numero: Optional[str],
    prio_num: int,
    hora: int,
    dia: int,
    is_monitoring: int,
    descricao: str,
    grupo: Optional[str],
    probabilidade: float,
    nivel_risco: str,
):
    conn = _get_connection()
    if not conn:
        return

    sql = """
        INSERT INTO aria_ola_predictions
            (numero, prio_num, hora_abertura, dia_semana, is_monitoring,
             descricao, grupo, probabilidade, nivel_risco)
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
    """
    cur = conn.cursor()
    try:
        cur.execute(sql, [
            numero, prio_num, hora, dia, is_monitoring,
            descricao[:500], grupo, round(probabilidade, 4), nivel_risco,
        ])
        conn.commit()
    except Exception as exc:
        logger.error("insert_ola_prediction falhou: %s", exc)
    finally:
        cur.close()
        conn.close()


def insert_priority_prediction(
    numero: Optional[str],
    prio_num_entrada: int,
    prioridade_predita: int,
    descricao: str,
    grupo: Optional[str],
):
    conn = _get_connection()
    if not conn:
        return

    sql = """
        INSERT INTO aria_priority_predictions
            (numero, prio_num_entrada, prioridade_predita, descricao, grupo)
        VALUES (:1, :2, :3, :4, :5)
    """
    cur = conn.cursor()
    try:
        cur.execute(sql, [numero, prio_num_entrada, prioridade_predita, descricao[:500], grupo])
        conn.commit()
    except Exception as exc:
        logger.error("insert_priority_prediction falhou: %s", exc)
    finally:
        cur.close()
        conn.close()


def fetch_recent_ola_predictions(limit: int = 100) -> list[dict]:
    """Retorna as ultimas predicoes OLA do banco."""
    conn = _get_connection()
    if not conn:
        return []

    sql = """
        SELECT numero, prio_num, hora_abertura, dia_semana, is_monitoring,
               descricao, grupo, probabilidade, nivel_risco, criado_em
        FROM   aria_ola_predictions
        ORDER  BY criado_em DESC
        FETCH  FIRST :1 ROWS ONLY
    """
    cur = conn.cursor()
    rows = []
    try:
        cur.execute(sql, [limit])
        cols = [c[0].lower() for c in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as exc:
        logger.error("fetch_recent_ola_predictions falhou: %s", exc)
    finally:
        cur.close()
        conn.close()
    return rows
