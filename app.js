document.addEventListener('click',async e=>{const start=e.target.closest('.start');if(start){const box=start.closest('.playarea');box.querySelector('.game').classList.remove('hidden');start.classList.add('hidden')}const choice=e.target.closest('.choices button');if(choice){choice.parentElement.querySelectorAll('button').forEach(b=>b.classList.remove('selected'));choice.classList.add('selected');box=choice.closest('.playarea');box.dataset.score=choice.dataset.score}const save=e.target.closest('.save');if(save){const box=save.closest('.playarea');const card=save.closest('.activity');const pid=location.pathname.split('/').pop();const score=box.dataset.score||50;const aid=box.dataset.activity;const note=box.querySelector('.note').value;const r=await fetch('/activity/log',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({patient_id:pid,activity_id:aid,score,duration:5,status:'completed',note})});if(r.ok){box.querySelector('.game').classList.add('hidden');box.querySelector('.done').classList.remove('hidden')}}const ap=e.target.closest('.approve,.reject');if(ap){const action=ap.classList.contains('approve')?'approve':'reject';await fetch('/admin/payment/'+ap.dataset.id+'/'+action,{method:'POST'});location.reload()}})

/* --- Final interactive practice engine --- */
(function(){
 const qs=(s,e=document)=>Array.from(e.querySelectorAll(s));
 function shuffle(a){return a.sort(()=>Math.random()-.5)}
 function buildGame(box){
   const title=box.dataset.title, board=box.querySelector('.game-board'), status=box.querySelector('.game-status');
   board.innerHTML=''; status.textContent='Let’s try it — no pressure.';
   let score=50;
   const finish=(s)=>{score=s; status.textContent='Nice work! Choose “Save session” when you’re ready.';};
   if(title==='Memory Match'){
     const vals=['🍎','🐶','⭐','🚗','🌈','🦋']; const cards=shuffle([...vals,...vals]); let open=[],matched=0;
     board.className='game-board memory-board';
     cards.forEach(v=>{const c=document.createElement('button');c.className='memory-card';c.textContent='?';c.dataset.v=v;c.onclick=()=>{if(c.classList.contains('matched')||open.includes(c)||open.length===2)return;c.textContent=v;open.push(c);if(open.length===2){if(open[0].dataset.v===open[1].dataset.v){open.forEach(x=>x.classList.add('matched'));matched+=2;open=[];finish(Math.round(matched/cards.length*100));if(matched===cards.length)status.textContent='🎉 All pairs found!';}else setTimeout(()=>{open.forEach(x=>x.textContent='?');open=[];},650)}};board.appendChild(c)});
   } else if(title==='Emotion Match'){
     const qs2=[['😊','Happy'],['😢','Sad'],['😠','Angry'],['😨','Scared']]; const target=qs2[Math.floor(Math.random()*qs2.length)];
     status.textContent='Which feeling is this?'; board.innerHTML='<div class="big-emoji">'+target[0]+'</div>';
     const row=document.createElement('div');row.className='choice-row';shuffle(qs2.map(x=>x[1])).forEach(x=>{let b=document.createElement('button');b.className='game-choice';b.textContent=x;b.onclick=()=>{finish(x===target[1]?100:25);row.querySelectorAll('button').forEach(z=>z.disabled=true);};row.appendChild(b)});board.appendChild(row);
   } else if(title==='Sort It'){
     const items=[['🍎','Food'],['🥕','Food'],['🐶','Animals'],['🐱','Animals'],['🚗','Vehicles'],['🚌','Vehicles']]; let i=0,good=0;
     function next(){if(i>=items.length){finish(Math.round(good/items.length*100));return;} const [emoji,cat]=items[i]; board.innerHTML='<div class="sort-item">'+emoji+'</div>';status.textContent='Where does it belong?';const row=document.createElement('div');row.className='choice-row';['Food','Animals','Vehicles'].forEach(c=>{let b=document.createElement('button');b.className='game-choice';b.textContent=c;b.onclick=()=>{if(c===cat)good++;i++;next()};row.appendChild(b)});board.appendChild(row)}
     next();
   } else if(title==='Hand Washing'||title==='Getting Dressed'||title==='Tooth Brushing'){
     const seq=title==='Hand Washing'?['Turn on water','Wet hands','Use soap','Rub hands','Rinse','Dry']:title==='Getting Dressed'?['Choose clothes','Put on shirt','Put on bottoms','Put on socks','Check comfort']:['Get toothbrush','Add toothpaste','Brush gently','Spit/rinse','Put toothbrush away'];
     let idx=0; status.textContent='Put the steps in order — tap the next step.'; const row=document.createElement('div');row.className='choice-row';
     shuffle(seq.slice()).forEach((x)=>{let b=document.createElement('button');b.className='game-choice';b.textContent=x;b.onclick=()=>{if(x===seq[idx]){b.disabled=true;idx++;status.textContent=idx===seq.length?'🎉 Routine complete!':'Good — next step';if(idx===seq.length)finish(100)}else{status.textContent='That’s okay. Try another step.'}};row.appendChild(b)});board.appendChild(row);
   } else if(title==='Find & Tap'){
     const wanted=['⭐','🍎','🐶','🚗'][Math.floor(Math.random()*4)];status.textContent='Find and tap '+wanted;const row=document.createElement('div');row.className='choice-row';shuffle(['⭐','🍎','🐶','🚗','🌈','🦋']).forEach(x=>{let b=document.createElement('button');b.className='game-choice emoji-choice';b.textContent=x;b.onclick=()=>{finish(x===wanted?100:25);row.querySelectorAll('button').forEach(z=>z.disabled=true)};row.appendChild(b)});board.appendChild(row);
   } else if(title==='Yes / No'){const answer=Math.random()>.5?'Yes':'No';status.textContent='Question: Is '+(answer==='Yes'?'the sky blue?':'a fish a bicycle?');const row=document.createElement('div');row.className='choice-row';['Yes','No'].forEach(x=>{let b=document.createElement('button');b.className='game-choice';b.textContent=x;b.onclick=()=>finish(x===answer?100:25);row.appendChild(b)});board.appendChild(row);
   } else {
     status.textContent='Try a short practice, then choose how it went.'; finish(50);
   }
 }
 document.addEventListener('click',e=>{const start=e.target.closest('.start');if(start){const box=start.closest('.playarea');start.classList.add('hidden');box.querySelector('.game').classList.remove('hidden');buildGame(box);}
 const save=e.target.closest('.save');if(save){const box=save.closest('.playarea');const pid=location.pathname.split('/').pop();const score=box.dataset.score||50;const aid=box.dataset.activity;const note=box.querySelector('.note').value;fetch('/activity/log',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({patient_id:pid,activity_id:aid,score,duration:5,status:'completed',note})}).then(r=>{if(r.ok){box.querySelector('.game').classList.add('hidden');box.querySelector('.done').classList.remove('hidden')}})}});
 document.addEventListener('click',e=>{const c=e.target.closest('.generic-choices button');if(c){const box=c.closest('.playarea');box.dataset.score=c.dataset.score;box.querySelectorAll('.generic-choices button').forEach(x=>x.classList.remove('selected'));c.classList.add('selected')}});
})();
