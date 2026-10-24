(() => {
 'use strict';
 const M=window.CoordinationModel,$=s=>document.querySelector(s);let state=M.create();
 $('#evenements').innerHTML=`<p class="coord-lead">Dans les deux cas, le producteur ignore qui utilisera son information. Observe ce qui circule : <b>une notification envoyée aux abonnés</b>, ou <b>une donnée déposée puis recherchée</b>.</p>
 <div class="coord-grid">
 <section class="coord-panel" aria-labelledby="pub-title"><h2 id="pub-title">Publish/subscribe</h2><p>Diffuser un événement aux abonnés présents</p><div class="coord-graph" id="pub-graph"></div><p class="coord-assumption">Scénario éphémère : sans conservation ni rejeu des messages.</p><div class="coord-actions"><button class="button primary" id="coord-publish">Publier CommandeCréée</button><button class="button" id="coord-connect" aria-pressed="true">Déconnecter Stock</button></div><p id="coord-pub-feedback" class="coord-feedback" role="status"></p><dl class="coord-receipts"><div><dt>Email a reçu</dt><dd id="coord-email"></dd></div><div><dt>Stock a reçu</dt><dd id="coord-stock"></dd></div></dl><p class="subtle">Ce journal montre les réceptions de la simulation ; il ne sert pas à rejouer des événements.</p><details class="study-item"><summary>Et si le système conservait les événements ?</summary><p>Un broker avec messages conservés, abonnements durables ou mécanisme de reprise peut permettre à un abonné de recevoir plus tard. Le découplage temporel dépend de ces garanties. « Asynchrone » seul ne les assure pas.</p></details></section>
 <section class="coord-panel" aria-labelledby="tuple-title"><h2 id="tuple-title">Espace de données partagé</h2><p>Déposer un tuple, puis le retrouver par motif</p><div class="coord-graph" id="tuple-graph"></div><p class="coord-assumption">Motif fixe : <code>(commande, 42, prête)</code>. Chaque dépôt est une occurrence distincte.</p><div class="coord-actions"><button class="button primary" id="coord-out">out · déposer</button><label for="coord-consumer">Consommateur<select id="coord-consumer"><option>A</option><option>B</option></select></label><button class="button" id="coord-rd">rd · lire</button><button class="button" id="coord-in">in · retirer</button></div><p id="coord-tuple-feedback" class="coord-feedback" role="status">Dépose un tuple, ou lance une lecture pour observer l’attente.</p><div id="coord-tuples" class="coord-tuples" aria-label="Occurrences présentes dans l’espace"></div><dl class="coord-receipts"><div><dt>Consommateur A</dt><dd id="coord-result-a"></dd></div><div><dt>Consommateur B</dt><dd id="coord-result-b"></dd></div><p class="subtle">in et rd attendent si aucun tuple ne correspond. La reprise suit ici l’ordre des demandes, pour rendre la simulation lisible ; cet ordre n’est pas une garantie générale de Linda.</p></section>
 </div>
 <div class="coord-summary"><h2>La différence à retenir</h2><p><b>Pub/sub :</b> un même événement peut être reçu par plusieurs abonnés. Dans le scénario éphémère, un abonné absent manque sa notification.</p><p><b>Espace partagé :</b> on retrouve des tuples par leur contenu. <code>rd</code> laisse le tuple disponible ; <code>in</code> retire une occurrence. Deux consommateurs en concurrence sur une seule occurrence ne peuvent pas tous deux la retirer.</p><p>Les deux modèles découplent les références entre producteurs et consommateurs. La conservation des tuples découple aussi leurs moments d’activité. L’espace partagé est une abstraction logicielle accessible par le réseau : ce n’est pas une RAM commune aux machines.</p><p class="study-source">Support p. 30–31 · Modèles simplifiés d’entraînement. <a href="https://redis.io/docs/latest/develop/pubsub/" target="_blank" rel="noopener">Exemple officiel de pub/sub éphémère ↗</a></p><a class="study-link" href="#synthese">Relire le thème 11 dans la synthèse →</a></div>`;
 const L=window.CloudStudy.linda;
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const lesson=document.createElement('section');lesson.id='linda-clair';lesson.className='coord-summary linda-lesson';
 lesson.innerHTML=`<h2>${esc(L.title)}</h2><p>${esc(L.intro)}</p><p>${esc(L.tuple)}</p><h3>Les trois opérations</h3><div class="linda-operations">${L.operations.map(op=>`<article><h4><code>${esc(op[0])}</code></h4><p>${esc(op[1])}</p><p>${esc(op[2])}</p></article>`).join('')}</div><p class="linda-memory"><b>${esc(L.memory)}</b></p><h3>Exercice corrigé · espace initialement vide</h3><p>A et B sont deux processus. Suis les instructions dans cet ordre : B peut avancer pendant que A attend. Cet exercice manipule des « notes » ; la simulation au-dessus manipule des « commandes », avec les mêmes règles.</p><ol class="linda-trace">${L.trace.map(t=>`<li><code>${esc(t.instruction)}</code><p>${esc(t.result)}</p><p class="linda-space">Espace après : <strong>${esc(t.space)}</strong></p></li>`).join('')}</ol><h3>Raisonner pour un exercice</h3><ul>${L.pitfalls.map(t=>`<li>${esc(t)}</li>`).join('')}</ul><p>${esc(L.course)}</p><p class="study-source">${esc(L.source)}</p>`;
 $('#evenements').append(lesson);
 const jump=document.createElement('button');jump.type='button';jump.id='coord-linda-link';jump.className='button';jump.textContent='Linda : définition et exercice ↓';
 jump.addEventListener('click',()=>{lesson.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'});lesson.querySelector('h2').tabIndex=-1;lesson.querySelector('h2').focus({preventScroll:true});});
 $('#evenements .coord-lead').after(jump);
 function diagram(kind){
  const mobile=matchMedia('(max-width:700px)').matches,tuple=kind==='tuple',w=mobile?340:620,h=mobile?330:255;
  const pos=mobile?[[96,8,148,56],[86,110,168,70],[4,240,157,68],[179,240,157,68]]:[[0,95,140,64],[208,85,180,85],[464,25,154,72],[464,158,154,72]];
  const labels=tuple?['Producteur','Espace de tuples','Consommateur A','Consommateur B']:['Commandes','Topic commandes','Abonné Email','Abonné Stock'];
  const status=tuple?['out(t)',`${state.tuples.length} occurrence${state.tuples.length!==1?'s':''}`,state.pending.some(r=>r.consumer==='A')?'En attente de tuple':'rd(motif) / in(motif)',state.pending.some(r=>r.consumer==='B')?'En attente de tuple':'rd(motif) / in(motif)']:['CommandeCréée','Notification éphémère','Connecté',state.stockOnline?'Connecté':'Déconnecté'];
  const n='http://www.w3.org/2000/svg',svg=document.createElementNS(n,'svg');svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',tuple?'Un producteur dépose des tuples dans un espace partagé. Deux consommateurs peuvent lire ou retirer par motif.':'Commandes publie sur un topic qui notifie Email et Stock si connecté.');
  function el(tag,attrs,text,parent=svg){const node=document.createElementNS(n,tag);Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,v));if(text!==undefined)node.textContent=text;parent.append(node);return node;}
  const defs=el('defs',{});['arrow','both'].forEach((id)=>{const mark=el('marker',{id:`${kind}-${id}`,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'},undefined,defs);el('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'context-stroke'},undefined,mark);});
  for(let dest=1;dest<=3;dest++){
    const source=dest===1?0:1,a=pos[source],b=pos[dest];
    const path=mobile?`M ${a[0]+a[2]/2} ${a[1]+a[3]} L ${b[0]+b[2]/2} ${b[1]}`:`M ${a[0]+a[2]} ${a[1]+a[3]/2} L ${b[0]} ${b[1]+b[3]/2}`;
    const active=!tuple&&state.lastDelivery.includes(dest===2?'email':dest===3?'stock':'email'),off=!tuple&&dest===3&&!state.stockOnline;
    el('path',{d:path,fill:'none',stroke:active?'var(--accent)':'var(--control)','stroke-width':active?2.5:1.5,'stroke-dasharray':off?'5 5':'none','marker-end':`url(#${kind}-arrow)`,...(tuple&&dest>1?{'marker-start':`url(#${kind}-both)`}:{})});
  }
  pos.forEach(([x,y,bw,bh],i)=>{el('rect',{x,y,width:bw,height:bh,rx:5,fill:'var(--surface)',stroke:i===1?'var(--accent)':'var(--control)'});el('text',{x:x+bw/2,y:y+26,'text-anchor':'middle','font-size':mobile?13:14,'font-weight':500},labels[i]);el('text',{x:x+bw/2,y:y+47,'text-anchor':'middle','font-size':13,fill:'var(--muted)'},status[i]);});
  return svg;
 }
 function draw(){
  $('#pub-graph').replaceChildren(diagram('pub'));$('#tuple-graph').replaceChildren(diagram('tuple'));
  $('#coord-connect').textContent=state.stockOnline?'Déconnecter Stock':'Reconnecter Stock';$('#coord-connect').setAttribute('aria-pressed',String(state.stockOnline));
  for(const key of ['email','stock'])$('#coord-'+key).textContent=state.received[key].length?state.received[key].map(id=>'E'+id).join(', '):'Aucun événement.';
  $('#coord-pub-feedback').textContent=!state.eventId?'Publie un événement pour suivre sa diffusion.':!state.lastDelivery.length?'Connexion modifiée : aucun événement passé n’est rejoué. Publie un nouvel événement.':`E${state.eventId} reçu par Email${state.lastDelivery.includes('stock')?' et Stock.':'. Stock était absent : cet événement lui manque.'}`;
  $('#coord-tuples').replaceChildren();
  if(!state.tuples.length)$('#coord-tuples').textContent='Espace vide : aucun tuple disponible.';
  state.tuples.forEach(id=>{const token=document.createElement('span');token.textContent=`T${id} · (commande, 42, prête)`;$('#coord-tuples').append(token);});
  $('#coord-result-a').textContent=state.results.A;$('#coord-result-b').textContent=state.results.B;
  const waiting=state.pending.some(r=>r.consumer===$('#coord-consumer').value);$('#coord-rd').disabled=waiting;$('#coord-in').disabled=waiting;
 }
 $('#coord-publish').addEventListener('click',()=>{M.publish(state);draw();});
 $('#coord-connect').addEventListener('click',()=>{M.connect(state,!state.stockOnline);draw();});
 $('#coord-out').addEventListener('click',()=>{const id=M.out(state);$('#coord-tuple-feedback').textContent=`out : occurrence T${id} déposée.${state.tuples.includes(id)?' Elle reste disponible.':' Une demande in en attente l’a immédiatement retirée.'}`;draw();});
 ['rd','in'].forEach(op=>$('#coord-'+op).addEventListener('click',()=>{M.read(state,$('#coord-consumer').value,op);$('#coord-tuple-feedback').textContent=`Demande ${op} du consommateur ${$('#coord-consumer').value}. Résultat ci-dessous.`;draw();}));
 $('#coord-consumer').addEventListener('change',draw);
 $('#reset').addEventListener('click',()=>{if(location.hash==='#evenements'){state=M.create();$('#coord-consumer').value='A';$('#coord-tuple-feedback').textContent='Dépose un tuple, ou lance une lecture pour observer l’attente.';draw();}});
 addEventListener('resize',()=>{if(location.hash==='#evenements')draw();});
 addEventListener('hashchange',()=>{if(location.hash==='#evenements')draw();});draw();
})();
