"""Build a compact standalone PDF from the reviewed Markdown report source."""
import html,re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/NyAI_Research_Work_Sample_2026-10-25.pdf'


def inline(text):
    text=html.escape(text)
    text=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',text)
    return text


def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#CBD5E1'))
    canvas.line(43,39,A4[0]-43,39)
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#475569'))
    canvas.drawString(43,26,'NyAI | Preliminary research pilot | 25 October 2026')
    canvas.drawRightString(A4[0]-43,26,str(doc.page))


if __name__=='__main__':
    OUT.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle',fontName='Helvetica-Bold',fontSize=23,leading=27,spaceAfter=14,textColor=colors.HexColor('#102A43')))
    styles.add(ParagraphStyle(name='ReportHeading',fontName='Helvetica-Bold',fontSize=12.5,leading=16,spaceBefore=10,spaceAfter=7,textColor=colors.HexColor('#102A43'),keepWithNext=True))
    styles.add(ParagraphStyle(name='ReportBody',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=9,splitLongWords=True))
    styles.add(ParagraphStyle(name='Cell',fontName='Helvetica',fontSize=8,leading=11,spaceAfter=0))
    source=(ROOT/'docs/work-sample.md').read_text()
    blocks=source.split('\n\n');story=[]
    for block in blocks:
        block=block.strip()
        if not block:continue
        if block=='<!-- pagebreak -->':story.append(PageBreak());continue
        if block.startswith('# '):story.append(Paragraph(inline(block[2:]),styles['ReportTitle']));continue
        if block.startswith('## '):story.append(Paragraph(inline(block[3:]),styles['ReportHeading']));continue
        if block.startswith('|'):
            data=[]
            for line in block.splitlines():
                cells=[c.strip() for c in line.strip('|').split('|')]
                if all(re.fullmatch(r'[-: ]+',c) for c in cells):continue
                data.append([Paragraph(inline(c),styles['Cell']) for c in cells])
            width=A4[0]-86;n=len(data[0])
            widths=([width*.23]+[width*.77/(n-1)]*(n-1)) if n>1 else [width]
            table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7EEF5')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#829AB1')),
                ('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#D9E2EC')),
                ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([table,Spacer(1,10)]);continue
        story.append(Paragraph(inline(block.replace('\n',' ')),styles['ReportBody']))
    doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=43,leftMargin=43,topMargin=42,bottomMargin=51,
        title='NyAI evidence validation and checkable oversight',author='Hrishikesh Wattamwar; prepared with AI assistance')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(OUT)
