import * as T from 'three';

const CAGE = {x:-223,y:-126,angle:Math.PI/12,length:70,width:40,height:20};
const mat=(color,roughness=1,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness,side:T.DoubleSide});
const grass=mat('#8eaa78'),pathMat=mat('#d1c9b5'),waterMat=new T.MeshPhysicalMaterial({color:'#4d9da5',roughness:.32,metalness:.02,transparent:true,opacity:.92,side:T.DoubleSide});
const buildingMat=mat('#a98770'),roofMat=mat('#b98765'),metalMat=mat('#e9eae2',.68,.14);
const stoneMat=mat('#c6c4ad'),hedgeMat=mat('#567c54'),reedMat=mat('#789462');

function cageLocal(x,y){
  const dx=x-CAGE.x,dy=y-CAGE.y,c=Math.cos(CAGE.angle),s=Math.sin(CAGE.angle);
  return [dx*c+dy*s,-dx*s+dy*c];
}
function insideCage(x,y,pad=0){const [u,v]=cageLocal(x,y);return (u/(35+pad))**2+(v/(20+pad))**2<1;}
function ribbon(points,width,material,z,closed=false){
  const v=[],ix=[];const count=points.length;
  for(let i=0;i<count;i++){
    const prev=points[(i-1+count)%count],next=points[(i+1)%count];
    const a=!closed&&i===0?points[0]:prev,b=!closed&&i===count-1?points[count-1]:next;
    const dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy)||1,nx=-dy/len*width/2,ny=dx/len*width/2;
    v.push(points[i][0]+nx,points[i][1]+ny,z,points[i][0]-nx,points[i][1]-ny,z);
  }
  for(let i=0;i<(closed?count:count-1);i++){const a=2*i,b=2*((i+1)%count);ix.push(a,a+1,b,a+1,b+1,b);}
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(v,3));g.setIndex(ix);g.computeVertexNormals();
  return new T.Mesh(g,material);
}
function curvePoints(points,samples=56){const curve=new T.CatmullRomCurve3(points.map(([x,y])=>new T.Vector3(x,y,0)),false,'centripetal');return curve.getPoints(samples).map(p=>[p.x,p.y]);}
function box(parent,w,d,h,x,y,z,material){const m=new T.Mesh(new T.BoxGeometry(w,d,h),material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}

function shape(points, holes=[]) {
  const s=new T.Shape();points.forEach(([x,y],i)=>i?s.lineTo(x,y):s.moveTo(x,y));s.closePath();
  for(const ring of holes){const h=new T.Path();ring.forEach(([x,y],i)=>i?h.lineTo(x,y):h.moveTo(x,y));h.closePath();s.holes.push(h);}
  return s;
}
function flat(points,material,z,holes=[]){
  const o=new T.Mesh(new T.ShapeGeometry(shape(points,holes)),material);o.position.z=z;o.receiveShadow=true;return o;
}
function segments(items,color,z){
  const verts=[];for(const f of items)for(const path of f.paths)for(let i=1;i<path.length;i++){
    verts.push(path[i-1][0],path[i-1][1],z,path[i][0],path[i][1],z);
  }
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(verts,3));
  return new T.LineSegments(g,new T.LineBasicMaterial({color,transparent:true,opacity:.85}));
}
function cylinderBetween(a,b,r,material,parent){
  const delta=b.clone().sub(a);const o=new T.Mesh(new T.CylinderGeometry(r,r,delta.length(),6),material);
  o.position.copy(a).addScaledVector(delta,.5);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.normalize());parent.add(o);return o;
}

function makeCage(){
  const root=new T.Group();root.name='Su Kuşları Kafesi — 70 × 40 × 20 m';root.position.set(CAGE.x,CAGE.y,-.09);root.rotation.z=CAGE.angle;
  const N=36,M=18,L=CAGE.length/2,R=CAGE.width/2,H=CAGE.height;
  const nodes=[];for(let i=0;i<=N;i++){
    const u=-L+.02+(CAGE.length-.04)*i/N;
    const k=Math.sqrt(Math.max(0,1-(u/L)**2));const row=[];
    for(let j=0;j<=M;j++){
      const a=Math.PI*j/M;row.push(new T.Vector3(u,R*k*Math.cos(a),H*k*Math.sin(a)));
    }nodes.push(row);
  }
  const bars=[];const add=(a,b)=>{if(a.distanceTo(b)>.08)bars.push([a,b]);};
  for(let i=0;i<=N;i++)for(let j=0;j<=M;j++){
    if(i<N)add(nodes[i][j],nodes[i+1][j]);
    if(j<M)add(nodes[i][j],nodes[i][j+1]);
    if(i<N&&j<M)add(nodes[i][j],nodes[i+1][j+1]);
  }
  const rodGeo=new T.CylinderGeometry(.052,.052,1,6),nodeGeo=new T.SphereGeometry(.095,6,5);
  const rods=new T.InstancedMesh(rodGeo,metalMat,bars.length);rods.name='çelik üçgen kafes — yaklaşık örgü';
  const ball=new T.InstancedMesh(nodeGeo,metalMat,(N+1)*(M+1));ball.name='çelik birleşim düğümleri';
  const dummy=new T.Object3D();let bi=0;
  for(const [a,b] of bars){const d=b.clone().sub(a);dummy.position.copy(a).addScaledVector(d,.5);dummy.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.clone().normalize());dummy.scale.set(1,d.length(),1);dummy.updateMatrix();rods.setMatrixAt(bi++,dummy.matrix);}
  let ni=0;for(const row of nodes)for(const p of row){dummy.position.copy(p);dummy.quaternion.identity();dummy.scale.setScalar(1);dummy.updateMatrix();ball.setMatrixAt(ni++,dummy.matrix);}
  rods.castShadow=true;ball.castShadow=true;root.add(rods,ball);
  // The translucent mesh suggests the nylon net without copying a source photo.
  const verts=[],indices=[];
  for(const row of nodes)for(const p of row)verts.push(p.x,p.y,p.z);
  for(let i=0;i<N;i++)for(let j=0;j<M;j++){
    const a=i*(M+1)+j,b=(i+1)*(M+1)+j;indices.push(a,b,a+1,b,b+1,a+1);
  }
  const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(verts,3));geo.setIndex(indices);geo.computeVertexNormals();
  const net=new T.Mesh(geo,new T.MeshBasicMaterial({color:'#d1ded9',transparent:true,opacity:.025,side:T.DoubleSide,depthWrite:false}));net.name='yarı saydam ağ yorumu';net.raycast=()=>{};root.add(net);
  const portalMat=mat('#535c59'),portalEdge=mat('#8e9892'),gateMat=mat('#273a35');
  for(const sign of [-1,1]){
    const x=sign*32.4;
    const porch=new T.Group();porch.name='İki uçtaki beşik çatılı giriş — fotoğraf eşleştirmesi';root.add(porch);
    porch.userData.sourceKey='entrance';
    box(porch,5.8,5.2,.12,x,0,-.03,pathMat);
    for(const side of [-1,1]){
      box(porch,5.6,.18,3.25,x,side*2.57,1.62,portalMat);
      const slope=box(porch,5.9,3.04,.19,x,side*1.25,3.94,portalEdge);slope.rotation.x=-side*.54;
      cylinderBetween(new T.Vector3(x-sign*2.75,side*2.57,0),new T.Vector3(x-sign*2.75,side*2.57,3.25),.11,portalEdge,porch);
    }
    const face=x+sign*2.91;
    box(porch,.14,1.0,3.15,face,-2.05,1.56,portalMat);
    box(porch,.14,1.0,3.15,face,2.05,1.56,portalMat);
    box(porch,.14,3.2,.5,face,0,2.9,portalMat);
    const gable=new T.BufferGeometry();gable.setAttribute('position',new T.Float32BufferAttribute([
      face,-2.62,3.12,face,2.62,3.12,face,0,4.72
    ],3));gable.computeVertexNormals();porch.add(new T.Mesh(gable,portalMat));
    const inner=face-sign*5.55;
    const shade=new T.Mesh(new T.PlaneGeometry(3.15,2.55),new T.MeshBasicMaterial({color:'#1c2a26',transparent:true,opacity:.36,side:T.DoubleSide,depthWrite:false}));
    shade.rotation.y=Math.PI/2;shade.position.set(inner,0,1.38);porch.add(shade);
    for(const y of [-1.36,-.68,0,.68,1.36])box(porch,.06,.045,2.7,inner+sign*.05,y,1.35,gateMat);
    box(porch,.07,1.6,.12,face+sign*.02,0,2.78,portalEdge);
  }
  const foot=new T.Mesh(new T.RingGeometry(19.87,20.08,96),mat('#a9afaa'));
  foot.scale.set(1.75,1,1);foot.position.z=-.075;root.add(foot);
  const approach=curvePoints([[35,0],[40.5,0],[48,-1.3],[57,-1.7]],28);
  const access=ribbon(approach,5.1,pathMat,-.06);access.name='Girişe uzanan açık renk yaya yolu — fotoğraf eşleştirmesi';access.userData.sourceKey='entrance';root.add(access);
  const benchWood=mat('#665243'),benchMetal=mat('#31594d');
  const bench=new T.Group();bench.name='Giriş önündeki bank — fotoğraf eşleştirmesi';bench.position.set(48,-8.1,0);root.add(bench);
  box(bench,2.2,.48,.1,0,0,.53,benchWood);box(bench,2.2,.1,.75,0,-.23,.91,benchWood);
  for(const x of [-.85,.85])for(const y of [-.16,.16])box(bench,.07,.07,.48,x,y,.26,benchMetal);
  decorateCage(root);
  root.userData.sourceKey='shell';
  root.userData.landmark='cage';
  return root;
}

function decorateCage(root){
  const lightPath=mat('#d9d3bf'),wood=mat('#725341'),woodLight=mat('#977052'),tile=mat('#a75f46');
  const loop=[];for(let i=0;i<80;i++){
    const a=2*Math.PI*i/80;
    loop.push([23.8*Math.cos(a)+1.1*Math.sin(3*a),14.4*Math.sin(a)+1.1*Math.cos(2*a)]);
  }
  const walk=ribbon(loop,2.25,lightPath,.02,true);walk.name='İç gezi yolu — görsel yorum';walk.receiveShadow=true;root.add(walk);
  walk.userData.sourceKey='landscape';
  const entry=curvePoints([[-33.9,0],[-29.2,-1.5],[-25.1,-5.2],[-22,-8.3]],26);
  root.add(ribbon(entry,2.35,lightPath,.025));
  const exit=curvePoints([[23,-3.4],[27.8,-1.8],[33.9,0]],24);root.add(ribbon(exit,2.35,lightPath,.025));
  // Both ends of the crossing extend onto dry ground beyond the pond shore.
  const bridge=new T.Group();bridge.name='Gölet üzerindeki ahşap köprü — görsel yorum';root.add(bridge);
  bridge.userData.sourceKey='landscape';
  const x0=-18.8,x1=8.6,by=2.2,bw=2.35,n=24;
  for(let i=0;i<n;i++){
    const x=x0+(x1-x0)*(i+.5)/n,raise=.23+.43*Math.sin(Math.PI*(i+.5)/n);
    box(bridge,(x1-x0)/n-.03,bw,.14,x,by,raise,woodLight);
    if(i%3===0)for(const side of [-1,1])box(bridge,.12,.12,.9,x,by+side*(bw/2+.07),raise+.48,wood);
  }
  for(const side of [-1,1]){
    const rail=[];for(let i=0;i<=n;i++){
      const x=x0+(x1-x0)*i/n,z=.23+.43*Math.sin(Math.PI*i/n)+.95;
      rail.push(new T.Vector3(x,by+side*(bw/2+.07),z));
    }
    for(let i=1;i<rail.length;i++)cylinderBetween(rail[i-1],rail[i],.055,wood,bridge);
  }
  const bridgeLead=curvePoints([[-23,-7],[-21,-2.7],[-18.8,2.2]],22);root.add(ribbon(bridgeLead,2.2,lightPath,.03));
  const millLead=curvePoints([[8.7,2.2],[11.4,4.5],[16,6.5],[22,6]],22);root.add(ribbon(millLead,2.0,lightPath,.03));

  const mill=new T.Group();mill.name='Ahşap kuş evi / değirmen silueti — fotoğraf eşleştirmesi';mill.position.set(13,5,0);root.add(mill);mill.userData.sourceKey='mill';
  box(mill,7.4,5.5,.22,0,0,.16,wood);
  const timberWall=mat('#594638');
  box(mill,6.65,4.68,4.75,0,0,3.05,timberWall);
  for(const side of [-1,1]){
    for(let b=-14;b<=14;b++)box(mill,.075,.085,4.55,b*.215,side*2.4,3.06,woodLight);
    box(mill,1.55,.09,1.65,-1.55,side*2.48,3.55,mat('#26302a'));
    box(mill,1.55,.09,1.65,1.55,side*2.48,3.55,mat('#26302a'));
  }
  for(const sx of [-1,1])for(const sy of [-1,1]){
    const x=sx*3.25,y=sy*2.3;
    box(mill,.23,.23,6.15,x,y,3.2,wood);
    cylinderBetween(new T.Vector3(x,y,.48),new T.Vector3(x-sx*1.5,y,3.1),.07,wood,mill);
  }
  for(const z of [2.85,5.55]){
    box(mill,7.25,5.4,.22,0,0,z,woodLight);
    for(const sy of [-1,1]){
      box(mill,7.3,.1,.12,0,sy*2.66,z+1.0,wood);
      for(let i=-3;i<=3;i++)box(mill,.08,.08,.95,i*1.05,sy*2.66,z+.55,wood);
    }
  }
  for(const sy of [-1,1]){
    const roof=box(mill,8.0,3.5,.19,0,sy*1.45,6.8,tile);roof.rotation.x=-sy*.55;
  }
  for(let step=0;step<14;step++){
    const y=-4.25+step*.57,z=.42+step*.34;
    box(mill,1.28,.42,.13,-4.08,y,z,woodLight);
  }
  for(const x of [-4.75,-3.42])cylinderBetween(new T.Vector3(x,-4.55,.6),new T.Vector3(x,3.35,5.35),.06,wood,mill);
  const wheel=new T.Mesh(new T.TorusGeometry(1.15,.12,6,18),wood);wheel.position.set(-3.85,-.6,1.55);wheel.rotation.y=Math.PI/2;mill.add(wheel);
  for(let i=0;i<8;i++){
    const a=2*Math.PI*i/8;
    cylinderBetween(new T.Vector3(-3.85,-.6,1.55),new T.Vector3(-3.85,-.6+Math.cos(a)*1.13,1.55+Math.sin(a)*1.13),.052,wood,mill);
  }

  // A low planted rim keeps the dome grounded, leaving both entrance axes open.
  const shrubs=new T.Group();shrubs.name='Kafes çevresi ve içindeki çalı kütleleri — görsel yorum';root.add(shrubs);
  shrubs.userData.sourceKey='landscape';
  const shrubGeo=new T.IcosahedronGeometry(1,1),bushes=[];
  for(let i=0;i<94;i++){
    const a=2*Math.PI*i/94,jitter=.72*Math.sin(i*2.33)+.42*Math.cos(i*.81),u=(36.1+jitter)*Math.cos(a),v=(21.1+jitter)*Math.sin(a);
    if(Math.abs(v)<3.4&&Math.abs(u)>31)continue;
    const r=.62+(i%8)*.11; bushes.push([u,v,r*.62,r]);
  }
  for(const [x,y] of [[-22,9],[-18,11],[-5,12],[0,13],[18,-8],[21,8],[-20,-10],[22,-4],[-4,-13],[9,-11]])
    for(let k=0;k<4;k++)bushes.push([x+(k%2)*1.1,y+Math.floor(k/2)*.95,.42,.65+(k%3)*.13]);
  for(const [x,y] of [[28,7],[29,-7],[43,7],[45,-8],[-29,6]])for(let k=0;k<4;k++){
    const r=1.05+.19*k;bushes.push([x+(k%2)*1.2,y+Math.floor(k/2)*1.2,r*.75,r]);
  }
  const im=new T.InstancedMesh(shrubGeo,mat('#ffffff'),bushes.length),d=new T.Object3D();
  const bushColors=['#486e4d','#5b8050','#779361','#6b8760','#668e59'];
  bushes.forEach(([x,y,z,r],i)=>{d.position.set(x,y,z);d.scale.set(r,r*.82,r*.78);d.rotation.set(0,0,i*1.63);d.updateMatrix();im.setMatrixAt(i,d.matrix);im.setColorAt(i,new T.Color(bushColors[i%bushColors.length]));});
  im.castShadow=true;shrubs.add(im);
  const conifer=new T.Group();conifer.name='Kafes içi iğne yapraklı kümeler — görsel yorum';root.add(conifer);conifer.userData.sourceKey='landscape';
  const needleMats=[mat('#42684f'),mat('#537456'),mat('#68835a')];
  for(const [k,[x,y,h]] of [[-23,8,5.6],[-18,10,6.1],[-11,12,4.8],[17,-10,5.9],[21,7,6.6],[9,12,5.4]].entries()){
    box(conifer,.17,.17,h*.55,x,y,h*.27,wood);
    for(let t=0;t<3;t++){
      const cone=new T.Mesh(new T.ConeGeometry(1.12*(1-t*.19),h*.5,6),needleMats[(k+t)%3]);
      cone.rotation.x=Math.PI/2;cone.position.set(x,y,h*(.41+t*.19));cone.castShadow=true;conifer.add(cone);
    }
  }
}

export function createSite(data){
  const site=new T.Group();site.name='Bursa Hayvanat Bahçesi — M5 kaynak çizgileri';
  let cagePondMesh=null;
  const ground=flat(data.outline,grass,-.24);ground.name='OSM bahçe sınırı içi — düz önizleme zemin';site.add(ground);
  for(const p of data.walkSurfaces){const m=flat(p.outer,pathMat,-.17,p.holes);m.name='DGN yol kenarından türetilmiş yaklaşık yol yüzeyi';site.add(m);}
  const water=data.features.filter(f=>f.role==='water');
  for(const f of water)if(f.closed)for(const p of f.paths)if(p.length>=4){const m=flat(p,waterMat,-.095);m.name=f.id+' · M5 havuz';site.add(m);}
  if(data.cagePond?.outer?.length>3){
    const p=data.cagePond.outer,open=p[0][0]===p[p.length-1][0]&&p[0][1]===p[p.length-1][1]?p.slice(0,-1):p;
    const pond=flat(p,waterMat,-.052);pond.name='Su Kuşları Kafesi göleti · birleşen M5 su kenarları';pond.userData.sourceKey='pond';site.add(pond);cagePondMesh=pond;
    const bank=ribbon(open,.88,stoneMat,-.045,true);bank.name='Gölet taş kıyısı — görsel yorum';site.add(bank);
    const shore=new T.Group();shore.name='Gölet kaya ve saz kümeleri — görsel yorum';site.add(shore);
    const rockGeo=new T.IcosahedronGeometry(1,0),reedGeo=new T.ConeGeometry(1,1,4),rocks=[],reeds=[];
    for(let i=0;i<open.length;i+=Math.max(1,Math.floor(open.length/23))){
      const [x,y]=open[i],seed=(i*17)%11;
      if(i%3!==0)rocks.push([x+((seed%3)-1)*.27,y+((seed%5)-2)*.19,.34,.46+seed*.035]);
      if(i%2===0)reeds.push([x+((seed%4)-1)*.38,y+((seed%3)-1)*.3,.55,1.15+seed*.09]);
    }
    const d=new T.Object3D(),rm=new T.InstancedMesh(rockGeo,stoneMat,rocks.length),gm=new T.InstancedMesh(reedGeo,reedMat,reeds.length);
    rocks.forEach(([x,y,z,r],i)=>{d.position.set(x,y,z);d.scale.set(r,r*.72,r*.55);d.rotation.set(0,0,i*.83);d.updateMatrix();rm.setMatrixAt(i,d.matrix);});
    reeds.forEach(([x,y,z,h],i)=>{d.position.set(x,y,z);d.scale.set(.21,.21,h);d.rotation.set(0,0,i*.71);d.updateMatrix();gm.setMatrixAt(i,d.matrix);});
    shore.add(rm,gm);
  }
  site.add(segments(data.features.filter(f=>f.role==='road_edge'),'#7b7866',-.08));
  site.add(segments(data.features.filter(f=>f.role==='curb'),'#e5d7b7',-.05));
  site.add(segments(data.features.filter(f=>f.role==='fence'),'#576652',.05));
  site.add(segments(data.features.filter(f=>f.role==='wall'),'#746d62',.055));
  site.add(segments(data.features.filter(f=>f.role==='water'&&!f.closed),'#438fa8',-.07));
  const footprints=new T.Group();footprints.name='Diğer yapı izleri — aşamalı modelleme';site.add(footprints);
  for(const f of data.features)if(f.role==='building'&&f.closed)for(const p of f.paths){
    if(p.length<4)continue;
    const height=Math.max(2,Math.min(8,f.sourceH-93.5));
    const mesh=new T.Mesh(new T.ExtrudeGeometry(shape(p),{depth:height,bevelEnabled:false,curveSegments:3}),buildingMat);
    mesh.position.z=.02;mesh.castShadow=true;mesh.receiveShadow=true;mesh.name=f.id+' · aday kütle';footprints.add(mesh);
  }
  const canopy=new T.Group();canopy.name='DGN sundurma izleri';site.add(canopy);
  for(const f of data.features)if(f.role==='canopy'&&f.closed)for(const p of f.paths){
    if(p.length<4)continue;
    const cx=p.reduce((a,v)=>a+v[0],0)/p.length,cy=p.reduce((a,v)=>a+v[1],0)/p.length;
    if(insideCage(cx,cy))continue;
    const m=flat(p,roofMat,Math.max(1.3,Math.min(6,f.sourceH-93.5)));
    m.name=f.id+' · kaynak sundurma üst izi';canopy.add(m);
  }
  const trees=new T.Group();trees.name='M5 ağaç sembollerinden temsili bitki örtüsü';site.add(trees);
  const positions=(data.treeClusters||[]).map(c=>({p:c.xy,id:c.sourceIds[0]}));
  const trunkMat=mat('#796b4e'),leafMat=mat('#ffffff');
  const trunks=new T.InstancedMesh(new T.CylinderGeometry(.18,.27,1,5),trunkMat,positions.length);
  const crowns=new T.InstancedMesh(new T.IcosahedronGeometry(1,1),leafMat,positions.length*3);
  const d=new T.Object3D();let i=0;
  const leafColors=['#638d5b','#789d69','#86a673','#a0ae76','#6e9561'];
  for(const {p,id} of positions){let seed=0;for(const c of id)seed=(seed*31+c.charCodeAt(0))>>>0;
    const within=insideCage(p[0],p[1],-1),[u,v]=cageLocal(p[0],p[1]);
    const dome=20*Math.sqrt(Math.max(0,1-(u/35)**2-(v/20)**2));
    const entranceClearing=u>38&&u<50&&Math.abs(v)<4;
    const h=entranceClearing?1.8:within?Math.min(11.4,Math.max(2.6,dome-2.2),8.7+(seed%36)/10):4.6+(seed%43)/10;
    const r=entranceClearing?.65:within?1.7+(seed%19)/12:1.4+(seed%19)/10;
    // CylinderGeometry runs along local Y; stand it upright in this Z-up scene.
    d.position.set(p[0],p[1],h*.33);d.rotation.set(Math.PI/2,0,0);d.scale.set(1.12,h*.66,1.12);d.updateMatrix();trunks.setMatrixAt(i,d.matrix);
    for(let l=0;l<3;l++){
      const a=((seed%360)*Math.PI/180)+l*2.09,offset=l===0?0:r*.42;
      d.position.set(p[0]+Math.cos(a)*offset,p[1]+Math.sin(a)*offset,h*(l===0?.77:.84));
      d.scale.set(r*(l===0?.9:.65),r*(l===0?.82:.7),r*(l===0?.83:.62));d.rotation.set(0,0,a*.22);d.updateMatrix();
      crowns.setMatrixAt(i*3+l,d.matrix);
      crowns.setColorAt(i*3+l,new T.Color(leafColors[(seed+l)%leafColors.length]));
    }
    i++;
  }
  trunks.instanceMatrix.needsUpdate=true;crowns.instanceMatrix.needsUpdate=true;crowns.instanceColor.needsUpdate=true;
  trunks.castShadow=true;crowns.castShadow=true;trees.add(trunks,crowns);
  const cage=makeCage();site.add(cage);
  return {site,cage,trees,footprints,canopy,pond:cagePondMesh};
}

export {CAGE};
