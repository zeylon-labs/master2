"""Compléments du 24 octobre, depuis la source partagée avec l'Atelier."""

def render(data,page,add,heading,table,link):
    for i,section in enumerate(data['sections']):
        page(section['title'],'Mise à jour du 24 octobre · Résumé Plaud confronté au support')
        for block in section['blocks']:
            if block['type']=='heading':heading(block['text'])
            elif block['type']=='table':table([block['header']]+block['rows'],block['widths'],padding=4)
            else:add(block['text'])
        add(section['source'],'small')
        if i==0:link('Idempotence : RFC 9110',data['links'][0][1])
        if i==3:
            for title,url in data['links'][1:]:link(title,url)
