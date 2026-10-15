// Metric behavior, independent of rendering: deterministic seeds, bounded
// acceleration/turning, clear travel segments, and individual quiet periods.
export function insideRing(ring,x,y){
  let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const a=ring[i],b=ring[j];
    if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;
  }
  return inside;
}
export function insideDomain(domain,x,y){return domain.some(p=>insideRing(p.outer,x,y)&&!p.holes.some(h=>insideRing(h,x,y)));}
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const angleDelta=(a,b)=>Math.atan2(Math.sin(a-b),Math.cos(a-b));
export function groundOffset(clips,name,time){
  const clip=clips[name],values=clip.groundOffsetMetres;
  const phase=((time%clip.duration)+clip.duration)%clip.duration/clip.duration*(values.length-1),index=Math.floor(phase);
  return values[index]+(values[Math.min(index+1,values.length-1)]-values[index])*(phase-index);
}
export function createPenguinBehavior(meta,index){
  const water=index>=meta.landStarts.length,domain=water?meta.waterDomain:meta.groundDomain;
  const start=water?meta.waterStarts[index-meta.landStarts.length]:meta.landStarts[index];
  let seed=15102026+index*1777;
  const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
  const bounds=[Infinity,Infinity,-Infinity,-Infinity];
  for(const p of domain)for(const [x,y] of p.outer){bounds[0]=Math.min(bounds[0],x);bounds[1]=Math.min(bounds[1],y);bounds[2]=Math.max(bounds[2],x);bounds[3]=Math.max(bounds[3],y);}
  const bird={index,water,x:start[0],y:start[1],heading:water?.2:index===0?0:Math.PI,scale:.96+random()*.08,speed:0,pace:1,clip:water?'Penguin swim':index===1?'Preen':'Idle',elapsed:0,wait:2+index*1.8,dive:0};
  let target=null,diveTime=0,diveDuration=0,diveWait=7+random()*10,diveDepth=0;
  function change(clip,wait){bird.clip=clip;bird.elapsed=0;bird.wait=wait;}
  function clearSegment(x,y){
    const n=Math.ceil(Math.hypot(x-bird.x,y-bird.y)/.12);
    for(let i=1;i<=n;i++)if(!insideDomain(domain,bird.x+(x-bird.x)*i/n,bird.y+(y-bird.y)*i/n))return false;
    return true;
  }
  function pickTarget(neighbors){
    for(let i=0;i<80;i++){
      const x=bounds[0]+random()*(bounds[2]-bounds[0]),y=bounds[1]+random()*(bounds[3]-bounds[1]);
      const distance=Math.hypot(x-bird.x,y-bird.y);
      if(distance<(water?2:1)||distance>(water?8:3.8)||!insideDomain(domain,x,y)||!clearSegment(x,y))continue;
      if(neighbors.some(other=>other!==bird&&other.water===water&&Math.hypot(x-other.x,y-other.y)<.9))continue;
      target={x,y};return true;
    }
    target=null;return false;
  }
  bird.update=(dt,neighbors=[])=>{
    bird.elapsed+=dt;
    if(water){
      diveWait-=dt;
      if(diveWait<=0&&!diveDuration){diveDuration=4.5+random()*2;diveDepth=.35+random()*.15;diveTime=0;}
      if(diveDuration){diveTime+=dt;bird.dive=diveDepth*Math.sin(Math.PI*clamp(diveTime/diveDuration,0,1))**2;if(diveTime>=diveDuration){diveDuration=0;bird.dive=0;diveWait=10+random()*15;}}
      if(!target)pickTarget(neighbors);
    }else if(bird.clip!=='Walk'&&bird.elapsed>=bird.wait){
      const choice=random();
      if(bird.clip!=='Idle')change('Idle',3+random()*6);
      else if(choice<.7&&pickTarget(neighbors))change('Walk',100);
      else if(choice<.92)change('Preen',meta.clips.Preen.duration);
      else change('Shake',meta.clips.Shake.duration);
    }
    const moving=water||bird.clip==='Walk';
    let desiredSpeed=0;
    if(moving&&target){
      const dx=target.x-bird.x,dy=target.y-bird.y,distance=Math.hypot(dx,dy),desiredHeading=Math.atan2(dy,dx);
      const turn=angleDelta(desiredHeading,bird.heading);
      bird.heading+=clamp(turn,-(water?.85:1.1)*dt,(water?.85:1.1)*dt);
      const topSpeed=(water?meta.swimSpeedMetresPerSecond:meta.walkSpeedMetresPerSecond)*bird.scale;
      desiredSpeed=Math.min(topSpeed,Math.sqrt(Math.max(0,distance-.12)*(water?.5:.2)))*Math.max(.1,Math.cos(turn));
      if(distance<.2){target=null;if(!water)change('Idle',3+random()*7);}
    }
    const acceleration=water?.32:.18;
    bird.speed+=clamp(desiredSpeed-bird.speed,-acceleration*dt,acceleration*dt);
    const x=bird.x+Math.cos(bird.heading)*bird.speed*dt,y=bird.y+Math.sin(bird.heading)*bird.speed*dt;
    const blocked=neighbors.some(other=>other!==bird&&other.water===water&&Math.hypot(x-other.x,y-other.y)<(water?.7:.64));
    if(!blocked&&insideDomain(domain,x,y)){bird.x=x;bird.y=y;}
    else{bird.speed=0;target=null;if(!water)change('Idle',1.8+random()*2.2);}
    bird.pace=water?.85+.15*Math.sin(bird.elapsed*.7+index):bird.clip==='Walk'?clamp(bird.speed/(meta.walkSpeedMetresPerSecond*bird.scale),.12,1):1;
    return bird;
  };
  return bird;
}
