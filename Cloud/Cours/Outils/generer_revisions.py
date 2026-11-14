"""Génère le guide PDF et les données de l’atelier depuis revisions.json.
Usage depuis Cloud/Cours : python Outils/generer_revisions.py (dépendance : reportlab ; Arial ou Liberation Sans).
"""
from pathlib import Path
from html import escape
import json, re
from architectures_pdf import render as render_architectures
from seance24_pdf import render as render_seance24
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, Line, String, PolyLine

ROOT = Path(__file__).resolve().parents[1] / 'Resumes'
D = json.loads((ROOT / 'revisions.json').read_text(encoding='utf8'))
APP = ROOT.parent / 'Atelier'
font_pairs = [
    (Path('C:/Windows/Fonts/arial.ttf'), Path('C:/Windows/Fonts/arialbd.ttf')),
    (Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'),
     Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf')),
    (Path('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'),
     Path('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')),
]
font_pair = next((pair for pair in font_pairs if all(font.is_file() for font in pair)), None)
if font_pair is None:
    raise SystemExit('Installer Arial (Windows) ou Liberation Sans (Linux).')
for name, path in zip(('Arial', 'Arial-Bold'), font_pair):
    pdfmetrics.registerFont(TTFont(name, str(path)))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')
INK, MUTED, ACCENT, RULE, PALE = map(colors.HexColor, ['#182d40','#526575','#1b6c80','#d9e2e8','#edf5f6'])
S = {name: ParagraphStyle(name,fontName=font,fontSize=size,leading=lead,textColor=col,spaceAfter=after,spaceBefore=before) for name,font,size,lead,col,after,before in [
 ('title','Arial-Bold',23,28,INK,15,0),('h','Arial-Bold',12,16,INK,7,12),
 ('p','Arial',9.8,13.8,INK,7,0),('small','Arial',8,11,MUTED,5,0),('cell','Arial',9,12,INK,0,0)]}
S['reference'] = ParagraphStyle('reference', parent=S['small'], spaceAfter=3)
story=[]
def para(text,style='p'):
 text=escape(text).replace('⇒','donc').replace('→',' → ').replace('⌈','plafond(').replace('⌉',')')
 mapping=str.maketrans('₀₁₂₃₄₅₆₇₈₉ₖ₊','0123456789k+')
 text=re.sub('[₀₁₂₃₄₅₆₇₈₉ₖ₊]+',lambda m:'<sub>'+m[0].translate(mapping)+'</sub>',text)
 text=text.replace('ᵏ','<super>k</super>').replace('ⁱ','<super>i</super>')
 return Paragraph(text,S[style])
def add(text,style='p'): story.append(para(text,style))
def heading(text): add(text,'h')
def page(title,sub):
 if story: story.append(PageBreak())
 add('ATELIER CLOUD · GUIDE DE RÉVISION · '+D['date'].upper(),'small')
 title_paragraph = para(title, 'title')
 title_paragraph.guide_heading = title
 story.append(title_paragraph)
 add(sub,'small')
def link(title,url):
 story.append(Paragraph(f'<link href="{escape(url,quote=True)}" color="#1b6c80">{escape(title)} (lien)</link>',S['small']))
def table(rows,widths,padding=7):
 t=Table([[para(c,'cell') for c in row] for row in rows],colWidths=widths,hAlign='LEFT',repeatRows=1)
 t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PALE),('LINEBELOW',(0,0),(-1,-1),.4,RULE),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding)]));story.append(t)
def graph():
 d=Drawing(499,145)
 for i,(x,title,note) in enumerate([(0,'Client','Envoie les requêtes'),(170,'Répartiteur','Oriente vers les VM'),(340,'VM A / VM B','Traitent les demandes')]):
  d.add(Rect(x,65,155,48,fillColor=PALE,strokeColor=RULE));d.add(String(x+77.5,94,title,fontName='Arial-Bold',fontSize=10,fillColor=INK,textAnchor='middle'));d.add(String(x+77.5,78,note,fontName='Arial',fontSize=8,fillColor=MUTED,textAnchor='middle'))
  if i<2:d.add(Line(x+155,89,x+170,89,strokeColor=ACCENT));d.add(String(x+158,92,'>',fontName='Arial',fontSize=10,fillColor=ACCENT))
 d.add(String(0,35,'B arrêté ≠ B détecté ; après retrait de B, A doit absorber toute la demande.',fontName='Arial',fontSize=9,fillColor=INK))
 d.add(String(0,18,'Le répartiteur ne réplique ni les données ni les sessions des VM.',fontName='Arial',fontSize=9,fillColor=MUTED))
 return d

page('Cloud et traitements distribués','Cours 1 et 2 · Notions, examen et préparation des TP')
add(D['scope'])
heading('Ce qui est établi, ce qui reste à confirmer')
for e in D['evidence']: heading(e['label']);add(e['text'])
heading('Un parcours de révision en quatre passages')
for t in [
 '1. Cours 1 : fondations, mise en charge, architectures, Linda et compléments du 24 octobre.',
 '2. Cours 2 : threads, virtualisation, serveurs, migration, RPC, messagerie et diffusion.',
 '3. Entraînement : formules, questions corrigées, exercices repris le 14 novembre et sujet blanc de 90 minutes.',
 '4. Pratique : VM, répartiteur, panne et compte rendu. Les sources figurent à la fin du guide.',
]: add(t)
add('La Fiche 01 illustrée et les modules de l’Atelier complètent ce guide. Les renvois C2 désignent les pages physiques du second PDF, couverture comprise. Le numéro imprimé est supérieur de 34 à partir de la page 9.','small')

grouped_topics = [t for t in D['topics'] if not t.get('standalone')]
for start in range(0,len(grouped_topics),2):
 page(['Fondations du distribué','Tenue en charge et files','Cloud et architectures','P2P, transactions et énergie','Objets, services et conteneurs','Événements et données partagées'][start//2],'Notions vérifiées dans le support ; les compléments sont signalés.')
 for t in grouped_topics[start:start+2]:
  heading(t['title']);add(t['priority']+' · '+t['source'],'small')
  if t['id']=='evenements-espaces':
   table([['Modèle du cours','Temporel','Référentiel'],['Direct','Couplé','Couplé'],['Événement éphémère','Couplé','Découplé'],['Boîte persistante adressée','Découplé','Couplé'],['Espace de tuples conservés','Découplé','Découplé']],[249,125,125]);story.append(Spacer(1,10))
  for text in t['points']:add(text)
  add('Piège : '+t['trap']);add('À savoir faire : '+t['task'],'small')

l = D['linda']
page(l['title'],'Support p. 31–32 · Définition, opérations et exercice corrigé')
add(l['intro']);add(l['tuple'])
heading('Les trois opérations')
table([['Opération','Effet','Attente']] + l['operations'],[85,207,207],padding=4)
add(l['memory'])
heading('Exercice corrigé · espace initialement vide')
add('A et B sont deux processus. Les lignes ci-dessous suivent un ordre proposé ; B peut avancer pendant que A attend.','small')
table([['Instruction','Résultat','Espace après']] + [[t['instruction'],t['result'],t['space']] for t in l['trace']],[152,242,105],padding=4)
heading('Raisonner pour un exercice')
for t in l['pitfalls']:add(t)
add(l['course'],'small');add(l['source'],'small')

render_architectures(D['architectures'],page,add,heading,table,story,link)

render_seance24(D['morning24'],page,add,heading,table,link)

for lesson in D['course2Pages'] + D['morning14']['lessons']:
    page(lesson['title'], lesson['source'])
    for block in lesson['blocks']:
        if block['kind'] == 'table':
            widths = [143, 178, 178] if len(block['rows'][0]) == 3 else [157, 342]
            table(block['rows'], widths, padding=6)
            story.append(Spacer(1, 10))
        elif block['kind'] == 'diagram':
            story.append(Spacer(1, 4))
            table([[block['text']]], [499], padding=10)
            story.append(Spacer(1, 12))
        elif block['kind'] == 'link':
            link(block['title'], block['url'])
        else:
            add(block['text'])

page('Les formules et leurs limites','Support p. 16–17, 26 et 36 ; dimensionnement : application proposée')
table([['Calcul','Formule','Conditions']] + [[f[0],f[1],f[2]] for f in D['formulas']],[104,207,188])
heading('Retrouver la loi stationnaire')
add('λpₖ = μpₖ₊₁ ⇒ pₖ = Uᵏp₀. Pour U < 1 : Σ Uᵏ = 1/(1 − U). Comme Σ pₖ = 1, p₀ = 1 − U. Le nombre moyen est L = U/(1 − U), puis Little donne R = L/λ = 1/(μ − λ), pour λ > 0. À demande nulle, le temps d’une requête isolée tend vers S.')
heading('La proximité de la saturation')
d=Drawing(499,170)
x0,y0,w,h=42,28,400,115
d.add(Line(x0,y0,x0+w,y0,strokeColor=MUTED));d.add(Line(x0,y0,x0,y0+h,strokeColor=MUTED))
for u in [0,.5,.8,.9]:
 x=x0+w*u/.9;d.add(String(x,y0-14,f'{round(u*100)} %',fontName='Arial',fontSize=8,textAnchor='middle',fillColor=MUTED))
for value in [1,5,10]:
 y=y0+h*value/10;d.add(Line(x0,y,x0+w,y,strokeColor=RULE));d.add(String(x0-7,y-3,str(value),fontName='Arial',fontSize=8,textAnchor='end',fillColor=MUTED))
coords=[]
for i in range(91):u=i/100;coords.extend([x0+w*u/.9,y0+h/(1-u)/10])
d.add(PolyLine(coords,strokeColor=ACCENT,strokeWidth=2));d.add(String(0,155,'Rapport R/S (×) ; abscisse : utilisation U',fontName='Arial-Bold',fontSize=9,fillColor=INK));story.append(d)
add('À 80 % : R = 5S ; à 90 % : R = 10S ; à 99 % : R = 100S (hors graphique). Il faut une marge de capacité, pas seulement une égalité entre arrivées et capacité.','small')
heading('Verticale et horizontale : ne pas comparer sans hypothèses')
add('Si la capacité verticale est multipliée par f : R = 1/(fμ − λ). Pour n files M/M/1 séparées avec répartition uniforme : R = 1/(μ − λ/n). Ces modèles idéaux négligent réseau, coordination et goulots communs ; ils ne décrivent pas une file unique M/M/n.')

questions_per_page = 4
question_pages = (len(D['questions']) + questions_per_page - 1) // questions_per_page
for start in range(0, len(D['questions']), questions_per_page):
 page(f"Questions corrigées · {start // questions_per_page + 1}/{question_pages}",'Entraînements proposés ; aucune question précise annoncée comme sujet officiel')
 for i,q in enumerate(D['questions'][start:start+questions_per_page],start+1):
  heading(str(i)+' · '+q['q']);add(q['category']+' · '+q['source'],'small');add(q['a'])
 add('Méthode : rédiger une réponse sans aide, puis vérifier le raisonnement et les unités. Les corrections sont masquées au départ dans l’application.','small')

page('Sujet blanc · 45 minutes','Barème d’entraînement proposé /20 ; durée et répartition non officielles')
add('Prévoir papier et calculatrice pour l’entraînement. Vérifier auprès de l’enseignant le matériel réellement autorisé à l’examen. Écrire les hypothèses, montrer les conversions, puis commenter les résultats.')
for m in D['mock'][:4]:
 heading(m['title']);add(m['prompt'])
heading('Correction et autoévaluation')
for m in D['mock'][:4]:add(m['title']+' : '+m['rubric'])
add('Pour A : application → middleware → OS → matériel sur chaque machine ; panne partielle et incertitude d’un timeout ; deux transparences illustrées avec leurs limites. Pour D : le répartiteur oriente les requêtes, la réplication duplique des données ; observer erreurs, latence et état des backends avant/pendant/après la panne.')
heading('Avant de rendre')
add('Résultats avec unités ? Stabilité contrôlée ? L compte-t-il bien l’attente et le traitement ? Arrondi du nombre de machines au supérieur ? Solution architecturale justifiée par un goulot identifié ? Les limites du modèle sont-elles écrites ?')

page('Entraînement complémentaire · Cours 2','Exercice proposé · Hors barème du sujet blanc')
for exercise in D['mock'][4:]:
    heading(exercise['title'])
    add(exercise['prompt'])
    heading('Correction')
    add(exercise['rubric'])
heading('Relier les deux supports')
add('Comparer le délai d’un appel RPC, l’attente dans une file et le retard de propagation d’une copie. '
    'Identifier qui attend, quel événement marque la fin de l’attente et ce que voit le client si un nœud tombe.')
heading('Vérifier les deux calculs du cours 2')
add('TLP : calculer le nombre de threads simultanés en moyenne, puis diviser par la fraction du temps avec au moins un thread actif.')
add('Pull : sous l’hypothèse de tirages indépendants et uniformes, un nœud reste ignorant si lui-même et le pair choisi le sont, soit p².')

mock = D['morning14']['mock90']
page('Sujet blanc · 90 minutes','Énoncé · Barème et temps par exercice proposés')
add(mock['intro'])
for exercise in mock['exercises']:
    heading(exercise['title'])
    add(exercise['prompt'])
page('Sujet blanc · Corrigé','Réponses courtes et critères de correction')
for exercise in mock['exercises']:
    heading(exercise['title'])
    add(exercise['rubric'])

for start in [0,3]:
 page('TP · '+('Construire et observer' if start==0 else 'Tester et expliquer'),'Préparation proposée du TP évoqué à l’oral : machines virtuelles et load balancing sur Google Cloud')
 if start==0:story.append(graph())
 for l in D['labs'][start:start+3]:
  heading(l['title']);add(l['action']);add('Preuve attendue : '+l['proof'],'small');add('Question possible : '+l['question'])
 if start==3:
  heading('Corriger le diagnostic')
  add('Service local OK mais accès distant KO : vérifier écoute/interface, port, pare-feu et routage. Backend unhealthy : vérifier chemin/port de sonde, réponse de l’application et accès réseau des sondes. Le retrait d’un backend ne prouve pas que les sessions et données ont survécu.')
  add('À λ = 160 req/s et μ = 100 req/s : deux VM idéales sont chacune à 80 %. Après perte d’une VM, le survivant serait à 160 % : aucun régime stationnaire stable. La disponibilité du processus ne suffit pas à garantir un service acceptable.')

page('Livre et sources','Traçabilité et limites de cette consolidation')
heading(D['book']['title']);add(D['book']['text']);link('Livre, slides et demande de copie numérique',D['book']['url'])
for c in D['book']['chapters']:add(c,'reference')
add(D['book']['reading'])
page('Sources du cours','Supports, transcriptions et documentation')
for s in D['sources']:
 add(s['title']+' — '+s['detail'],'reference')
 if s.get('url') and s['url']!=D['book']['url']:link(s['title'],s['url'])
add('Pour enrichir le cours : mettre à jour Resumes/revisions.json, puis exécuter python Outils/generer_revisions.py depuis Cloud/Cours. Le PDF et revision-data.js sont régénérés ensemble. Ajouter un repère de source à chaque nouvelle notion.','small')

class GuideDocument(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        title = getattr(flowable, 'guide_heading', None)
        if title:
            key = f'guide-{self.page}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key)


def footer(c,doc):
 c.saveState();c.setStrokeColor(RULE);c.line(48,41,547,41);c.setFont('Arial',8);c.setFillColor(MUTED);c.drawString(48,27,'Atelier Cloud · Révision et TP · '+D['date']);c.drawRightString(547,27,str(doc.page));c.restoreState()

out=ROOT/'Guide_revision_Cloud_examen_TP.pdf'
GuideDocument(str(out),pagesize=(595.28,841.89),rightMargin=48,leftMargin=48,topMargin=40,bottomMargin=55,title='Cloud et traitements distribués — Cours 1 et 2',author='Atelier Cloud').build(story,onFirstPage=footer,onLaterPages=footer)
(APP/'guide-revision.pdf').write_bytes(out.read_bytes())
(APP / 'revision-data.js').write_text('window.CloudStudy = ' + json.dumps(D, ensure_ascii=False, indent=2) + ';\n', encoding='utf8')
print(out)
