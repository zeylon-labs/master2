/* Les valeurs de départ viennent des exemples du cours, pas de mesures réelles. */
(function(root){
  const NODES = Object.freeze([1,4,9,11,14,18,20,21,28]);
  function queue(utilisation,serviceMs){
    const u=utilisation/100,capacity=1000/serviceMs;
    return {u,capacity,arrival:u*capacity,stable:u<1,response:u<1?serviceMs/(1-u):Infinity,wait:u<1?serviceMs/(1-u)-serviceMs:Infinity};
  }
  function successor(key){return NODES.find(n=>n>=key)??NODES[0];}
  function distance(a,b){return (b-a+32)%32;}
  function fingers(node){return [...new Set(Array.from({length:5},(_,i)=>successor((node+2**i)%32)))];}
  function route(start,key){
    const owner=successor(key),path=[start];let cur=start;
    while(cur!==owner){
      const target=distance(cur,key);
      const eligible=fingers(cur).filter(n=>distance(cur,n)>0 && distance(cur,n)<target);
      const next=eligible.sort((a,b)=>distance(cur,b)-distance(cur,a))[0]??successor((cur+1)%32);
      if(path.includes(next))throw new Error('Cycle de routage');
      path.push(next);cur=next;
      if(path.length>NODES.length)throw new Error('Routage invalide');
    }
    return {path,owner};
  }
  root.CloudModel={NODES,queue,successor,fingers,route};
  if(typeof module!=='undefined')module.exports=root.CloudModel;
})(typeof window!=='undefined'?window:globalThis);
