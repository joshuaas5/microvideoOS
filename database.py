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
    """Cria as tabelas se não existirem e aplica migrações."""
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
                observacoes TEXT DEFAULT '',
                status TEXT DEFAULT 'Aberto',
                valor_total REAL DEFAULT 0.0,
                desconto REAL DEFAULT 0.0,
                valor_final REAL DEFAULT 0.0,
                forma_pagamento TEXT DEFAULT '',
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
        # Migrações - adiciona colunas novas em bancos existentes
        _migrar_colunas(cursor)
        conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao inicializar banco: {e}")
    finally:
        conn.close()


def _migrar_colunas(cursor):
    """Adiciona colunas novas se o banco já existia sem elas."""
    colunas_servicos = {row[1] for row in cursor.execute("PRAGMA table_info(servicos)").fetchall()}
    novas = {
        "desconto": "REAL DEFAULT 0.0",
        "valor_final": "REAL DEFAULT 0.0",
        "forma_pagamento": "TEXT DEFAULT ''",
        "observacoes": "TEXT DEFAULT ''",
    }
    for col, tipo in novas.items():
        if col not in colunas_servicos:
            try:
                cursor.execute(f"ALTER TABLE servicos ADD COLUMN {col} {tipo}")
            except sqlite3.OperationalError:
                pass


# ──────────────────────────── CLIENTES ────────────────────────────

def salvar_cliente(nome, endereco="", telefone="", documento=""):
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
                   numero_serie="", defeito_relatado="", valor_total=0.0,
                   desconto=0.0, valor_final=0.0, forma_pagamento="",
                   observacoes=""):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO servicos
               (ra, cliente_id, aparelho, marca, modelo, numero_serie,
                defeito_relatado, valor_total, desconto, valor_final,
                forma_pagamento, observacoes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ra, cliente_id, aparelho.strip(), marca.strip(), modelo.strip(),
             numero_serie.strip(), defeito_relatado.strip(), valor_total,
             desconto, valor_final, forma_pagamento.strip(), observacoes.strip())
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha ao salvar serviço: {e}")
        return False
    finally:
        conn.close()


def obter_servico(ra):
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
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if status:
            cursor.execute(
                """SELECT s.ra, c.nome AS cliente_nome, s.aparelho, s.marca, s.status,
                          s.valor_total, s.desconto, s.valor_final, s.forma_pagamento,
                          s.data_entrada
                   FROM servicos s
                   JOIN clientes c ON s.cliente_id = c.id
                   WHERE s.status = ?
                   ORDER BY s.data_entrada DESC""",
                (status,)
            )
        else:
            cursor.execute(
                """SELECT s.ra, c.nome AS cliente_nome, s.aparelho, s.marca, s.status,
                          s.valor_total, s.desconto, s.valor_final, s.forma_pagamento,
                          s.data_entrada
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
    conn = get_connection()
    try:
        cursor = conn.cursor()
        like = f"%{query.strip()}%"
        cursor.execute(
            """SELECT s.ra, c.nome AS cliente_nome, s.aparelho, s.marca, s.status,
                      s.valor_total, s.desconto, s.valor_final, s.forma_pagamento,
                      s.data_entrada
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


def atualizar_servico(ra, servico_realizado="", valor_total=0.0,
                      desconto=0.0, valor_final=0.0, forma_pagamento="",
                      observacoes=""):
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE servicos SET servico_realizado=?, valor_total=?,
               desconto=?, valor_final=?, forma_pagamento=?, observacoes=?
               WHERE ra=?""",
            (servico_realizado.strip(), valor_total, desconto, valor_final,
             forma_pagamento.strip(), observacoes.strip(), ra)
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


# ──────────────────────────── FINANCEIRO ────────────────────────────

def resumo_financeiro_mes(ano=None, mes=None):
    """Retorna resumo financeiro de um mês: total faturado, descontos, por forma de pagto."""
    if not ano:
        ano = datetime.now().year
    if not mes:
        mes = datetime.now().month
    mes_str = f"{ano}-{mes:02d}"
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Total faturado
        cursor.execute(
            """SELECT COALESCE(SUM(valor_final), 0) as faturado,
                      COALESCE(SUM(desconto), 0) as descontos,
                      COALESCE(SUM(valor_total), 0) as bruto,
                      COUNT(*) as total_os
               FROM servicos
               WHERE data_entrada LIKE ?""",
            (f"{mes_str}%",)
        )
        row = cursor.fetchone()
        resultado = dict(row) if row else {"faturado": 0, "descontos": 0, "bruto": 0, "total_os": 0}

        # Por forma de pagamento
        cursor.execute(
            """SELECT forma_pagamento, COUNT(*) as qtd, COALESCE(SUM(valor_final), 0) as total
               FROM servicos
               WHERE data_entrada LIKE ? AND forma_pagamento != ''
               GROUP BY forma_pagamento
               ORDER BY total DESC""",
            (f"{mes_str}%",)
        )
        resultado["por_pagamento"] = [dict(r) for r in cursor.fetchall()]
        return resultado
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha no resumo financeiro: {e}")
        return {"faturado": 0, "descontos": 0, "bruto": 0, "total_os": 0, "por_pagamento": []}
    finally:
        conn.close()


def faturamento_ultimos_meses(n=6):
    """Retorna o faturamento dos últimos n meses."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT strftime('%Y-%m', data_entrada) as mes,
                      COALESCE(SUM(valor_final), 0) as total,
                      COUNT(*) as qtd_os
               FROM servicos
               WHERE data_entrada >= date('now', ? || ' months')
               GROUP BY mes
               ORDER BY mes""",
            (f"-{n}",)
        )
        return [dict(r) for r in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"[ERRO DB] Falha no faturamento: {e}")
        return []
    finally:
        conn.close()


# ──────────────────────────── EXPORTAR / IMPORTAR ────────────────────────────

import shutil
import zipfile
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def exportar_dados(destino_zip):
    """Exporta banco, config e PDFs para um arquivo ZIP."""
    try:
        with zipfile.ZipFile(destino_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Banco de dados
            if os.path.exists(DB_PATH):
                zf.write(DB_PATH, "oficina.db")
            # Config
            config_path = os.path.join(BASE_DIR, "config.json")
            if os.path.exists(config_path):
                zf.write(config_path, "config.json")
            # PDFs
            pdf_dir = os.path.join(BASE_DIR, "PDFs")
            if os.path.exists(pdf_dir):
                for f in os.listdir(pdf_dir):
                    fp = os.path.join(pdf_dir, f)
                    if os.path.isfile(fp):
                        zf.write(fp, f"PDFs/{f}")
            # Backups
            bkp_dir = os.path.join(BASE_DIR, "Backups")
            if os.path.exists(bkp_dir):
                for f in os.listdir(bkp_dir):
                    fp = os.path.join(bkp_dir, f)
                    if os.path.isfile(fp):
                        zf.write(fp, f"Backups/{f}")
        return True
    except Exception as e:
        print(f"[ERRO] Exportacao falhou: {e}")
        return False


def importar_dados(zip_path):
    """Importa dados de um ZIP previamente exportado. Sobrescreve o banco atual."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            nomes = zf.namelist()
            # Restaura banco
            if "oficina.db" in nomes:
                zf.extract("oficina.db", BASE_DIR)
            # Restaura config
            if "config.json" in nomes:
                zf.extract("config.json", BASE_DIR)
            # Restaura PDFs
            for n in nomes:
                if n.startswith("PDFs/"):
                    zf.extract(n, BASE_DIR)
                elif n.startswith("Backups/"):
                    zf.extract(n, BASE_DIR)
        return True
    except Exception as e:
        print(f"[ERRO] Importacao falhou: {e}")
        return False


def importar_clientes_csv(csv_path, encoding="utf-8"):
    """
    Importa clientes de um CSV.
    Espera colunas: nome, telefone, documento, endereco (em qualquer ordem).
    Pelo menos a coluna 'nome' deve existir.
    Retorna (importados, duplicados, erros).
    """
    importados = 0
    duplicados = 0
    erros = 0
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Carrega nomes existentes para deduplicar
        cursor.execute("SELECT LOWER(nome) FROM clientes")
        existentes = {row[0] for row in cursor.fetchall()}

        with open(csv_path, 'r', encoding=encoding, errors='replace') as f:
            # Tenta detectar delimitador
            sample = f.read(2048)
            f.seek(0)
            if ';' in sample and ',' not in sample:
                delim = ';'
            elif '\t' in sample:
                delim = '\t'
            else:
                delim = ','

            reader = csv.DictReader(f, delimiter=delim)
            # Normaliza nomes das colunas
            if reader.fieldnames:
                reader.fieldnames = [c.strip().lower().replace(' ', '_') for c in reader.fieldnames]

            for row in reader:
                try:
                    nome = (row.get("nome", "") or "").strip()
                    if not nome:
                        erros += 1
                        continue

                    if nome.lower() in existentes:
                        duplicados += 1
                        continue

                    telefone = (row.get("telefone", "") or row.get("tel", "") or row.get("fone", "") or "").strip()
                    documento = (row.get("documento", "") or row.get("cpf", "") or row.get("cnpj", "") or row.get("doc", "") or "").strip()
                    endereco = (row.get("endereco", "") or row.get("endereço", "") or row.get("end", "") or "").strip()

                    cursor.execute(
                        "INSERT INTO clientes (nome, endereco, telefone, documento) VALUES (?, ?, ?, ?)",
                        (nome, endereco, telefone, documento)
                    )
                    existentes.add(nome.lower())
                    importados += 1
                except Exception:
                    erros += 1

        conn.commit()
    except Exception as e:
        print(f"[ERRO] Importacao CSV falhou: {e}")
        erros += 1
    finally:
        conn.close()

    return importados, duplicados, erros


if __name__ == "__main__":
    init_db()
    print(f"[OK] Banco de dados inicializado em: {DB_PATH}")
