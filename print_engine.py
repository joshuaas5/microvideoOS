# -*- coding: utf-8 -*-
"""
print_engine.py — Módulo de impressão de OS em PDF (ReportLab)
Sistema Oficina 2026

Gera PDF A4 com duas vias: Via da Loja (superior) e Via do Cliente (inferior),
separadas por linha tracejada.
"""

import os
import sys
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, grey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate
)
from reportlab.pdfgen import canvas
from database import obter_servico, listar_pecas

# ──────────────────────────── CONSTANTES ────────────────────────────

PAGE_W, PAGE_H = A4  # 210mm x 297mm
HALF_H = PAGE_H / 2
MARGIN = 15 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

# Cores
COR_AZUL = HexColor("#1a3a5c")
COR_CINZA = HexColor("#666666")
COR_FUNDO_HEADER = HexColor("#e8eef5")

# Dados da empresa (personalizável)
EMPRESA = {
    "nome": "ELETRÔNICA EXEMPLO",
    "endereco": "Rua Exemplo, 123 — Centro — Cidade/UF",
    "telefone": "(00) 0000-0000",
    "cnpj": "00.000.000/0001-00",
}

TERMO_GARANTIA = (
    "TERMO DE GARANTIA: A garantia dos serviços é de 90 (noventa) dias, contados a partir da data de entrega, "
    "conforme o Código de Defesa do Consumidor (Lei 8.078/90). A garantia não cobre defeitos causados por mau uso, "
    "quedas, oscilação de energia ou violação do aparelho por terceiros. Aparelhos não retirados em até 90 dias "
    "após a comunicação de conclusão do serviço serão considerados abandonados, conforme Art. 1.275 do Código Civil."
)

# Diretório de saída dos PDFs
PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PDFs")


def _garantir_diretorio():
    """Cria o diretório de PDFs se necessário."""
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)


def gerar_pdf_ra(ra_numero):
    """
    Gera o PDF da Ordem de Serviço com duas vias (Loja + Cliente).
    Retorna o caminho do PDF gerado ou None em caso de erro.
    """
    try:
        # Busca dados
        servico = obter_servico(ra_numero)
        if not servico:
            print(f"[PDF] ✗ Serviço RA {ra_numero} não encontrado.")
            return None

        pecas = listar_pecas(ra_numero)

        _garantir_diretorio()
        pdf_path = os.path.join(PDF_DIR, f"OS_{ra_numero}.pdf")

        # Cria canvas
        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.setTitle(f"Ordem de Serviço — RA {ra_numero}")

        # Desenha as duas vias
        _desenhar_via(c, servico, pecas, y_offset=HALF_H, via_label="VIA DA LOJA")
        _desenhar_via(c, servico, pecas, y_offset=0, via_label="VIA DO CLIENTE")

        # Linha tracejada central
        c.setStrokeColor(grey)
        c.setDash(6, 3)
        c.setLineWidth(0.8)
        c.line(MARGIN, HALF_H, PAGE_W - MARGIN, HALF_H)

        # Texto de corte
        c.setFont("Helvetica", 7)
        c.setFillColor(grey)
        c.drawCentredString(PAGE_W / 2, HALF_H + 2, "✂  Corte aqui  ✂")

        c.save()
        print(f"[PDF] ✓ PDF gerado: {pdf_path}")

        # Abre o PDF automaticamente
        _abrir_pdf(pdf_path)

        return pdf_path

    except Exception as e:
        print(f"[PDF] ✗ Erro ao gerar PDF: {e}")
        return None


def _desenhar_via(c, servico, pecas, y_offset, via_label):
    """Desenha uma via completa (metade da página)."""
    x = MARGIN
    y_top = y_offset + HALF_H - MARGIN  # Topo da área de conteúdo
    y = y_top

    # ─── CABEÇALHO ───
    # Fundo do header
    header_h = 22 * mm
    c.setFillColor(COR_FUNDO_HEADER)
    c.rect(x, y - header_h, CONTENT_W, header_h, fill=1, stroke=0)

    # Nome da empresa
    c.setFillColor(COR_AZUL)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x + 5 * mm, y - 7 * mm, EMPRESA["nome"])

    # Dados da empresa
    c.setFont("Helvetica", 7)
    c.setFillColor(COR_CINZA)
    c.drawString(x + 5 * mm, y - 12 * mm, f'{EMPRESA["endereco"]}  |  Tel: {EMPRESA["telefone"]}')
    c.drawString(x + 5 * mm, y - 16 * mm, f'CNPJ: {EMPRESA["cnpj"]}')

    # Via label (direita)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(COR_AZUL)
    c.drawRightString(x + CONTENT_W - 5 * mm, y - 7 * mm, via_label)

    y -= header_h + 4 * mm

    # ─── RA EM DESTAQUE ───
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(COR_AZUL)
    c.drawString(x, y, f"RA: {servico['ra']}")

    # Data e Status (à direita)
    c.setFont("Helvetica", 9)
    c.setFillColor(black)
    c.drawRightString(x + CONTENT_W, y + 2 * mm, f"Data: {servico.get('data_entrada', '')}")
    c.drawRightString(x + CONTENT_W, y - 4 * mm, f"Status: {servico.get('status', '')}")

    y -= 12 * mm

    # ─── DADOS DO CLIENTE ───
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(COR_AZUL)
    c.drawString(x, y, "DADOS DO CLIENTE")
    y -= 4 * mm

    c.setFont("Helvetica", 8)
    c.setFillColor(black)
    cliente_info = [
        f"Nome: {servico.get('cliente_nome', '')}",
        f"Telefone: {servico.get('cliente_telefone', '')}    Doc: {servico.get('cliente_documento', '')}",
        f"Endereço: {servico.get('cliente_endereco', '')}",
    ]
    for info in cliente_info:
        c.drawString(x, y, info)
        y -= 3.5 * mm

    y -= 2 * mm

    # ─── DADOS DO APARELHO ───
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(COR_AZUL)
    c.drawString(x, y, "DADOS DO APARELHO")
    y -= 4 * mm

    c.setFont("Helvetica", 8)
    c.setFillColor(black)
    aparelho_info = [
        f"Aparelho: {servico.get('aparelho', '')}    Marca: {servico.get('marca', '')}    Modelo: {servico.get('modelo', '')}",
        f"Nº Série: {servico.get('numero_serie', '')}",
        f"Defeito: {servico.get('defeito_relatado', '')}",
    ]
    for info in aparelho_info:
        c.drawString(x, y, info)
        y -= 3.5 * mm

    y -= 2 * mm

    # ─── TABELA DE PEÇAS / SERVIÇOS ───
    if pecas:
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(COR_AZUL)
        c.drawString(x, y, "PEÇAS / SERVIÇOS")
        y -= 4 * mm

        # Cabeçalho da tabela
        col_widths = [CONTENT_W * 0.7, CONTENT_W * 0.3]
        data = [["Descrição", "Valor (R$)"]]
        for peca in pecas:
            data.append([
                peca.get("descricao", ""),
                f"{peca.get('valor_unitario', 0):.2f}"
            ])

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TEXTCOLOR", (0, 0), (-1, 0), COR_AZUL),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, COR_AZUL),
            ("LINEBELOW", (0, -1), (-1, -1), 0.3, grey),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))

        tw, th = table.wrap(CONTENT_W, HALF_H)
        table.drawOn(c, x, y - th)
        y -= th + 3 * mm

    # ─── VALOR TOTAL ───
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(COR_AZUL)
    valor = servico.get("valor_total", 0) or 0
    c.drawRightString(x + CONTENT_W, y, f"VALOR TOTAL: R$ {valor:.2f}")
    y -= 8 * mm

    # ─── SERVIÇO REALIZADO ───
    servico_realizado = servico.get("servico_realizado", "")
    if servico_realizado:
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(COR_AZUL)
        c.drawString(x, y, "SERVIÇO REALIZADO:")
        y -= 3 * mm
        c.setFont("Helvetica", 7)
        c.setFillColor(black)
        c.drawString(x, y, servico_realizado[:120])
        y -= 5 * mm

    # ─── ASSINATURA ───
    sig_y = y_offset + MARGIN + 18 * mm
    c.setStrokeColor(black)
    c.setDash(1, 0)
    c.setLineWidth(0.4)
    c.line(x, sig_y, x + 70 * mm, sig_y)
    c.line(x + 80 * mm, sig_y, x + CONTENT_W, sig_y)

    c.setFont("Helvetica", 7)
    c.setFillColor(COR_CINZA)
    c.drawString(x, sig_y - 3 * mm, "Assinatura do Cliente")
    c.drawString(x + 80 * mm, sig_y - 3 * mm, "Assinatura da Loja")

    # ─── TERMO DE GARANTIA ───
    c.setFont("Helvetica", 5)
    c.setFillColor(COR_CINZA)
    termo_y = y_offset + MARGIN + 2 * mm
    # Quebra o termo em linhas de ~130 chars
    linhas_termo = _quebrar_texto(TERMO_GARANTIA, 160)
    for lt in linhas_termo:
        c.drawString(x, termo_y, lt)
        termo_y -= 2.5 * mm


def _quebrar_texto(texto, max_chars):
    """Quebra texto em linhas de no máximo max_chars caracteres, respeitando palavras."""
    palavras = texto.split()
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= max_chars:
            linha_atual += (" " if linha_atual else "") + palavra
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    return linhas


def _abrir_pdf(pdf_path):
    """Abre o PDF com o visualizador padrão do sistema."""
    try:
        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", pdf_path])
        else:
            subprocess.Popen(["xdg-open", pdf_path])
    except Exception as e:
        print(f"[PDF] Não foi possível abrir o PDF automaticamente: {e}")


if __name__ == "__main__":
    # Teste direto
    if len(sys.argv) > 1:
        ra = sys.argv[1]
        gerar_pdf_ra(ra)
    else:
        print("Uso: python print_engine.py <RA>")
