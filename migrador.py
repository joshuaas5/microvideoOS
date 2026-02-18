# -*- coding: utf-8 -*-
"""
migrador.py — Script de migração de dados legados (CSV → SQLite)
Sistema Oficina 2026

Uso:
    python migrador.py clientes.csv servicos.csv
"""

import csv
import sys
import os
from database import get_connection, init_db


def limpar_string(valor):
    """Remove espaços extras e normaliza maiúsculas."""
    if valor is None:
        return ""
    return " ".join(valor.strip().split()).upper()


def importar_clientes(csv_path):
    """
    Importa clientes de um CSV.
    Colunas esperadas: nome, endereco, telefone, documento
    Deduplicação por telefone ou nome.
    """
    if not os.path.exists(csv_path):
        print(f"[MIGRADOR] ✗ Arquivo não encontrado: {csv_path}")
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    importados = 0
    duplicados = 0

    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")

            # Normaliza nomes das colunas
            if reader.fieldnames:
                reader.fieldnames = [col.strip().lower() for col in reader.fieldnames]

            for row in reader:
                try:
                    nome = limpar_string(row.get("nome", ""))
                    endereco = limpar_string(row.get("endereco", ""))
                    telefone = limpar_string(row.get("telefone", ""))
                    documento = limpar_string(row.get("documento", ""))

                    if not nome:
                        continue

                    # Verifica duplicata por telefone (se houver) ou nome
                    if telefone:
                        cursor.execute(
                            "SELECT id FROM clientes WHERE telefone = ?", (telefone,)
                        )
                    else:
                        cursor.execute(
                            "SELECT id FROM clientes WHERE nome = ?", (nome,)
                        )

                    if cursor.fetchone():
                        duplicados += 1
                        continue

                    cursor.execute(
                        "INSERT INTO clientes (nome, endereco, telefone, documento) VALUES (?, ?, ?, ?)",
                        (nome, endereco, telefone, documento)
                    )
                    importados += 1

                except Exception as e:
                    print(f"[MIGRADOR] Erro na linha: {e}")
                    continue

        conn.commit()
        print(f"[MIGRADOR] ✓ Clientes importados: {importados} | Duplicados ignorados: {duplicados}")
        return importados

    except Exception as e:
        print(f"[MIGRADOR] ✗ Erro ao importar clientes: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()


def importar_servicos(csv_path):
    """
    Importa serviços de um CSV.
    Colunas esperadas: ra, cliente_nome, aparelho, marca, modelo,
                       numero_serie, defeito_relatado, status, valor_total, data_entrada
    Vincula ao cliente pelo nome. Cria o cliente se não existir.
    """
    if not os.path.exists(csv_path):
        print(f"[MIGRADOR] ✗ Arquivo não encontrado: {csv_path}")
        return 0

    conn = get_connection()
    cursor = conn.cursor()
    importados = 0
    erros = 0

    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")

            if reader.fieldnames:
                reader.fieldnames = [col.strip().lower() for col in reader.fieldnames]

            for row in reader:
                try:
                    ra = limpar_string(row.get("ra", ""))
                    cliente_nome = limpar_string(row.get("cliente_nome", ""))
                    aparelho = limpar_string(row.get("aparelho", ""))
                    marca = limpar_string(row.get("marca", ""))
                    modelo = limpar_string(row.get("modelo", ""))
                    numero_serie = limpar_string(row.get("numero_serie", ""))
                    defeito = limpar_string(row.get("defeito_relatado", ""))
                    status = limpar_string(row.get("status", "ABERTO"))
                    data_entrada = row.get("data_entrada", "").strip()

                    try:
                        valor_total = float(row.get("valor_total", "0").replace(",", "."))
                    except ValueError:
                        valor_total = 0.0

                    if not ra or not cliente_nome:
                        erros += 1
                        continue

                    # Normaliza status
                    status_map = {
                        "ABERTO": "Aberto",
                        "AGUARDANDO PEÇA": "Aguardando Peça",
                        "AGUARDANDO PECA": "Aguardando Peça",
                        "PRONTO": "Pronto",
                        "ENTREGUE": "Entregue",
                    }
                    status = status_map.get(status, "Aberto")

                    # Busca ou cria cliente
                    cursor.execute(
                        "SELECT id FROM clientes WHERE nome = ?", (cliente_nome,)
                    )
                    cliente_row = cursor.fetchone()
                    if cliente_row:
                        cliente_id = cliente_row["id"]
                    else:
                        cursor.execute(
                            "INSERT INTO clientes (nome) VALUES (?)", (cliente_nome,)
                        )
                        cliente_id = cursor.lastrowid

                    # Verifica se RA já existe
                    cursor.execute("SELECT ra FROM servicos WHERE ra = ?", (ra,))
                    if cursor.fetchone():
                        erros += 1
                        continue

                    cursor.execute(
                        """INSERT INTO servicos
                           (ra, cliente_id, aparelho, marca, modelo, numero_serie,
                            defeito_relatado, status, valor_total, data_entrada)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (ra, cliente_id, aparelho, marca, modelo, numero_serie,
                         defeito, status, valor_total, data_entrada)
                    )
                    importados += 1

                except Exception as e:
                    print(f"[MIGRADOR] Erro na linha: {e}")
                    erros += 1
                    continue

        conn.commit()
        print(f"[MIGRADOR] ✓ Serviços importados: {importados} | Erros/Duplicados: {erros}")
        return importados

    except Exception as e:
        print(f"[MIGRADOR] ✗ Erro ao importar serviços: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()


def main():
    """Ponto de entrada CLI."""
    print("=" * 60)
    print("  MIGRADOR — Sistema Oficina 2026")
    print("=" * 60)

    # Inicializa o banco
    init_db()

    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python migrador.py clientes.csv")
        print("  python migrador.py clientes.csv servicos.csv")
        print("\nFormato CSV: separador ';', encoding UTF-8")
        print("\nColunas para clientes.csv:")
        print("  nome;endereco;telefone;documento")
        print("\nColunas para servicos.csv:")
        print("  ra;cliente_nome;aparelho;marca;modelo;numero_serie;defeito_relatado;status;valor_total;data_entrada")
        return

    # Primeiro argumento: CSV de clientes
    if len(sys.argv) >= 2:
        print(f"\n→ Importando clientes de: {sys.argv[1]}")
        importar_clientes(sys.argv[1])

    # Segundo argumento (opcional): CSV de serviços
    if len(sys.argv) >= 3:
        print(f"\n→ Importando serviços de: {sys.argv[2]}")
        importar_servicos(sys.argv[2])

    print("\n✓ Migração concluída!")


if __name__ == "__main__":
    main()
