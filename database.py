# -*- coding: utf-8 -*-
"""
database.py — Módulo de banco de dados (SQLite3)
Sistema Oficina 2026
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oficina.db")


def get_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Cria as tabelas se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                endereco TEXT DEFAULT '',
                telefone TEXT DEFAULT '',
                documento TEXT DEFAULT '',
                data_cadastro TEXT DEFAULT (DATE('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS servicos (
                ra TEXT PRIMARY KEY,
                cliente_id INTEGER NOT NULL,
                aparelho TEXT DEFAULT '',
                marca TEXT DEFAULT '',
                modelo TEXT DEFAULT '',
                numero_serie TEXT DEFAULT '',
                defeito_relatado TEXT DEFAULT '',
                servico_realizado TEXT DEFAULT '',
                status TEXT DEFAULT 'Aberto' CHECK(status IN ('Aberto','Aguardando Peça','Pronto','Entregue')),
                valor_total REAL DEFAULT 0.0,
                data_entrada TEXT DEFAULT (DATE('now', 'localtime')),
                data_saida TEXT DEFAULT '',
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            );

            CREATE TABLE IF NOT EXISTS pecas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servico_ra TEXT NOT NULL,
                descricao TEXT DEFAULT '',
                valor_unitario REAL DEFAULT 0.0,
                FOREIGN KEY (servico_ra) REFERENCES servicos(ra)
            );
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao inicializar banco: {e}")
    finally:
        conn.close()


# ──────────────────────────── CLIENTES ────────────────────────────

def salvar_cliente(nome, endereco="", telefone="", documento=""):
    """Insere um novo cliente e retorna o ID gerado."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nome, endereco, telefone, documento) VALUES (?, ?, ?, ?)",
            (nome.strip(), endereco.strip(), telefone.strip(), documento.strip())
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao salvar cliente: {e}")
        return None
    finally:
        conn.close()


def buscar_clientes(query):
    """Busca clientes cujo nome ou telefone contenha a query (as-you-type)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        like = f"%{query.strip()}%"
        cursor.execute(
            "SELECT * FROM clientes WHERE nome LIKE ? OR telefone LIKE ? ORDER BY nome LIMIT 20",
            (like, like)
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha na busca de clientes: {e}")
        return []
    finally:
        conn.close()


def obter_cliente(cliente_id):
    """Retorna um cliente por ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao obter cliente: {e}")
        return None
    finally:
        conn.close()


def listar_todos_clientes():
    """Retorna todos os clientes ordenados por nome."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao listar clientes: {e}")
        return []
    finally:
        conn.close()


def atualizar_cliente(cliente_id, nome, endereco, telefone, documento):
    """Atualiza os dados de um cliente existente."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE clientes SET nome=?, endereco=?, telefone=?, documento=? WHERE id=?",
            (nome.strip(), endereco.strip(), telefone.strip(), documento.strip(), cliente_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao atualizar cliente: {e}")
        return False
    finally:
        conn.close()


# ──────────────────────────── SERVIÇOS / OS ────────────────────────────

def gerar_ra():
    """Gera um RA no formato ANO + SEQUENCIAL (ex: 2026001)."""
    ano = datetime.now().year
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ra FROM servicos WHERE ra LIKE ? ORDER BY ra DESC LIMIT 1",
            (f"{ano}%",)
        )
        row = cursor.fetchone()
        if row:
            ultimo_seq = int(row["ra"][4:])
            novo_seq = ultimo_seq + 1
        else:
            novo_seq = 1
        return f"{ano}{novo_seq:03d}"
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao gerar RA: {e}")
        return f"{ano}001"
    finally:
        conn.close()


def salvar_servico(ra, cliente_id, aparelho="", marca="", modelo="",
                   numero_serie="", defeito_relatado="", valor_total=0.0):
    """Insere uma nova ordem de serviço."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO servicos
               (ra, cliente_id, aparelho, marca, modelo, numero_serie, defeito_relatado, valor_total)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (ra, cliente_id, aparelho.strip(), marca.strip(), modelo.strip(),
             numero_serie.strip(), defeito_relatado.strip(), valor_total)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao salvar serviço: {e}")
        return False
    finally:
        conn.close()


def obter_servico(ra):
    """Retorna um serviço por RA, incluindo dados do cliente."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT s.*, c.nome AS cliente_nome, c.endereco AS cliente_endereco,
                      c.telefone AS cliente_telefone, c.documento AS cliente_documento
               FROM servicos s
               JOIN clientes c ON s.cliente_id = c.id
               WHERE s.ra = ?""",
            (ra,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao obter serviço: {e}")
        return None
    finally:
        conn.close()


def listar_servicos(status=None):
    """Lista serviços filtrados por status. Se status=None, retorna todos."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if status:
            cursor.execute(
                """SELECT s.ra, c.nome AS cliente_nome, s.aparelho, s.marca, s.status,
                          s.valor_total, s.data_entrada
                   FROM servicos s
                   JOIN clientes c ON s.cliente_id = c.id
                   WHERE s.status = ?
                   ORDER BY s.data_entrada DESC""",
                (status,)
            )
        else:
            cursor.execute(
                """SELECT s.ra, c.nome AS cliente_nome, s.aparelho, s.marca, s.status,
                          s.valor_total, s.data_entrada
                   FROM servicos s
                   JOIN clientes c ON s.cliente_id = c.id
                   ORDER BY s.data_entrada DESC"""
            )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao listar serviços: {e}")
        return []
    finally:
        conn.close()


def buscar_servicos(query):
    """Busca serviços por RA ou nome do cliente."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        like = f"%{query.strip()}%"
        cursor.execute(
            """SELECT s.ra, c.nome AS cliente_nome, s.aparelho, s.marca, s.status,
                      s.valor_total, s.data_entrada
               FROM servicos s
               JOIN clientes c ON s.cliente_id = c.id
               WHERE s.ra LIKE ? OR c.nome LIKE ?
               ORDER BY s.data_entrada DESC
               LIMIT 50""",
            (like, like)
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha na busca de serviços: {e}")
        return []
    finally:
        conn.close()


def atualizar_status(ra, novo_status):
    """Atualiza o status de um serviço. Preenche data_saida se 'Entregue'."""
    conn = get_connection()
    try:
        if novo_status == "Entregue":
            conn.execute(
                "UPDATE servicos SET status=?, data_saida=DATE('now','localtime') WHERE ra=?",
                (novo_status, ra)
            )
        else:
            conn.execute(
                "UPDATE servicos SET status=?, data_saida='' WHERE ra=?",
                (novo_status, ra)
            )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao atualizar status: {e}")
        return False
    finally:
        conn.close()


def atualizar_servico(ra, servico_realizado="", valor_total=0.0):
    """Atualiza campos editáveis de um serviço."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE servicos SET servico_realizado=?, valor_total=? WHERE ra=?",
            (servico_realizado.strip(), valor_total, ra)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao atualizar serviço: {e}")
        return False
    finally:
        conn.close()


# ──────────────────────────── PEÇAS ────────────────────────────

def adicionar_peca(servico_ra, descricao, valor_unitario=0.0):
    """Adiciona uma peça a um serviço."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO pecas (servico_ra, descricao, valor_unitario) VALUES (?, ?, ?)",
            (servico_ra, descricao.strip(), valor_unitario)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao adicionar peça: {e}")
        return False
    finally:
        conn.close()


def listar_pecas(servico_ra):
    """Lista todas as peças de um serviço."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM pecas WHERE servico_ra = ? ORDER BY id",
            (servico_ra,)
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao listar peças: {e}")
        return []
    finally:
        conn.close()


def remover_peca(peca_id):
    """Remove uma peça por ID."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM pecas WHERE id = ?", (peca_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao remover peça: {e}")
        return False
    finally:
        conn.close()


# ──────────────────────────── DASHBOARD ────────────────────────────

def contar_por_status():
    """Retorna contagem de serviços por status."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT status, COUNT(*) as total FROM servicos
               WHERE status != 'Entregue'
               GROUP BY status"""
        )
        result = {}
        for row in cursor.fetchall():
            result[row["status"]] = row["total"]
        return result
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao contar por status: {e}")
        return {}
    finally:
        conn.close()


def contar_pendentes():
    """Conta serviços com status 'Aberto' ou 'Aguardando Peça'."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as total FROM servicos WHERE status IN ('Aberto', 'Aguardando Peça')"
        )
        row = cursor.fetchone()
        return row["total"] if row else 0
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao contar pendentes: {e}")
        return 0
    finally:
        conn.close()


def contar_prontos():
    """Conta serviços com status 'Pronto'."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM servicos WHERE status = 'Pronto'")
        row = cursor.fetchone()
        return row["total"] if row else 0
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao contar prontos: {e}")
        return 0
    finally:
        conn.close()


# Inicializa o banco ao importar o módulo
if __name__ == "__main__":
    init_db()
    print(f"[OK] Banco de dados inicializado em: {DB_PATH}")
