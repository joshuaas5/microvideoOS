# -*- coding: utf-8 -*-
"""
backup.py — Módulo de backup automático
Sistema Oficina 2026
"""

import os
import shutil
import glob
from datetime import datetime

# Caminhos relativos ao diretório do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "oficina.db")
BACKUP_DIR = os.path.join(BASE_DIR, "Backups")
MAX_BACKUPS = 30


def realizar_backup():
    """
    Copia oficina.db para Backups/oficina_YYYY-MM-DD.db.
    Mantém apenas os últimos MAX_BACKUPS arquivos.
    Retorna True se o backup foi realizado, False se já existe backup do dia ou houve erro.
    """
    try:
        # Verifica se o banco existe
        if not os.path.exists(DB_PATH):
            print("[BACKUP] Banco de dados não encontrado. Pulando backup.")
            return False

        # Cria pasta de backups se necessário
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            print(f"[BACKUP] Pasta criada: {BACKUP_DIR}")

        # Nome do arquivo de backup
        hoje = datetime.now().strftime("%Y-%m-%d")
        backup_filename = f"oficina_{hoje}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        # Verifica se já fez backup hoje
        if os.path.exists(backup_path):
            print(f"[BACKUP] Backup de hoje já existe: {backup_filename}")
            return False

        # Realiza a cópia
        shutil.copy2(DB_PATH, backup_path)
        print(f"[BACKUP] ✓ Backup realizado: {backup_filename}")

        # Rotação: manter apenas os últimos MAX_BACKUPS
        _limpar_backups_antigos()

        return True

    except Exception as e:
        print(f"[BACKUP] ✗ Erro ao realizar backup: {e}")
        return False


def _limpar_backups_antigos():
    """Remove backups excedentes, mantendo apenas os MAX_BACKUPS mais recentes."""
    try:
        backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "oficina_*.db")))
        if len(backups) > MAX_BACKUPS:
            excedentes = backups[:len(backups) - MAX_BACKUPS]
            for arquivo in excedentes:
                os.remove(arquivo)
                print(f"[BACKUP] Removido backup antigo: {os.path.basename(arquivo)}")
    except Exception as e:
        print(f"[BACKUP] Erro na limpeza de backups: {e}")


if __name__ == "__main__":
    realizar_backup()
