(function(){
  'use strict';
  const qs=(s,e=document)=>Array.from(e.querySelectorAll(s));
  const shuffle=a=>a.sort(()=>Math.random()-0.5);

  function show(el){ if(el){ el.classList.remove('hidden'); el.style.display=''; } }
  function hide(el){ if(el){ el.classList.add('hidden'); el.style.display='none'; } }

  function buildGame(box){
    const title=box.dataset.title;
    const board=box.querySelector('.game-board');
    const status=box.querySelector('.game-status');
    const generic=box.querySelector('.generic-choices');
    board.innerHTML='';
    hide(generic);
    box.dataset.score='50';
    status.textContent='Let’s try it — no pressure.';

    const finish=(score,message)=>{
      box.dataset.score=String(score);
      status.textContent=message || 'Nice work! Now choose how the session went.';
      show(generic);
    };

    if(title==='Memory Match'){
      const vals=['🍎','🐶','⭐','🚗','🌈','🦋'];
      const cards=shuffle([...vals,...vals]);
      let open=[], matched=0;
      board.className='game-board memory-board';
      cards.forEach(v=>{
        const c=document.createElement('button');
        c.type='button'; c.className='memory-card'; c.textContent='?'; c.dataset.v=v;
        c.addEventListener('click',()=>{
          if(c.classList.contains('matched')||open.includes(c)||open.length===2)return;
          c.textContent=v; open.push(c);
          if(open.length===2){
            if(open[0].dataset.v===open[1].dataset.v){
              open.forEach(x=>x.classList.add('matched')); matched+=2; open=[];
              if(matched===cards.length) finish(100,'🎉 All pairs found!');
            } else {
              const pair=open.slice();
              setTimeout(()=>{pair.forEach(x=>x.textContent='?');open=[];},650);
            }
          }
        });
        board.appendChild(c);
      });
      return;
    }

    if(title==='Emotion Match'){
      const data=[['😊','Happy'],['😢','Sad'],['😠','Angry'],['😨','Scared']];
      const target=data[Math.floor(Math.random()*data.length)];
      status.textContent='Which feeling is this?';
      board.innerHTML='<div class="big-emoji">'+target[0]+'</div>';
      const row=document.createElement('div'); row.className='choice-row';
      shuffle(data.map(x=>x[1])).forEach(x=>{
        const b=document.createElement('button'); b.type='button'; b.className='game-choice'; b.textContent=x;
        b.onclick=()=>{finish(x===target[1]?100:25,x===target[1]?'🎉 Great match!':'That’s okay — good try!');row.querySelectorAll('button').forEach(z=>z.disabled=true)};
        row.appendChild(b);
      });
      board.appendChild(row); return;
    }

    if(title==='Sort It'){
      const items=[['🍎','Food'],['🥕','Food'],['🐶','Animals'],['🐱','Animals'],['🚗','Vehicles'],['🚌','Vehicles']];
      let i=0,good=0;
      const next=()=>{
        if(i>=items.length){finish(Math.round(good/items.length*100),'🎉 Sorting complete!');return;}
        const [emoji,cat]=items[i]; board.innerHTML='<div class="sort-item">'+emoji+'</div>'; status.textContent='Where does it belong?';
        const row=document.createElement('div');row.className='choice-row';
        ['Food','Animals','Vehicles'].forEach(c=>{const b=document.createElement('button');b.type='button';b.className='game-choice';b.textContent=c;b.onclick=()=>{if(c===cat)good++;i++;next()};row.appendChild(b)});
        board.appendChild(row);
      }; next(); return;
    }

    if(title==='Hand Washing'||title==='Getting Dressed'||title==='Tooth Brushing'){
      const seq=title==='Hand Washing'?['Turn on water','Wet hands','Use soap','Rub hands','Rinse','Dry']:
        title==='Getting Dressed'?['Choose clothes','Put on shirt','Put on bottoms','Put on socks','Check comfort']:
        ['Get toothbrush','Add toothpaste','Brush gently','Spit/rinse','Put toothbrush away'];
      let idx=0; status.textContent='Tap the next step in the routine.';
      const row=document.createElement('div');row.className='choice-row';
      shuffle(seq.slice()).forEach(x=>{const b=document.createElement('button');b.type='button';b.className='game-choice';b.textContent=x;b.onclick=()=>{
        if(x===seq[idx]){b.disabled=true;idx++;if(idx===seq.length)finish(100,'🎉 Routine complete!');else status.textContent='Good — next step';}
        else status.textContent='That’s okay. Try another step.';
      };row.appendChild(b)});
      board.appendChild(row); return;
    }

    if(title==='Find & Tap'){
      const wanted=['⭐','🍎','🐶','🚗'][Math.floor(Math.random()*4)];
      status.textContent='Find and tap '+wanted;
      const row=document.createElement('div');row.className='choice-row';
      shuffle(['⭐','🍎','🐶','🚗','🌈','🦋']).forEach(x=>{const b=document.createElement('button');b.type='button';b.className='game-choice emoji-choice';b.textContent=x;b.onclick=()=>{finish(x===wanted?100:25,x===wanted?'🎉 You found it!':'Good try — let’s keep practicing.');row.querySelectorAll('button').forEach(z=>z.disabled=true)};row.appendChild(b)});
      board.appendChild(row); return;
    }

    if(title==='Yes / No'){
      const isYes=Math.random()>.5;
      status.textContent='Question: '+(isYes?'Is the sky blue?':'Is a fish a bicycle?');
      const row=document.createElement('div');row.className='choice-row';
      ['Yes','No'].forEach(x=>{const b=document.createElement('button');b.type='button';b.className='game-choice';b.textContent=x;b.onclick=()=>finish((x==='Yes')===isYes?100:25,(x==='Yes')===isYes?'🎉 Correct!':'That’s okay — good try!');row.appendChild(b)});
      board.appendChild(row); return;
    }

    status.textContent='Try this activity, then rate how it went.';
    finish(50);
  }

  document.addEventListener('click',async function(e){
    const start=e.target.closest('.start');
    if(start){
      e.preventDefault();
      const box=start.closest('.playarea');
      hide(start);
      show(box.querySelector('.game'));
      buildGame(box);
      return;
    }

    const choice=e.target.closest('.generic-choices button');
    if(choice){
      const box=choice.closest('.playarea');
      box.dataset.score=choice.dataset.score;
      qs('.generic-choices button',box).forEach(b=>b.classList.remove('selected'));
      choice.classList.add('selected');
      return;
    }

    const save=e.target.closest('.save');
    if(save){
      e.preventDefault();
      const box=save.closest('.playarea');
      const pid=location.pathname.split('/').pop();
      const body=new URLSearchParams({
        patient_id:pid,
        activity_id:box.dataset.activity,
        score:box.dataset.score||'50',
        duration:'5',
        status:'completed',
        note:box.querySelector('.note').value
      });
      try{
        const r=await fetch('/activity/log',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});
        if(!r.ok)throw new Error('save failed');
        hide(box.querySelector('.game')); show(box.querySelector('.done'));
      }catch(err){
        box.querySelector('.game-status').textContent='Could not save this session. Please try again.';
      }
      return;
    }

    const ap=e.target.closest('.approve,.reject');
    if(ap){
      const action=ap.classList.contains('approve')?'approve':'reject';
      await fetch('/admin/payment/'+ap.dataset.id+'/'+action,{method:'POST'});
      location.reload();
    }
  });
})();
