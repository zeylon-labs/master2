"""Dessins vectoriels de comparaison, depuis les mêmes données que l'Atelier."""
import math
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.shapes import Drawing,Rect,Line,String,Polygon

INK=colors.HexColor('#182d40');MUTED=colors.HexColor('#526575');RULE=colors.HexColor('#b7bec1');PALE=colors.HexColor('#edf5f6')

def diagram(mode):
    factor=499/900
    d=Drawing(499,300*factor)
    def xy(x,y):return x*factor,(300-y)*factor
    def arrow(x1,y1,x2,y2,both=False):
        a,b=xy(x1,y1),xy(x2,y2);d.add(Line(*a,*b,strokeColor=MUTED,strokeWidth=.8))
        def head(p,q):
            angle=math.atan2(q[1]-p[1],q[0]-p[0]);k=4
            d.add(Polygon([q[0],q[1],q[0]-k*math.cos(angle-.45),q[1]-k*math.sin(angle-.45),q[0]-k*math.cos(angle+.45),q[1]-k*math.sin(angle+.45)],fillColor=MUTED,strokeColor=None))
        head(a,b)
        if both:head(b,a)
    for edge in mode['edges']:
        a=next(n for n in mode['nodes'] if n['id']==edge['source']);b=next(n for n in mode['nodes'] if n['id']==edge['target'])
        ax,ay=a['x']+a['w']/2,a['y']+32;bx,by=b['x']+b['w']/2,b['y']+32
        dx,dy=bx-ax,by-ay
        if abs(dx)>abs(dy):
            sign=1 if dx>0 else -1;arrow(ax+sign*a['w']/2,ay,bx-sign*b['w']/2,by,edge['both'])
        else:
            sign=1 if dy>0 else -1;arrow(ax,ay+sign*32,bx,by-sign*32,edge['both'])
    for n in mode['nodes']:
        x,y=xy(n['x'],n['y']+64)
        d.add(Rect(x,y,n['w']*factor,64*factor,rx=3,ry=3,fillColor=PALE if 'db' in n['id'] else colors.white,strokeColor=RULE,strokeWidth=.5))
        for offset,text,size,font in [(26,n['title'],10,'Arial-Bold'),(48,n['detail'],8.8,'Arial')]:
            while stringWidth(text,font,size)>n['w']*factor-7 and size>8.5:size-=.5
            cx,cy=xy(n['x']+n['w']/2,n['y']+offset)
            d.add(String(cx,cy,text,fontName=font,fontSize=size,fillColor=INK,textAnchor='middle'))
    return d

def render(data,page,add,heading,table,story,link):
    modes=data['modes']
    def block(m):
        heading(m['title']+' · '+m['focus']);story.append(diagram(m));add(m['description']);add('Déploiement illustratif : '+m['placement'],'small');add('Compromis : '+m['tradeoff'],'small')
    page('Architectures des systèmes · 1/3','Même exemple : catalogue du livre 42 et demande de commande')
    add(data['example']);add(data['scope'],'small')
    for m in modes[:2]:block(m)
    page('Services et microservices · 2/3','Deux découpages métier ; ne pas confondre service, processus et machine')
    for m in modes[2:4]:block(m)
    add('Les réponses et certains détails techniques sont omis pour garder les dessins lisibles. Une demande enregistrée n’est pas une garantie de réservation atomique ou de paiement.','small')
    page('P2P et comparaison · 3/3','Place de marché pédagogique : le pair B possède le livre 42')
    block(modes[4]);add(modes[4]['warning'],'small')
    heading('Comparer selon le besoin')
    table([['Modèle','Données dans l’exemple','Évolution']] + [[m['title'],m['data'],m['change']] for m in modes],[100,205,194],padding=5)
    add('À savoir expliquer : une application microservices peut aussi utiliser des relations client-serveur ; trois couches ne prouvent pas trois machines ; plusieurs services ne garantissent pas la tolérance aux pannes.','small')
    add(data['source'],'small')
    for title,url in data['links']:link(title,url)
