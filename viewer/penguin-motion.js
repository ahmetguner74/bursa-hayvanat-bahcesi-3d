// Deterministic interaction state. No rendering, timers, random wandering or
// land/water teleportation. Only an explicit request advances a short sequence.
export function insideRing(ring,x,y){
  let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const a=ring[i],b=ring[j];
    if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;
  }
  return inside;
}
export function insideDomain(domain,x,y){
  return domain.some(p=>insideRing(p.outer,x,y)&&!p.holes.some(h=>insideRing(h,x,y)));
}
export function groundOffset(clips,name,time){
  const clip=clips[name],values=clip.groundOffsetMetres;
  const phase=((time%clip.duration)+clip.duration)%clip.duration/clip.duration*(values.length-1),i=Math.floor(phase);
  return values[i]+(values[Math.min(i+1,values.length-1)]-values[i])*(phase-i);
}
export function transitionGround(data,from,to,time,weight){
  const table=data.tables[from+'>'+to];
  if(!table)throw Error('Penguen geçiş tablosu eksik: '+from+'>'+to);
  const p=((time%table.duration)+table.duration)%table.duration/table.duration*data.phaseSegments;
  const w=Math.max(0,Math.min(1,weight))*data.weightSegments,pi=Math.floor(p),wi=Math.floor(w),pt=p-pi,wt=w-wi;
  const pj=Math.min(pi+1,data.phaseSegments),wj=Math.min(wi+1,data.weightSegments);
  const a=table.values[pi][wi]*(1-wt)+table.values[pi][wj]*wt,b=table.values[pj][wi]*(1-wt)+table.values[pj][wj]*wt;
  return a*(1-pt)+b*pt;
}

const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));
const smooth=t=>t*t*(3-2*t);
const blend=(clip,duration=.5)=>({kind:'blend',clip,time:0,duration});
const play=(clip,duration)=>({kind:'play',clip,duration});
const hold=(clip,time=0)=>({kind:'hold',clip,time});
const labels={notice:'Silkeleniyor',look:'Bakınıyor',preen:'Tüylerini düzeltiyor',sleep:'Uykuya hazırlanıyor',swim:'Yüzüyor',rest:'Dinleniyor'};

export function createPenguinInteraction(meta,index){
  const water=index>=meta.landStarts.length,start=water?meta.waterStarts[index-meta.landStarts.length]:meta.landStarts[index];
  const route=water?meta.waterRoutes[index-meta.landStarts.length]:null;
  let angle=route?.startAngle||0,step=null,queue=[],pending=null,activity=null,elapsed=0,from=null;
  let pose={clip:'Idle',time:water?0:index*3.1};
  const bird={index,water,x:start[0],y:start[1],scale:[.98,1.02,.97,1.01,.99][index],heading:[-1.35,-1.8,-.9][index]||0,speed:0};
  function waterHeading(){
    const [rx,ry]=route.radii;
    return Math.atan2(ry*Math.cos(angle)*route.direction,-rx*Math.sin(angle)*route.direction);
  }
  if(water)bird.heading=waterHeading();

  function advance(){
    step=queue.shift()||null;elapsed=0;
    if(!step){activity=null;return;}
    if(step.kind==='hold'){
      pose={clip:step.clip,time:step.time};queue=[];step=null;activity=null;return;
    }
    from={...pose};
    if(step.kind==='play')pose={clip:step.clip,time:0};
  }
  function begin(command){
    activity=command;pending=null;
    if(water){
      queue=command==='swim'?[blend('Penguin swim',.65),{kind:'swim',duration:9,stopping:false},blend('Idle',.8),hold('Idle')]:[{kind:'swim',duration:1.6,stopping:true},blend('Idle',.8),hold('Idle')];
      advance();return;
    }
    const wake=pose.clip==='Sleep'?[blend('Sit1',.8),play('Sit1',.6),blend('Idle',.7)]:pose.clip==='Idle'&&pose.time===0?[]:[blend('Idle',.45)];
    if(command==='sleep')queue=[...wake,blend('Sit1',.7),play('Sit1',meta.clips.Sit1.duration),blend('Sleep',.8),play('Sleep',2),hold('Sleep',2)];
    else if(command==='preen')queue=[...wake,blend('Preen',.4),play('Preen',meta.clips.Preen.duration),blend('Idle'),hold('Idle')];
    else if(command==='notice')queue=[...wake,blend('Shake',.2),play('Shake',meta.clips.Shake.duration),blend('Idle'),hold('Idle')];
    else if(command==='look')queue=[...wake,play('Idle',4.2),blend('Idle'),hold('Idle')];
    else queue=[blend('Idle'),hold('Idle')];
    advance();
  }
  function request(command){
    const allowed=water?['swim','rest']:['notice','look','preen','sleep','rest'];
    if(!allowed.includes(command))return false;
    if(water&&command==='swim'&&activity==='swim'){
      // A watched swimmer keeps swimming on a new touch, without teleporting
      // or resetting its clip phase. Extend travel or safely re-enter after rest.
      if(step?.kind==='swim'&&!step.stopping)elapsed=0;
      else if(step?.kind==='blend'&&step.clip==='Idle'){pending='swim';queue=[];}
      return true;
    }
    if(activity===command)return false;
    if(!step&&((command==='sleep'&&pose.clip==='Sleep')||(water&&command==='rest')))return false;
    if(step?.kind==='blend'){
      pending=command;queue=[];
    }else begin(command);
    return true;
  }
  function update(dt){
    if(!step)return false;
    dt=clamp(dt,0,.08);elapsed=Math.min(step.duration,elapsed+dt);
    if(step.kind==='play')pose={clip:step.clip,time:elapsed%meta.clips[step.clip].duration};
    else if(step.kind==='swim'){
      const target=step.stopping||step.duration-elapsed<1.6?0:meta.swimSpeedMetresPerSecond*bird.scale;
      bird.speed+=clamp(target-bird.speed,-.36*dt,.32*dt);
      const [rx,ry]=route.radii;
      const nextAngle=angle+route.direction*bird.speed*dt/Math.hypot(rx*Math.sin(angle),ry*Math.cos(angle));
      const x=route.centre[0]+rx*Math.cos(nextAngle),y=route.centre[1]+ry*Math.sin(nextAngle);
      if(!insideDomain(meta.waterDomain,x,y)){bird.speed=0;step=null;queue=[];pending=null;activity=null;return true;}
      angle=nextAngle;bird.x=x;bird.y=y;bird.heading=waterHeading();
      pose.time=(pose.time+dt*bird.speed/(meta.swimSpeedMetresPerSecond*bird.scale))%meta.clips['Penguin swim'].duration;
    }
    if(elapsed>=step.duration){
      if(step.kind==='blend')pose={clip:step.clip,time:step.time};
      if(step.kind==='swim')bird.speed=0;
      if(pending){const command=pending;pending=null;begin(command);}else advance();
    }
    return true;
  }
  function samples(){
    if(step?.kind!=='blend')return [{...pose,weight:1}];
    const weight=smooth(elapsed/step.duration);
    return [{...from,weight:1-weight},{clip:step.clip,time:step.time,weight}];
  }
  function cancel(){
    if(!step)return false;
    return request('rest');
  }
  return Object.assign(bird,{request,update,samples,cancel,
    active:()=>Boolean(step),sleeping:()=>!step&&pose.clip==='Sleep',
    activity:()=>activity,
    label:()=>activity&&activity!=='sleep'&&(pose.clip==='Sit1'||step?.kind==='blend'&&from.clip==='Sleep')?'Uyanıyor':activity?labels[activity]:pose.clip==='Sleep'?'Uyuyor':water?'Suda dinleniyor':'Dinleniyor',
    snapshot:()=>({index,water,x:bird.x,y:bird.y,heading:bird.heading,speed:bird.speed,active:Boolean(step),activity,phase:step?.kind||'hold',pose:{...pose},samples:samples()})});
}
