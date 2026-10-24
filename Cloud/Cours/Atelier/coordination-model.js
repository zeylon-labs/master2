(function(root){
  'use strict';
  const create=()=>({eventId:0,stockOnline:true,received:{email:[],stock:[]},lastDelivery:[],tupleId:0,tuples:[],pending:[],results:{A:'Aucune opération.',B:'Aucune opération.'}});
  function publish(s){s.eventId++;s.lastDelivery=['email'];s.received.email.push(s.eventId);if(s.stockOnline){s.lastDelivery.push('stock');s.received.stock.push(s.eventId);}return s.eventId;}
  function connect(s,online){s.stockOnline=online;s.lastDelivery=[];}
  function settle(s){
    const finished=[];
    for(const request of s.pending){
      if(!s.tuples.length)break;
      const tuple=s.tuples[0];
      if(request.operation==='in')s.tuples.shift();
      s.results[request.consumer]=`${request.operation} : occurrence T${tuple} ${request.operation==='in'?'retirée':'lue sans retrait'}.`;
      finished.push(request);
    }
    s.pending=s.pending.filter(r=>!finished.includes(r));
  }
  function out(s){s.tuples.push(++s.tupleId);settle(s);return s.tupleId;}
  function read(s,consumer,operation){
    if(!['A','B'].includes(consumer)||!['rd','in'].includes(operation))throw new Error('Opération invalide');
    if(s.pending.some(r=>r.consumer===consumer))return;
    s.pending.push({consumer,operation});s.results[consumer]=`${operation} en attente d’un tuple correspondant.`;settle(s);
  }
  const api={create,publish,connect,out,read};
  if(typeof module==='object'&&module.exports)module.exports=api;else root.CoordinationModel=api;
})(typeof window==='object'?window:globalThis);
