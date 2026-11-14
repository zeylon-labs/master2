"""Génère les deux PDF d’examen depuis les sources Markdown de Resumes/.

Usage: python Cloud/Cours/Outils/generer_fiches_examen.py (ReportLab et DejaVu Sans ou Arial).
"""

from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Table, TableStyle


COURSE = Path(__file__).resolve().parents[1]
DOCUMENTS = ('Guide_Cloud_Examen_Mi_Decembre', 'Fiche_Formules_Maths_Cloud')
INK = colors.HexColor('#152c3c')
TEAL = colors.HexColor('#056f69')
MUTED = colors.HexColor('#465e6d')
PALE = colors.HexColor('#eaf4f3')
RULE = colors.HexColor('#ccdcde')


def register_fonts():
    locations = (
        (Path('/usr/share/fonts/truetype/dejavu'), 'DejaVuSans.ttf', 'DejaVuSans-Bold.ttf'),
        (Path('C:/Windows/Fonts'), 'arial.ttf', 'arialbd.ttf'),
    )
    for folder, normal, bold in locations:
        if (folder / normal).is_file() and (folder / bold).is_file():
            pdfmetrics.registerFont(TTFont('Revision', str(folder / normal)))
            pdfmetrics.registerFont(TTFont('RevisionBold', str(folder / bold)))
            pdfmetrics.registerFontFamily('Revision', normal='Revision', bold='RevisionBold')
            symbol_font = folder / 'seguisym.ttf' if normal == 'arial.ttf' else folder / normal
            pdfmetrics.registerFont(TTFont('RevisionSymbols', str(symbol_font)))
            return
    raise SystemExit('Installer DejaVu Sans ou Arial.')


def make_styles(compact):
    body = ParagraphStyle('body', fontName='Revision', fontSize=9.6 if compact else 10,
                          leading=13.1 if compact else 14.5, textColor=INK, spaceAfter=7)
    return {
        'h1': ParagraphStyle('h1', parent=body, fontName='RevisionBold', fontSize=25,
                              leading=30, spaceAfter=10, keepWithNext=True),
        'h2': ParagraphStyle('h2', parent=body, fontName='RevisionBold', textColor=TEAL,
                              fontSize=13, leading=17, spaceBefore=8, spaceAfter=6,
                              keepWithNext=True),
        'body': body,
        'note': ParagraphStyle('note', parent=body, textColor=MUTED, fontSize=8.4, leading=11.6),
        'callout': ParagraphStyle('callout', parent=body, borderColor=RULE, borderWidth=0.5,
                                   borderPadding=7, backColor=PALE, spaceBefore=6, spaceAfter=12),
        'list': ParagraphStyle('list', parent=body, leftIndent=16, firstLineIndent=-16),
        'cell': ParagraphStyle('cell', parent=body, fontSize=8.8 if compact else 9.2,
                               leading=11.9 if compact else 12.8, spaceAfter=0),
    }


def markup(line):
    line = escape(line)
    line = line.replace('∪', '<font name="RevisionSymbols">∪</font>')
    line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
    line = re.sub(r'`([^`]+)`', r'<b>\1</b>', line)
    for chars, values, tag in (
        ('₀₁₂₃₄₅₆₇₈₉ₐᵢⱼₖ₊', '0123456789aijk+', 'sub'),
        ('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁽⁾ᴺᵈᵏᵐʲᵖ', '0123456789-()Ndkmjp', 'super'),
    ):
        mapping = str.maketrans(chars, values)
        line = re.sub(f'[{chars}]+', lambda m: f'<{tag}>{m[0].translate(mapping)}</{tag}>', line)
    return line


def table_flowable(block, styles, width):
    rows = [[value.strip() for value in line.strip('|').split('|')] for line in block.splitlines()]
    headings, entries = rows[0], rows[2:]
    fractions = (0.29, 0.71) if len(headings) == 2 else (0.35, 0.25, 0.40)
    table = Table(
        [[Paragraph(f'<b>{markup(cell)}</b>' if row == 0 else markup(cell), styles['cell'])
          for cell in cells] for row, cells in enumerate([headings, *entries])],
        colWidths=[width * part for part in fractions], repeatRows=1, spaceAfter=9,
    )
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PALE),
        ('LINEBELOW', (0, 0), (-1, -1), 0.45, RULE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return table


def contents(source, styles, width):
    for block in source.strip().split('\n\n'):
        if block == '<!-- page -->':
            yield PageBreak()
        elif block.startswith('|'):
            yield table_flowable(block, styles, width)
        elif re.match(r'(?:- |\d+\. )', block):
            for line in block.splitlines():
                yield Paragraph(markup(re.sub(r'^- ', '• ', line)), styles['list'])
        else:
            style = 'body'
            if block.startswith('# '):
                style, block = 'h1', block[2:]
            elif block.startswith('## '):
                style, block = 'h2', block[3:]
            elif block.startswith('> '):
                style, block = 'callout', block[2:]
            elif block.startswith(('Références · ', 'Sources · ')):
                style = 'note'
            yield Paragraph(markup(block), styles[style])


def page_footer(canvas, doc):
    canvas.setStrokeColor(RULE)
    canvas.line(doc.leftMargin, 39, A4[0] - doc.rightMargin, 39)
    canvas.setFillColor(MUTED)
    canvas.setFont('Revision', 8)
    canvas.drawString(doc.leftMargin, 25, 'Master DSICS  ·  Cloud et traitements distribués')
    canvas.drawRightString(A4[0] - doc.rightMargin, 25, str(doc.page))


def main():
    register_fonts()
    for name in DOCUMENTS:
        source = (COURSE / 'Resumes' / f'{name}.md').read_text(encoding='utf-8')
        output = COURSE / 'Atelier' / f'{name}.pdf'
        doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=42, rightMargin=42,
                                topMargin=40, bottomMargin=52, pageCompression=True,
                                title=source.splitlines()[0][2:], author='Master DSICS', invariant=True)
        doc.build(list(contents(source, make_styles(name.startswith('Fiche')), doc.width - 12)),
                  onFirstPage=page_footer, onLaterPages=page_footer)
        print(output)


if __name__ == '__main__':
    main()
