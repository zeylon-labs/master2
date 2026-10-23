(() => {
  'use strict';
  const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)], M=window.CloudModel;
  const pages={saturation:{title:'Saturation d’un serveur',intro:'Pourquoi quelques requêtes de plus peuvent-elles ralentir tout le service ?',source:'Scalabilité · Support, pages 15 à 18'},donnees:{title:'Données distribuées',intro:'Copier une donnée ou répartir les données : observe ce qui change quand un nœud tombe en panne.',source:'Réplication et partitionnement · Support, page 18'},chord:{title:'Une recherche dans Chord',intro:'Suis le chemin d’une clé entre les nœuds de l’exemple du cours.',source:'Architectures P2P · Support, pages 34 à 35'},cloud:{title:'ASP et couches cloud',intro:'Où tourne l’application, et qui prend en charge les différentes couches ?',source:'Hébergement et services · Support, pages 8 à 9 et 21'}};
  const feedback={queue:'R = 10 / (1 − 0,8) = 50 ms, dont 40 ms d’attente.',data:'Les mêmes données sur plusieurs nœuds : c’est une réplication.',chord:'Le premier nœud actif à partir de 12 est 14.',cloud:'Le SaaS fournit l’usage d’une application. Une machine virtuelle relève plutôt de l’IaaS.'};
  pages.middleware={title:'Le middleware entre les couches',intro:'Un même service distribué, plusieurs machines et plusieurs systèmes d’exploitation locaux.',source:'Middleware · Support, page 13'};
  feedback.middleware='Le middleware fournit des fonctions communes au-dessus des OS locaux ; il ne les remplace pas.';
  let active='saturation',data={mode:'replication',online:true,a:1,b:1},chord={path:[9,28,1,4],owner:4,step:0},client='web';
  function show(){
    const hash=location.hash.slice(1);active=Object.hasOwn(pages,hash)?hash:'saturation';
    $$('.view').forEach(el=>el.hidden=el.id!==active);
    $$('[data-route]').forEach(el=>{if(el.dataset.route===active)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
    $('#lesson').value=active;$('#page-title').textContent=pages[active].title;$('#page-intro').textContent=pages[active].intro;$('#page-source').textContent=pages[active].source;$('#footer-source').textContent=pages[active].source;
    document.title=`${pages[active].title} · Atelier Cloud`;
    if(active==='saturation')drawQueue();if(active==='donnees')drawData();if(active==='chord')drawChord();if(active==='cloud')drawCloud();
  }
  window.addEventListener('hashchange',show);$('#lesson').addEventListener('change',e=>location.hash=e.target.value);
  function nf(v,d=0){return new Intl.NumberFormat('fr-FR',{maximumFractionDigits:d}).format(v);}
  function drawQueue(){
    const u=Number($('#utilisation').value),s=Number($('#service').value),q=M.queue(u,s);
    $('#utilisation-value').textContent=`${u} %`;$('#service-value').textContent=`${s} ms`;
    $('#response').innerHTML=q.stable?`${nf(q.response,1)} <small>ms</small>`:'Pas de régime stable';
    $('#response').style.fontSize=q.stable?'':'20px';$('#wait').innerHTML=q.stable?`${nf(q.wait,1)} <small>ms</small>`:'Non bornée';$('#arrival').innerHTML=`${nf(q.arrival,1)} <small>/s</small>`;$('#capacity').textContent=nf(q.capacity,1);
    $('#queue-explanation').textContent=!q.stable?'Les arrivées atteignent la capacité moyenne. La file n’a plus de régime stationnaire stable dans ce modèle. Le serveur ne s’arrête pas instantanément.':u===0?'Aucune requête n’arrive. Une requête isolée mettrait le temps S à être traitée, sans attente.':`À ${u} % de charge, une requête passe en moyenne ${nf(q.response/s,1)} fois son temps de traitement dans le système. ${nf(q.wait/q.response*100)} % de ce temps est de l’attente.`;
    $$('[data-charge]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.charge)===u)));
    const labels=Array.from({length:100},(_,i)=>String(i)),values=labels.map((_,i)=>1/(1-i/100));
    $('#queue-chart').replaceChildren();
    Charts.line($('#queue-chart'),{labels,series:[{name:'Rapport R/S',values}],height:()=>innerWidth<700?200:230,min:0,max:20,yTicks:[0,5,10,15,20],clipAbove:true,format:v=>`×${nf(v,1)}`,tickFormat:v=>String(v),xAt:innerWidth<700?[0,50,99]:[0,25,50,75,99],annotations:u<100?[{at:u,label:`Charge : ${u} %`,short:`${u} %`}]:[]});
  }
  ['utilisation','service'].forEach(id=>$('#'+id).addEventListener('input',drawQueue));
  $$('[data-charge]').forEach(b=>b.addEventListener('click',()=>{$('#utilisation').value=b.dataset.charge;drawQueue();}));
  function drawData(){
    const rep=data.mode==='replication', letters=['A','B','C','D','E','F'];
    $$('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===data.mode)));
    $('#data-flow').innerHTML=['A','B'].map((node,i)=>{const docs=rep?letters:letters.slice(i*3,i*3+3),down=i===0&&!data.online;return `<div class="node ${down?'down':''}"><div class="node-head"><strong>Nœud ${node}</strong><span>${down?'Hors ligne':'En ligne'}</span></div><div class="documents">${docs.map(l=>`<div class="document ${l==='B'&&data.a>data.b&&i===0?'updated':''}">${l}</div>`).join('')}</div><p class="version">${rep?`Document B · version ${i===0?data.a:data.b}`:`Partition ${i===0?'A à C':'D à F'}`}</p></div>`;}).join('');
    $('#fail-a').textContent=data.online?'Arrêter le nœud A':'Redémarrer le nœud A';
    $('#write-data').disabled=!rep||!data.online;$('#sync-data').disabled=!rep||!data.online||data.a===data.b;
    $('#write-data').title=!rep?'La modification est proposée dans le scénario de réplication.':!data.online?'Le nœud d’écriture est arrêté.':'';
    $('#data-explanation').textContent=rep?(data.a!==data.b?`Les copies diffèrent : version ${data.a} sur A, version ${data.b} sur B. ${data.online?'Propage la mise à jour pour les synchroniser.':'Une lecture sur B reste possible, mais renvoie l’ancienne version.'}`:data.online?'Deux nœuds, deux copies complètes. Arrête A pour lire la copie sur B, ou modifie un document pour observer le décalage de mise à jour.':'A est arrêté. B contient une copie complète : les lectures restent possibles. Les écritures de ce scénario restent bloquées tant que A est arrêté.'):(data.online?'Chaque nœud contient trois documents différents. Les six documents restent accessibles, mais il n’existe qu’une copie de chacun.':'Les documents A, B et C ne sont plus accessibles. D, E et F restent disponibles sur le nœud B.');
  }
  $$('[data-mode]').forEach(b=>b.addEventListener('click',()=>{data={mode:b.dataset.mode,online:true,a:1,b:1};$('#read-result').textContent='Choisis un document pour voir quel nœud peut le servir.';drawData();}));
  $('#fail-a').addEventListener('click',()=>{data.online=!data.online;$('#read-result').textContent='État du nœud modifié. Relance une lecture.';drawData();});
  $('#write-data').addEventListener('click',()=>{data.a++;$('#read-result').textContent=`Document B modifié sur A : version ${data.a}. La copie sur B reste en version ${data.b}.`;drawData();});
  $('#sync-data').addEventListener('click',()=>{data.b=data.a;$('#read-result').textContent=`Mise à jour propagée : les deux copies du document B sont en version ${data.a}.`;drawData();});
  $$('[data-read]').forEach(b=>b.addEventListener('click',()=>{const letter=b.dataset.read;if(data.mode==='replication')$('#read-result').textContent=`Document ${letter} lu sur le nœud ${data.online?'A':'B'}${letter==='B'?`, version ${data.online?data.a:data.b}`:''}.${!data.online&&data.a!==data.b&&letter==='B'?' Cette copie est ancienne.':''}`;else $('#read-result').textContent=letter==='B'&&!data.online?'Document B indisponible : son unique partition est sur le nœud A, arrêté.':`Document ${letter} lu sur le nœud ${letter==='B'?'A':'B'}.`;}));
  $('#start-node').innerHTML=M.NODES.map(n=>`<option value="${n}" ${n===9?'selected':''}>${n}</option>`).join('');
  function prepareChord(){const key=Number($('#key').value),valid=$('#key').value.trim()!==''&&Number.isInteger(key)&&key>=0&&key<=31;$('#key-error').hidden=valid;$('#key').setAttribute('aria-invalid',String(!valid));if(!valid){$('#next-hop').disabled=true;$('#chord-graph').replaceChildren();$('#hop-path').replaceChildren();$('#hop-result').textContent='La recherche attend une clé valide.';$('#chord-owner').textContent='';$('#fingers').textContent='';return;}chord={...M.route(Number($('#start-node').value),key),step:0};drawChord();}
  function drawChord(){
    if(!$('#key-error').hidden)return;
    const key=Number($('#key').value),current=chord.path[chord.step],done=current===chord.owner,svg=$('#chord-graph'),w=Math.max(280,svg.clientWidth),h=innerWidth<700?310:330,cx=w/2,cy=h/2,r=Math.min(w/2-42,120);svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.replaceChildren();
    const ns='http://www.w3.org/2000/svg',el=(tag,attrs,t)=>{const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(t!==undefined)e.textContent=t;svg.appendChild(e);return e;},position=n=>{const a=Math.PI/2-2*Math.PI*n/32;return {x:cx+r*Math.cos(a),y:cy-r*Math.sin(a)}};
    el('title',{},`Clé ${key}, responsable ${chord.owner}, nœud courant ${current}`);el('circle',{cx,cy,r,fill:'none',stroke:'var(--border)','stroke-width':1.5});
    for(let i=1;i<=chord.step;i++){const a=position(chord.path[i-1]),b=position(chord.path[i]);el('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:'var(--accent)','stroke-width':2});}
    M.NODES.forEach(n=>{const pos=position(n),a=Math.atan2(pos.y-cy,pos.x-cx),rr=10;el('circle',{cx:pos.x,cy:pos.y,r:rr,fill:n===current?'var(--accent)':'var(--raised)',stroke:n===chord.owner?'var(--accent)':'var(--control)','stroke-width':n===chord.owner?2:1});const t=el('text',{x:pos.x+22*Math.cos(a),y:pos.y+22*Math.sin(a)+4,'text-anchor':'middle'},n);t.setAttribute('aria-hidden','true');});
    el('text',{x:cx,y:cy-4,'text-anchor':'middle',class:'ring-label'},`Clé ${key}`);el('text',{x:cx,y:cy+18,'text-anchor':'middle',class:'ring-label'},done?'Trouvée':`Nœud courant : ${current}`);
    $('#hop-path').innerHTML=chord.path.slice(0,chord.step+1).map(n=>`<li>${n}</li>`).join('');$('#hop-result').textContent=done?`Le nœud ${chord.owner} est responsable de la clé ${key}. ${chord.step} saut${chord.step>1?'s':''} effectué${chord.step>1?'s':''}.`:`La recherche est au nœud ${current}. Avance pour observer le prochain saut.`;
    $('#chord-owner').textContent=`successeur(${key}) = ${chord.owner}`;$('#fingers').textContent=`Depuis ${current} : ${M.fingers(current).join(', ')}. Les doublons de la table de raccourcis sont retirés.`;$('#next-hop').disabled=done;
  }
  $('#key').addEventListener('input',prepareChord);$('#start-node').addEventListener('change',prepareChord);$('#next-hop').addEventListener('click',()=>{if(chord.step<chord.path.length-1)chord.step++;drawChord();});
  function drawCloud(){
    $$('[data-client]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.client===client)));
    $('#asp-diagram').innerHTML=`<div class="asp-box"><strong>Ton ordinateur</strong><p>${client==='web'?'Navigateur web':'Client natif installé'}</p></div><div class="asp-arrow" aria-label="Échanges par Internet">⇄</div><div class="asp-box"><strong>Chez le fournisseur</strong><p>Application métier<br>Base de données</p></div>`;
    $('#asp-description').textContent=client==='web'?'L’interface passe par le navigateur. Les traitements principaux et les données restent chez l’ASP ; aucun client métier natif n’est nécessaire sur le poste.':'Le client natif améliore l’interface, mais il faut l’installer et le mettre à jour sur chaque poste. Il dialogue avec les services hébergés chez l’ASP.';
    const offer=$('#offer').value,layers=['Application','Environnement d’exécution','Système d’exploitation','Serveur virtuel et réseau','Matériel physique'],counts={local:0,iaas:2,paas:4,saas:5},descriptions={local:'Sur site : ton organisation exploite l’ensemble de la pile représentée.',iaas:'IaaS : tu loues l’infrastructure ; tu exploites notamment le système invité et ton application.',paas:'PaaS : tu déploies ton application dans un environnement géré par le fournisseur.',saas:'SaaS : tu utilises une application fournie comme service. Tu configures notamment les accès et l’usage des données.'};
    $('#cloud-stack').innerHTML=layers.map((name,i)=>{const provider=i>=layers.length-counts[offer];return `<div class="stack-row ${provider?'provider':''}"><span>${name}</span><span>${provider?'Fournisseur':'Ton organisation'}</span></div>`;}).join('');$('#offer-description').textContent=descriptions[offer];
  }
  $$('[data-client]').forEach(b=>b.addEventListener('click',()=>{client=b.dataset.client;drawCloud();}));$('#offer').addEventListener('change',drawCloud);
  $$('.quiz').forEach(quiz=>quiz.querySelectorAll('[data-answer]').forEach(b=>b.addEventListener('click',()=>{quiz.querySelectorAll('[data-answer]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));const good=b.dataset.answer==='true',result=quiz.querySelector('.feedback');result.className=`feedback ${good?'correct':'wrong'}`;result.textContent=`${good?'Exact.':'Pas tout à fait.'} ${feedback[quiz.dataset.quiz]}`;})));
  $('#reset').addEventListener('click',()=>{if(active==='saturation'){$('#utilisation').value=50;$('#service').value=10;drawQueue();}if(active==='donnees'){data={mode:'replication',online:true,a:1,b:1};$('#read-result').textContent='Choisis un document pour voir quel nœud peut le servir.';drawData();}if(active==='chord'){$('#start-node').value=9;$('#key').value=3;prepareChord();}if(active==='cloud'){client='web';$('#offer').value='saas';drawCloud();}const quiz=$(`#${active} .quiz`);quiz.querySelector('.feedback').textContent='';quiz.querySelectorAll('[data-answer]').forEach(b=>b.removeAttribute('aria-pressed'));});
  let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(active==='saturation')drawQueue();if(active==='chord')drawChord();},150);});
  show();
})();
