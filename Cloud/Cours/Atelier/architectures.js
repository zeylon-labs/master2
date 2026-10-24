(() => {
 'use strict';
 const D=window.CloudStudy.architectures,$=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let index=0,journey='catalogue',step=0;
 $('#architectures').innerHTML=`<p class="arch-lead">${esc(D.example)}</p><p class="arch-scope">${esc(D.scope)}</p><div class="arch-controls"><label for="arch-mode">Architecture<select id="arch-mode">${D.modes.map((m,i)=>`<option value="${i}">${esc(m.title)}</option>`).join('')}</select></label><label for="arch-journey">Même opération<select id="arch-journey"><option value="catalogue">Consulter le livre 42</option><option value="commande">Envoyer une commande</option></select></label></div><section class="arch-diagram-section"><div class="section-heading"><h2 id="arch-name"></h2><span id="arch-focus" class="subtle"></span></div><div id="arch-graph"></div><p class="arch-key">Boîtes : composants ou stockage, pas un nombre imposé de machines. Flèches : échanges logiques ; les réponses sont précisées dans les étapes.</p><div class="arch-step-controls"><button id="arch-next" class="button primary">Étape suivante</button><button id="arch-restart" class="button">Rejouer le parcours</button><span id="arch-progress" role="status"></span></div><ol id="arch-steps" class="arch-steps"></ol></section><div id="arch-details" class="arch-details"></div><section class="arch-comparison"><h2>Comparer les cinq modèles</h2><p>Le même besoin peut conduire à des organisations différentes. Ces modèles peuvent se combiner ; les données et le déploiement ci-dessous correspondent aux exemples dessinés.</p><div class="arch-table-scroll" tabindex="0" role="region" aria-label="Tableau comparatif des architectures, défilable horizontalement"><table><thead><tr><th>Modèle</th><th>Données de l’exemple</th><th>Unité d’évolution</th><th>Coût à considérer</th></tr></thead><tbody>${D.modes.map(m=>`<tr><th scope="row">${esc(m.title)}</th><td>${esc(m.data)}</td><td>${esc(m.change)}</td><td>${esc(m.tradeoff)}</td></tr>`).join('')}</tbody></table></div></section><section class="arch-exam"><h2>Questions pour vérifier la compréhension</h2>${D.questions.map(([q,a])=>`<details class="study-item"><summary>${esc(q)}</summary><div><p>${esc(a)}</p></div></details>`).join('')}<p class="study-source">${esc(D.source)}</p><div class="arch-links">${D.links.map(([t,u])=>`<a class="study-link" href="${u}" target="_blank" rel="noopener">${esc(t)} ↗</a>`).join('')}</div></section>`;
 function endpoints(a,b,mobile){
  const x=n=>mobile?n.mx:n.x,y=n=>mobile?n.my:n.y,w=n=>mobile?n.mw:n.w;
  const ax=x(a)+w(a)/2,ay=y(a)+32,bx=x(b)+w(b)/2,by=y(b)+32,dx=bx-ax,dy=by-ay;
  return Math.abs(dx)>Math.abs(dy)?[[ax+Math.sign(dx)*w(a)/2,ay],[bx-Math.sign(dx)*w(b)/2,by]]:[[ax,ay+Math.sign(dy)*32],[bx,by-Math.sign(dy)*32]];
 }
 function drawGraph(m){
  const mobile=matchMedia('(max-width:700px)').matches,w=mobile?360:900,h=mobile?m.mobileHeight:300,ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',m.title+' : '+m.description);
  const add=(tag,attrs,text,parent=svg)=>{const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text!==undefined)e.textContent=text;parent.append(e);return e;};
  const defs=add('defs',{}),marker=add('marker',{id:'arch-arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'},undefined,defs);add('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'context-stroke'},undefined,marker);
  const routes=m.journeys[journey],current=step?routes[step-1].edge:null,done=new Set(routes.slice(0,step).map(s=>s.edge));
  for(const link of m.edges){
   const a=m.nodes.find(n=>n.id===link.source),b=m.nodes.find(n=>n.id===link.target),points=endpoints(a,b,mobile);
   add('polyline',{points:points.map(p=>p.join(',')).join(' '),fill:'none',stroke:done.has(link.id)?'var(--accent)':'var(--control)','stroke-width':link.id===current?3:1.7,'marker-end':'url(#arch-arrow)',...(link.both?{'marker-start':'url(#arch-arrow)'}:{})});
  }
  for(const n of m.nodes){
   const x=mobile?n.mx:n.x,y=mobile?n.my:n.y,bw=mobile?n.mw:n.w,storage=n.id.includes('db');
   add('rect',{x,y,width:bw,height:64,rx:5,fill:storage?'var(--raised)':'var(--surface)',stroke:'var(--control)'});
   add('text',{x:x+bw/2,y:y+26,'text-anchor':'middle','font-size':mobile?(n.title.length>16?12:13):(n.title.length>16?16:18),'font-weight':500},n.title);
   add('text',{x:x+bw/2,y:y+48,'text-anchor':'middle','font-size':mobile?12:16},n.detail);
  }
  $('#arch-graph').replaceChildren(svg);
 }
 function draw(){
  const m=D.modes[index],routes=m.journeys[journey];$('#arch-name').textContent=m.title;$('#arch-focus').textContent=m.focus;drawGraph(m);
  $('#arch-progress').textContent=`${step} / ${routes.length} échanges parcourus`;
  $('#arch-next').disabled=step===routes.length;$('#arch-restart').disabled=step===0;
  $('#arch-steps').innerHTML=routes.map((s,i)=>`<li class="${i<step?'arch-visited':''}" ${i===step-1?'aria-current="step"':''}>${esc(s.text)}</li>`).join('');
  $('#arch-details').innerHTML=`<section><h2>Organisation</h2><p>${esc(m.description)}</p><p><b>Déploiement illustratif.</b> ${esc(m.placement)}</p></section><section><h2>Gains et limites</h2><p><b>Intérêt.</b> ${esc(m.advantage)}</p><p><b>Compromis.</b> ${esc(m.tradeoff)}</p><p><b>En cas de panne.</b> ${esc(m.failure)}</p></section><p class="arch-warning"><b>À ne pas conclure.</b> ${esc(m.warning)}</p>`;
 }
 $('#arch-mode').addEventListener('change',e=>{index=Number(e.target.value);step=0;draw();});
 $('#arch-journey').addEventListener('change',e=>{journey=e.target.value;step=0;draw();});
 $('#arch-next').addEventListener('click',()=>{if(step<D.modes[index].journeys[journey].length)step++;draw();});
 $('#arch-restart').addEventListener('click',()=>{step=0;draw();});
 $('#reset').addEventListener('click',()=>{if(location.hash==='#architectures'){index=0;journey='catalogue';step=0;$('#arch-mode').value='0';$('#arch-journey').value='catalogue';draw();}});
 addEventListener('resize',()=>{if(location.hash==='#architectures')draw();});addEventListener('hashchange',()=>{if(location.hash==='#architectures')draw();});draw();
})();
