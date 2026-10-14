import * as T from 'three';

// The official plan locates the dome area; the M5 fence and builder dimensions anchor this provisional shell.
const CAGE = {x:-30,y:-64,angle:9*Math.PI/180,length:70,width:40,height:20};
const mat=(color,roughness=1,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness,side:T.DoubleSide});
const grass=new T.MeshStandardMaterial({map:grassTexture(),roughness:1,side:T.DoubleSide}),waterMat=mat('#4d9da5',.32,.02);
const buildingMat=mat('#a98770'),metalMat=mat('#e9eae2',.68,.14);
const stoneMat=mat('#c6c4ad'),hedgeMat=mat('#567c54'),reedMat=mat('#789462');
const pavementSideMat=mat('#aa987a');

function grassTexture(){
  // A single mottled ground material gives woodland light variation without
  // layering transparent decals over the terrain or path geometry.
  const size=128,pixels=new Uint8Array(size*size*4),field=[];let seed=5021;
  const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
  for(let i=0;i<64;i++)field.push(random()*2-1);
  const lerp=(a,b,t)=>a+(b-a)*t;
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const gx=x/16,gy=y/16,ix=Math.floor(gx),iy=Math.floor(gy),tx=gx-ix,ty=gy-iy;
    const at=(dx,dy)=>field[((iy+dy)&7)*8+((ix+dx)&7)];
    const shade=lerp(lerp(at(0,0),at(1,0),tx),lerp(at(0,1),at(1,1),tx),ty)*21+(random()-.5)*5;
    const p=(y*size+x)*4;
    pixels[p]=Math.max(0,Math.min(255,143+shade));
    pixels[p+1]=Math.max(0,Math.min(255,168+shade));
    pixels[p+2]=Math.max(0,Math.min(255,118+shade*.7));pixels[p+3]=255;
  }
  const texture=new T.DataTexture(pixels,size,size,T.RGBAFormat);
  texture.colorSpace=T.SRGBColorSpace;texture.wrapS=texture.wrapT=T.RepeatWrapping;
  texture.repeat.set(.055,.055);texture.magFilter=T.LinearFilter;texture.minFilter=T.LinearMipmapLinearFilter;
  texture.generateMipmaps=true;texture.anisotropy=4;texture.needsUpdate=true;
  return texture;
}

function pavementTexture(){
  // The selected reference uses warm, compacted gravel rather than a flat grey slab.
  const size=128,pixels=new Uint8Array(size*size*4),coarse=[];let seed=1837;
  const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
  for(let i=0;i<64;i++)coarse.push(random()*2-1);
  const lerp=(a,b,t)=>a+(b-a)*t;
  const sample=(x,y)=>{
    const gx=x/16,gy=y/16,ix=Math.floor(gx),iy=Math.floor(gy),tx=gx-ix,ty=gy-iy;
    const at=(dx,dy)=>coarse[((iy+dy)&7)*8+((ix+dx)&7)];
    return lerp(lerp(at(0,0),at(1,0),tx),lerp(at(0,1),at(1,1),tx),ty);
  };
  // Subtle irregular stone joints break up the broad gravel without a second mesh.
  const pavers=Array.from({length:64},()=>[.2+random()*.6,.2+random()*.6,(random()-.5)*9]);
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const cx=Math.floor(x/16),cy=Math.floor(y/16),gx=x/16,gy=y/16;
    let first=Infinity,second=Infinity,patch=0;
    for(let oy=-1;oy<=1;oy++)for(let ox=-1;ox<=1;ox++){
      const px=cx+ox,py=cy+oy,site=pavers[((py+8)&7)*8+((px+8)&7)];
      const distance=(gx-px-site[0])**2+(gy-py-site[1])**2;
      if(distance<first){second=first;first=distance;patch=site[2];}
      else if(distance<second)second=distance;
    }
    const joint=second-first<.075?-12:0;
    const p=(y*size+x)*4,grain=sample(x,y)*7+(random()-.5)*8+patch+joint,chip=random()<.025?(random()-.5)*30:0;
    pixels[p]=Math.max(0,Math.min(255,220+grain+chip));
    pixels[p+1]=Math.max(0,Math.min(255,203+grain+chip));
    pixels[p+2]=Math.max(0,Math.min(255,174+grain+chip));pixels[p+3]=255;
  }
  const texture=new T.DataTexture(pixels,size,size,T.RGBAFormat);
  texture.colorSpace=T.SRGBColorSpace;texture.wrapS=texture.wrapT=T.RepeatWrapping;
  texture.repeat.set(.22,.22);texture.magFilter=T.LinearFilter;texture.minFilter=T.LinearMipmapLinearFilter;
  texture.generateMipmaps=true;texture.anisotropy=4;texture.needsUpdate=true;
  return texture;
}
const pavementMat=new T.MeshStandardMaterial({map:pavementTexture(),roughness:1,side:T.DoubleSide});

function cageLocal(x,y){
  const dx=x-CAGE.x,dy=y-CAGE.y,c=Math.cos(CAGE.angle),s=Math.sin(CAGE.angle);
  return [dx*c+dy*s,-dx*s+dy*c];
}
function insideCage(x,y,pad=0){const [u,v]=cageLocal(x,y);return (u/(35+pad))**2+(v/(20+pad))**2<1;}
function box(parent,w,d,h,x,y,z,material){const m=new T.Mesh(new T.BoxGeometry(w,d,h),material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}

function shape(points, holes=[]) {
  const s=new T.Shape();points.forEach(([x,y],i)=>i?s.lineTo(x,y):s.moveTo(x,y));s.closePath();
  for(const ring of holes){const h=new T.Path();ring.forEach(([x,y],i)=>i?h.lineTo(x,y):h.moveTo(x,y));h.closePath();s.holes.push(h);}
  return s;
}
function flat(points,material,z,holes=[]){
  const o=new T.Mesh(new T.ShapeGeometry(shape(points,holes)),material);o.position.z=z;o.receiveShadow=true;return o;
}
function ringArea(points){
  let sum=0;for(let i=0;i<points.length;i++){const a=points[i],b=points[(i+1)%points.length];sum+=a[0]*b[1]-b[0]*a[1];}
  return Math.abs(sum)/2;
}
function riverStoneCurbs(rings){
  // One instanced mesh traces the real buffered-road boundary. Rounded stones
  // enter the existing pavement volume, so no second coplanar cap is drawn.
  const samples=[],occupied=new Map(),cell=.76,minDistanceSq=cell*cell;
  const key=(x,y)=>`${x},${y}`;
  const free=(x,y)=>{
    const gx=Math.floor(x/cell),gy=Math.floor(y/cell);
    for(let ix=gx-1;ix<=gx+1;ix++)for(let iy=gy-1;iy<=gy+1;iy++)
      for(const p of occupied.get(key(ix,iy))||[])if((p[0]-x)**2+(p[1]-y)**2<minDistanceSq)return false;
    const bucket=key(gx,gy);if(!occupied.has(bucket))occupied.set(bucket,[]);
    occupied.get(bucket).push([x,y]);return true;
  };
  for(let ri=0;ri<rings.length;ri++){
    const ring=rings[ri];let walked=0,next=.65+(ri%4)*.17;
    for(let i=0;i<ring.length;i++){
      const a=ring[i],b=ring[(i+1)%ring.length],dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
      if(length<.001)continue;
      while(next<=walked+length){
        const t=(next-walked)/length,x=a[0]+dx*t,y=a[1]+dy*t;
        if(free(x,y))samples.push([x,y,Math.atan2(dy,dx)]);
        next+=1.07;
      }
      walked+=length;
    }
  }
  const geometry=new T.IcosahedronGeometry(1,0);
  const material=new T.MeshStandardMaterial({color:'#ffffff',roughness:1});
  const stones=new T.InstancedMesh(geometry,material,samples.length);
  stones.name='Yol sınırındaki alçak dere taşları — M5 yaklaşık güzergâh';
  const palette=['#a79d88','#c0b398','#b2a68e','#d0bea0','#968f7e'];
  const dummy=new T.Object3D();
  for(let i=0;i<samples.length;i++){
    const [x,y,angle]=samples[i],variation=((i*2654435761)>>>0)/4294967296;
    dummy.position.set(x,y,-.125);
    dummy.rotation.set(0,0,angle+(variation-.5)*.45);
    dummy.scale.set(.27+variation*.065,.185+variation*.035,.12+variation*.025);
    dummy.updateMatrix();stones.setMatrixAt(i,dummy.matrix);
    stones.setColorAt(i,new T.Color(palette[i%palette.length]));
  }
  stones.instanceMatrix.needsUpdate=true;stones.instanceColor.needsUpdate=true;
  stones.computeBoundingSphere();stones.receiveShadow=true;
  return stones;
}
function woodlandEdgePlanting(roadRings,pathSurfaces,data,currentPlan){
  // Roadside planting is a single set of instanced low models on terrain.
  // Candidates must stay beyond the paved edge and outside mapped features.
  const containsRing=(ring,x,y)=>{
    let inside=false;
    for(let i=0,j=ring.length-1;i<ring.length;j=i++){
      const a=ring[i],b=ring[j];
      if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;
    }
    return inside;
  };
  const containsSurface=(surface,x,y)=>containsRing(surface.outer,x,y)&&
    !(surface.holes||[]).some(h=>containsRing(h,x,y));
  const forbidden=[];
  for(const f of data.features)if((f.role==='water'||f.role==='building')&&f.closed)
    for(const ring of f.paths)if(ring.length>=4)forbidden.push({outer:ring,holes:[]});
  if(data.alligatorPond?.outer?.length>=4)forbidden.push({outer:data.alligatorPond.outer,holes:[]});
  const entrancePond=currentPlan?.features?.find(f=>f.id==='entrance_pond_5');
  if(entrancePond?.pointsXYMetres?.length>=4)forbidden.push({outer:entrancePond.pointsXYMetres,holes:[]});
  const hash=(x,y,salt=0)=>{
    const n=Math.sin(x*127.1+y*311.7+salt*71.9)*43758.5453;
    return n-Math.floor(n);
  };
  const planted=[],occupied=new Map(),cell=1.05;
  const free=(x,y)=>{
    const gx=Math.floor(x/cell),gy=Math.floor(y/cell);
    for(let ix=gx-1;ix<=gx+1;ix++)for(let iy=gy-1;iy<=gy+1;iy++)
      for(const p of occupied.get(`${ix},${iy}`)||[])if((p[0]-x)**2+(p[1]-y)**2<cell*cell)return false;
    const key=`${gx},${gy}`;if(!occupied.has(key))occupied.set(key,[]);
    occupied.get(key).push([x,y]);return true;
  };
  const suitable=(x,y)=>{
    if(!containsRing(data.outline,x,y)||insideCage(x,y,1.2))return false;
    const [u,v]=cageLocal(x,y);
    if(Math.abs(v)<6.5&&Math.abs(u)>27&&Math.abs(u)<65)return false;
    if(pathSurfaces.some(s=>containsSurface(s,x,y)))return false;
    return !forbidden.some(s=>containsSurface(s,x,y));
  };
  for(let ri=0;ri<roadRings.length;ri++){
    const ring=roadRings[ri];let walked=0,next=2.3+(ri%3)*.57;
    for(let i=0;i<ring.length;i++){
      const a=ring[i],b=ring[(i+1)%ring.length],dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
      if(length<.001)continue;
      while(next<=walked+length){
        const t=(next-walked)/length,x=a[0]+dx*t,y=a[1]+dy*t;
        if(hash(x,y,1)<.78){
          const side=hash(x,y,2)<.5?-1:1,offset=.84+hash(x,y,3)*.42;
          for(const sign of [side,-side]){
            const px=x-sign*dy/length*offset,py=y+sign*dx/length*offset;
            if(suitable(px,py)&&free(px,py)){
              planted.push([px,py,hash(px,py,4),hash(px,py,5)]);
              // Small grouped patches read as undergrowth from a distance.
              for(const direction of [-1,1])if(hash(px,py,7+direction)<.66){
                const distance=1.13+hash(px,py,8+direction)*.25;
                const qx=px+dx/length*direction*distance-sign*dy/length*.18;
                const qy=py+dy/length*direction*distance+sign*dx/length*.18;
                if(suitable(qx,qy)&&free(qx,qy))
                  planted.push([qx,qy,hash(qx,qy,4),hash(qx,qy,5)]);
              }
              break;
            }
          }
        }
        next+=4.45;
      }
      walked+=length;
    }
  }
  const group=new T.Group();group.name='Yol kenarı alçak eğrelti, yer örtücü ve kır çiçekleri — görsel yorum';
  group.userData.sourceKey='landscape';
  if(!planted.length)return group;
  const mound=new T.InstancedMesh(new T.IcosahedronGeometry(1,0),mat('#ffffff'),planted.length);
  mound.name='alçak yer örtücü';
  const frondVertices=[];
  for(let i=0;i<7;i++){
    const angle=2*Math.PI*i/7,radial=.25+(i%3)*.04,h=.44+(i%3)*.065;
    const ux=Math.cos(angle),uy=Math.sin(angle),vx=-uy,vy=ux;
    const base=[0,0,0],left=[ux*radial*.48+vx*.105,uy*radial*.48+vy*.105,h*.44];
    const tip=[ux*radial,uy*radial,h],right=[ux*radial*.48-vx*.105,uy*radial*.48-vy*.105,h*.44];
    frondVertices.push(...base,...left,...tip,...base,...tip,...right);
  }
  const frondGeo=new T.BufferGeometry();frondGeo.setAttribute('position',new T.Float32BufferAttribute(frondVertices,3));frondGeo.computeVertexNormals();
  const fronds=new T.InstancedMesh(frondGeo,new T.MeshStandardMaterial({color:'#ffffff',roughness:1,side:T.DoubleSide}),planted.length);
  fronds.name='yedi yapraklı alçak eğrelti kümesi';
  const flowerSites=planted.filter(([x,y])=>hash(x,y,6)<.27);
  const flowers=new T.InstancedMesh(new T.IcosahedronGeometry(1,0),mat('#ffffff'),flowerSites.length);
  flowers.name='seyrek kır çiçekleri';
  const green=['#436d43','#547d49','#6d9052','#729658','#4b7846'];
  const petals=['#f2e7bd','#fff3d0','#dfd8ac'];
  const dummy=new T.Object3D();
  for(let i=0;i<planted.length;i++){
    const [x,y,a,b]=planted[i];
    dummy.position.set(x,y,-.19);dummy.rotation.set(0,0,a*2*Math.PI);
    dummy.scale.set(.34+b*.12,.26+b*.08,.13+b*.04);
    dummy.updateMatrix();mound.setMatrixAt(i,dummy.matrix);mound.setColorAt(i,new T.Color(green[i%green.length]));
    dummy.position.set(x,y,-.18);dummy.scale.setScalar(.7+a*.4);
    dummy.updateMatrix();fronds.setMatrixAt(i,dummy.matrix);fronds.setColorAt(i,new T.Color(green[(i+2)%green.length]));
  }
  for(let i=0;i<flowerSites.length;i++){
    const [x,y,a,b]=flowerSites[i];
    dummy.position.set(x+(a-.5)*.28,y+(b-.5)*.28,.16+b*.12);
    dummy.rotation.set(0,0,a*6.28);dummy.scale.setScalar(.055+a*.035);
    dummy.updateMatrix();flowers.setMatrixAt(i,dummy.matrix);flowers.setColorAt(i,new T.Color(petals[i%petals.length]));
  }
  for(const mesh of [mound,fronds,flowers]){
    mesh.instanceMatrix.needsUpdate=true;mesh.instanceColor.needsUpdate=true;
    mesh.computeBoundingSphere();mesh.receiveShadow=true;group.add(mesh);
  }
  return group;
}
function cylinderBetween(a,b,r,material,parent){
  const delta=b.clone().sub(a);const o=new T.Mesh(new T.CylinderGeometry(r,r,delta.length(),6),material);
  o.position.copy(a).addScaledVector(delta,.5);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.normalize());parent.add(o);return o;
}

function pointInBox(p,box){
  return p.x>=box.minX&&p.x<=box.maxX&&p.y>=box.minY&&p.y<=box.maxY&&p.z>=box.minZ&&p.z<=box.maxZ;
}
function triangleTouchesBox(a,b,c,box){
  return Math.max(a.x,b.x,c.x)>=box.minX&&Math.min(a.x,b.x,c.x)<=box.maxX&&
    Math.max(a.y,b.y,c.y)>=box.minY&&Math.min(a.y,b.y,c.y)<=box.maxY&&
    Math.max(a.z,b.z,c.z)>=box.minZ&&Math.min(a.z,b.z,c.z)<=box.maxZ;
}
function barOutsideBox(a,b,box){
  let enter=0,leave=1;
  for(const axis of ['x','y','z']){
    const delta=b[axis]-a[axis],low=box['min'+axis.toUpperCase()],high=box['max'+axis.toUpperCase()];
    if(Math.abs(delta)<1e-9){if(a[axis]<low||a[axis]>high)return [[a,b]];continue;}
    const t0=(low-a[axis])/delta,t1=(high-a[axis])/delta;
    enter=Math.max(enter,Math.min(t0,t1));leave=Math.min(leave,Math.max(t0,t1));
    if(enter>=leave)return [[a,b]];
  }
  const parts=[];
  if(enter>1e-5)parts.push([a,a.clone().lerp(b,enter)]);
  if(leave<1-1e-5)parts.push([a.clone().lerp(b,leave),b]);
  return parts;
}
function splitPolygonAtPlane(poly,axis,limit,keepGreater){
  const inside=[],outside=[];
  const signed=p=>keepGreater?p[axis]-limit:limit-p[axis];
  let prev=poly[poly.length-1],prevDistance=signed(prev);
  for(const point of poly){
    const distance=signed(point);
    if((prevDistance>=0)!==(distance>=0)){
      const crossing=prev.clone().lerp(point,prevDistance/(prevDistance-distance));
      inside.push(crossing);outside.push(crossing);
    }
    (distance>=0?inside:outside).push(point);
    prev=point;prevDistance=distance;
  }
  return [inside,outside];
}
function polygonOutsideBox(poly,box){
  // Partition the triangle at each portal plane. Every emitted polygon lies
  // outside at least one plane; only the portion inside all six is discarded.
  const planes=[['x',box.minX,true],['x',box.maxX,false],
    ['y',box.minY,true],['y',box.maxY,false],
    ['z',box.minZ,true],['z',box.maxZ,false]];
  let pending=[poly];const outside=[];
  for(const [axis,limit,keepGreater] of planes){
    const next=[];
    for(const piece of pending){
      const [inside,cut]=splitPolygonAtPlane(piece,axis,limit,keepGreater);
      if(cut.length>=3)outside.push(cut);
      if(inside.length>=3)next.push(inside);
    }
    pending=next;
    if(!pending.length)break;
  }
  return outside;
}

function makeCage(cageLocalSurfaces){
  const root=new T.Group();root.name='Su Kuşları Kafesi — 70 × 40 × 20 m';root.position.set(CAGE.x,CAGE.y,-.09);root.rotation.z=CAGE.angle;
  const N=36,M=18,L=CAGE.length/2,R=CAGE.width/2,H=CAGE.height;
  // Leave the full walk-through volume clear at both portal ends, with a small
  // margin for the thickness of the steel members and their joint spheres.
  const portalBoxes=[-1,1].map(sign=>({
    minX:sign<0?-L-.5:29.5,maxX:sign<0?-29.5:L+.5,
    minY:-1.75,maxY:1.75,minZ:-.2,maxZ:2.8
  }));
  const nodes=[];for(let i=0;i<=N;i++){
    const u=-L+.02+(CAGE.length-.04)*i/N;
    const k=Math.sqrt(Math.max(0,1-(u/L)**2));const row=[];
    for(let j=0;j<=M;j++){
      const a=Math.PI*j/M;row.push(new T.Vector3(u,R*k*Math.cos(a),H*k*Math.sin(a)));
    }nodes.push(row);
  }
  const bars=[];const add=(a,b)=>{
    let parts=[[a,b]];
    for(const box of portalBoxes)parts=parts.flatMap(([start,end])=>barOutsideBox(start,end,box));
    for(const [start,end] of parts)if(start.distanceTo(end)>.08)bars.push([start,end]);
  };
  for(let i=0;i<=N;i++)for(let j=0;j<=M;j++){
    if(i<N)add(nodes[i][j],nodes[i+1][j]);
    if(j<M)add(nodes[i][j],nodes[i][j+1]);
    if(i<N&&j<M)add(nodes[i][j],nodes[i+1][j+1]);
  }
  const nearSteel=new T.Group();nearSteel.name='yakın görünüm — tam tek katlı çelik örgü ve ağ';
  const rodGeo=new T.CylinderGeometry(.052,.052,1,6),nodeGeo=new T.SphereGeometry(.078,6,5);
  const rods=new T.InstancedMesh(rodGeo,metalMat,bars.length);rods.name='çelik üçgen kafes — yaklaşık örgü';
  const visibleNodes=nodes.flat().filter(p=>!portalBoxes.some(box=>pointInBox(p,box)));
  const ball=new T.InstancedMesh(nodeGeo,metalMat,visibleNodes.length);ball.name='çelik birleşim düğümleri';
  const dummy=new T.Object3D();let bi=0;
  for(const [a,b] of bars){const d=b.clone().sub(a);dummy.position.copy(a).addScaledVector(d,.5);dummy.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.clone().normalize());dummy.scale.set(1,d.length(),1);dummy.updateMatrix();rods.setMatrixAt(bi++,dummy.matrix);}
  let ni=0;for(const p of visibleNodes){dummy.position.copy(p);dummy.quaternion.identity();dummy.scale.setScalar(1);dummy.updateMatrix();ball.setMatrixAt(ni++,dummy.matrix);}
  rods.instanceMatrix.needsUpdate=true;ball.instanceMatrix.needsUpdate=true;
  rods.computeBoundingSphere();ball.computeBoundingSphere();
  rods.castShadow=true;ball.castShadow=true;nearSteel.add(rods,ball);
  // The translucent mesh suggests the nylon net without copying a source photo.
  const verts=[];
  for(let i=0;i<N;i++)for(let j=0;j<M;j++){
    for(const triangle of [[nodes[i][j],nodes[i+1][j],nodes[i][j+1]],
      [nodes[i+1][j],nodes[i+1][j+1],nodes[i][j+1]]]){
      let pieces=[triangle];
      for(const portal of portalBoxes){
        if(triangleTouchesBox(...triangle,portal))
          pieces=pieces.flatMap(piece=>polygonOutsideBox(piece,portal));
      }
      for(const piece of pieces)for(let k=1;k<piece.length-1;k++){
        const [a,b,c]=[piece[0],piece[k],piece[k+1]];
        if(new T.Vector3().subVectors(b,a).cross(new T.Vector3().subVectors(c,a)).lengthSq()<1e-10)continue;
        verts.push(a.x,a.y,a.z,b.x,b.y,b.z,c.x,c.y,c.z);
      }
    }
  }
  const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(verts,3));geo.computeVertexNormals();
  const net=new T.Mesh(geo,new T.MeshBasicMaterial({color:'#d1ded9',transparent:true,opacity:.025,side:T.DoubleSide,forceSinglePass:true,depthWrite:false}));
  net.name='tek katlı yarı saydam ağ yorumu';net.raycast=()=>{};nearSteel.add(net);
  // At map scale, the measured tube diameter projects to less than a pixel.
  // Keep the full near structure; show only selected, more contrasted ribs at
  // distance so the open, single-wall dome reads as a cage rather than haze.
  const farSteel=new T.Group();farSteel.name='uzak görünüm — seçilmiş ana kirişler';
  const farBars=[];
  const farDisplayRadius=.09;
  const farPortalClearance=farDisplayRadius+.02;
  // Clip the simplified tubes with their display radius in mind, so even the
  // thick far LOD leaves the same actual walk-through portal volume clear.
  const farPortalBoxes=portalBoxes.map(box=>({
    minX:box.minX-farPortalClearance,maxX:box.maxX+farPortalClearance,
    minY:box.minY-farPortalClearance,maxY:box.maxY+farPortalClearance,
    minZ:box.minZ-farPortalClearance,maxZ:box.maxZ+farPortalClearance
  }));
  const addFar=(a,b)=>{
    let parts=[[a,b]];
    for(const box of farPortalBoxes)parts=parts.flatMap(([start,end])=>barOutsideBox(start,end,box));
    for(const [start,end] of parts)if(start.distanceTo(end)>.2)farBars.push([start,end]);
  };
  const step=3;
  for(let i=0;i<=N;i+=step)for(let j=0;j<=M;j+=step){
    if(i+step<=N)addFar(nodes[i][j],nodes[i+step][j]);
    if(i>0&&i<N&&j+step<=M)addFar(nodes[i][j],nodes[i][j+step]);
    if(i+step<=N&&j+step<=M&&(i/step+j/step)%2===0)
      addFar(nodes[i][j],nodes[i+step][j+step]);
  }
  // 0.09 m is a screen-legibility radius for the sparse far LOD, not a
  // measured pipe size; its 180 mm diameter exceeds the builder's published
  // 42.4–139.7 mm pipe range. The near geometry retains its 0.052 m radius.
  const farRodGeo=new T.CylinderGeometry(farDisplayRadius,farDisplayRadius,1,6);
  // Both LODs share one steel finish. The far silhouette comes from the
  // selected ribs and their screen-space thickness, not a darker substitute.
  const farRods=new T.InstancedMesh(farRodGeo,metalMat,farBars.length);
  farRods.name='uzaktan okunur tek katlı kafes kirişleri';
  for(let i=0;i<farBars.length;i++){
    const [a,b]=farBars[i],delta=b.clone().sub(a);
    dummy.position.copy(a).addScaledVector(delta,.5);
    dummy.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.clone().normalize());
    dummy.scale.set(1,delta.length(),1);dummy.updateMatrix();farRods.setMatrixAt(i,dummy.matrix);
  }
  farRods.instanceMatrix.needsUpdate=true;farRods.computeBoundingSphere();farRods.castShadow=true;farSteel.add(farRods);
  // The two alternatives are mutually exclusive: no second shell or net is
  // drawn on top of the high-detail geometry.
  const cageLod=new T.LOD();cageLod.name='kafes detay düzeyleri';
  cageLod.addLevel(nearSteel,0);cageLod.addLevel(farSteel,85);
  const eye=new T.Vector3(),center=new T.Vector3();let showingFar=false;
  cageLod.update=function(camera){
    const distance=camera.getWorldPosition(eye).distanceTo(this.getWorldPosition(center));
    // Initial desktop and mobile map presets both use the far presentation.
    // Switch back to full detail only after the visitor zooms in explicitly.
    const zoomFactor=camera.isOrthographicCamera?Math.max(1,camera.zoom/11):camera.zoom;
    const apparent=distance/zoomFactor;
    if(showingFar ? apparent<85 : apparent>92)showingFar=!showingFar;
    nearSteel.visible=!showingFar;farSteel.visible=showingFar;
    this._currentLevel=showingFar?1:0;
  };
  root.add(cageLod);
  const portalMat=mat('#535c59'),portalEdge=mat('#8e9892'),gateMat=mat('#273a35');
  for(const sign of [-1,1]){
    const x=sign*32.4;
    const porch=new T.Group();porch.name='İki uçtaki beşik çatılı giriş — fotoğraf eşleştirmesi';root.add(porch);
    porch.userData.sourceKey='entrance';
    // The mutually exclusive path partition owns the walk-through floor.
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
    // The two inner gate leaves are shown swung toward the side walls, so they
    // retain their bars without closing the walk-through opening.
    for(const side of [-1,1]){
      for(const offset of [.14,.48,.82,1.16,1.5])
        box(porch,.06,.045,2.7,inner+sign*offset,side*1.45,1.35,gateMat);
      for(const z of [.22,2.5])box(porch,1.52,.05,.07,inner+sign*.82,side*1.45,z,gateMat);
    }
    box(porch,.07,1.6,.12,face+sign*.02,0,2.78,portalEdge);
  }
  // A three-dimensional perimeter member replaces the coplanar footing ring.
  const foot=new T.InstancedMesh(new T.CylinderGeometry(.09,.09,1,6),metalMat,96);
  foot.name='Kafes çevresi — tek instanslı 3B taban kirişi';foot.castShadow=true;root.add(foot);
  const footing=new T.Object3D();
  for(let i=0;i<96;i++){
    const a=2*Math.PI*i/96,b=2*Math.PI*(i+1)/96;
    const start=new T.Vector3(35*Math.cos(a),20*Math.sin(a),-.015),
      end=new T.Vector3(35*Math.cos(b),20*Math.sin(b),-.015),delta=end.sub(start);
    footing.position.copy(start).addScaledVector(delta,.5);
    footing.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.clone().normalize());
    footing.scale.set(1,delta.length(),1);footing.updateMatrix();foot.setMatrixAt(i,footing.matrix);
  }
  foot.instanceMatrix.needsUpdate=true;foot.computeBoundingSphere();
  const benchWood=mat('#665243'),benchMetal=mat('#31594d');
  const bench=new T.Group();bench.name='Giriş önündeki bank — fotoğraf eşleştirmesi';bench.position.set(48,-8.1,0);root.add(bench);
  box(bench,2.2,.48,.1,0,0,.53,benchWood);box(bench,2.2,.1,.75,0,-.23,.91,benchWood);
  for(const x of [-.85,.85])for(const y of [-.16,.16])box(bench,.07,.07,.48,x,y,.26,benchMetal);
  decorateCage(root,cageLocalSurfaces);
  root.userData.sourceKey='shell';
  root.userData.landmark='cage';
  return root;
}

function decorateCage(root,cageLocalSurfaces){
  const wood=mat('#725341'),woodLight=mat('#977052'),tile=mat('#a75f46');
  // The plan confirms water inside the dome but does not delineate its shore.
  // Keep this lagoon an explicitly interpreted shape beneath the footbridge.
  const lagoon=cageLocalSurfaces.lagoonOutline;
  // The visible lagoon top is produced once by the partitioned site water layer.
  // Rounded individual stones mark the bank without adding another surface.
  const shorePoints=[];
  for(let i=0;i<lagoon.length-1;i++){
    const a=lagoon[i],b=lagoon[i+1],length=Math.hypot(b[0]-a[0],b[1]-a[1]);
    const count=Math.max(1,Math.round(length/.72));
    for(let j=0;j<count;j++){
      const t=(j+.5)/count;
      shorePoints.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);
    }
  }
  const stones=new T.InstancedMesh(new T.IcosahedronGeometry(.33,0),stoneMat,shorePoints.length);
  stones.name='İç gölet kıyısı — tekil 3B taşlar';stones.castShadow=true;stones.receiveShadow=true;
  const stone=new T.Object3D();
  for(let i=0;i<shorePoints.length;i++){
    const [x,y]=shorePoints[i];stone.position.set(x,y,-.025);
    stone.rotation.set((i%7)*.19,(i%5)*.23,(i%11)*.31);
    stone.scale.set(.8+(i%4)*.13,.72+(i%3)*.18,.5+(i%5)*.07);
    stone.updateMatrix();stones.setMatrixAt(i,stone.matrix);
  }
  stones.instanceMatrix.needsUpdate=true;stones.computeBoundingSphere();root.add(stones);
  // The entrance, loop, exit and bridge leads are part of surface-layers.path.
  // Both ends of the crossing extend onto dry ground beyond the pond shore.
  const bridge=new T.Group();bridge.name='Gölet üzerindeki ahşap köprü — görsel yorum';root.add(bridge);
  bridge.userData.sourceKey='landscape';
  const x0=-18.8,x1=10.0,by=2.2,bw=2.35,n=25;
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
  // The west bank path enters the lagoon before the straight crossing. A
  // raised timber ramp covers only that water crossing, as an actual 3D deck.
  const [rampStart,rampEnd]=cageLocalSurfaces.westernBridgeRamp;
  const rdx=rampEnd[0]-rampStart[0],rdy=rampEnd[1]-rampStart[1],rl=Math.hypot(rdx,rdy);
  const rangle=Math.atan2(rdy,rdx),rnx=-rdy/rl,rny=rdx/rl,rn=11;
  const rampHeight=t=>-.035+.265*t;
  for(let i=0;i<rn;i++){
    const t=(i+.5)/rn;
    const plank=box(bridge,rl/rn-.03,2.2,.14,
      rampStart[0]+rdx*t,rampStart[1]+rdy*t,rampHeight(t),woodLight);
    plank.rotation.z=rangle;
  }
  for(const side of [-1,1]){
    const rail=[];
    for(let i=0;i<=5;i++){
      const t=i/5,x=rampStart[0]+rdx*t+side*rnx*(bw/2+.07),
        y=rampStart[1]+rdy*t+side*rny*(bw/2+.07),z=rampHeight(t);
      box(bridge,.1,.1,.85,x,y,z+.45,wood);
      rail.push(new T.Vector3(x,y,z+.94));
    }
    for(let i=1;i<rail.length;i++)cylinderBetween(rail[i-1],rail[i],.055,wood,bridge);
    cylinderBetween(rail.at(-1),new T.Vector3(x0,by+side*(bw/2+.07),.23+.95),.055,wood,bridge);
  }
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

export function createSite(data,currentPlan,surfaceData,buildingShellData){
  if(surfaceData?.schema!=='bursa-zoo-planar-surface-partition/v1')throw Error('Bölünmüş zemin verisi eksik veya uyumsuz');
  if(buildingShellData?.schema!=='bursa-zoo-building-shell/v1')throw Error('Birleşik bina kabuğu verisi eksik veya uyumsuz');
  const anchor=currentPlan?.features?.find(f=>f.id==='waterbird_aviary_dome_candidate')?.modelAnchor;
  const centre=anchor?.provisionalShellCentreXYMetres;
  const dimensions=anchor?.independentMajorMinorDimensionsMetres;
  if(centre?.length===2&&centre.every(Number.isFinite)&&Number.isFinite(anchor.provisionalShellAngleDegreesCounterclockwiseFromEast)&&dimensions?.length===2&&dimensions.every(n=>Number.isFinite(n)&&n>0)){
    CAGE.x=centre[0];CAGE.y=centre[1];CAGE.angle=anchor.provisionalShellAngleDegreesCounterclockwiseFromEast*Math.PI/180;
    CAGE.length=dimensions[0];CAGE.width=dimensions[1];
  }
  const site=new T.Group();site.name='Bursa Hayvanat Bahçesi — 2026 kroki ve M5 yerleşimi';
  const surfaceLayers=surfaceData.layers;
  for(const p of surfaceLayers.terrain){
    const ground=flat(p.outer,grass,-.24,p.holes);
    ground.name='OSM sınırı içi · çakışmasız çim yüzey';site.add(ground);
  }
  const roadBoundaryRings=[];
  for(const p of surfaceLayers.path){
    // The provisional path caps own their XY regions; no water or building cap is below them.
    roadBoundaryRings.push(p.outer,...p.holes);
    const geometry=new T.ExtrudeGeometry(shape(p.outer,p.holes),{depth:.135,steps:1,bevelEnabled:false,curveSegments:1});
    const m=new T.Mesh(geometry,[pavementMat,pavementSideMat]);
    m.position.z=-.24;m.receiveShadow=true;
    m.name='M5 yol çizgilerinden türetilmiş alçak kaplama · yaklaşık genişlik';site.add(m);
  }
  site.add(riverStoneCurbs(roadBoundaryRings));
  for(const p of surfaceLayers.water){
    const pond=flat(p.outer,waterMat,-.135,p.holes);
    pond.name='M5 ve 2026 kroki · çakışmasız su yüzeyi';
    pond.userData.sourceKey='surfacePartition';site.add(pond);
  }
  // DGN curb and other survey lines remain in site-data.json for later plan alignment.
  const footprints=new T.Group();footprints.name='M5 yapı izlerinden tekil dış kabuk · aşamalı modelleme';site.add(footprints);
  // Roof polygons partition the footprint by its highest source elevation.
  // One wall is emitted at each outside edge or roof-height step; there are no
  // overlapping closed building extrusions or internal coplanar wall faces.
  for(const p of buildingShellData.bases){
    const base=flat(p.outer,buildingMat,buildingShellData.baseZ,p.holes);
    const indices=base.geometry.getIndex()?.array;
    if(indices){for(let i=0;i<indices.length;i+=3){const swap=indices[i+1];indices[i+1]=indices[i+2];indices[i+2]=swap;}
      base.geometry.getIndex().needsUpdate=true;base.geometry.computeVertexNormals();}
    base.name='M5 yapı kabuğu · tekil alt kapak';footprints.add(base);
  }
  for(const p of buildingShellData.roofs){
    const roof=flat(p.outer,buildingMat,p.z,p.holes);
    roof.castShadow=true;roof.name=p.sourceId+' · tekil çatı';footprints.add(roof);
  }
  const wallVertices=[];
  for(const wall of buildingShellData.walls){
    const [ax,ay]=wall.a,[bx,by]=wall.b,z0=wall.bottom,z1=wall.top;
    wallVertices.push(ax,ay,z0,bx,by,z0,bx,by,z1,ax,ay,z0,bx,by,z1,ax,ay,z1);
  }
  if(wallVertices.length){
    const geometry=new T.BufferGeometry();
    geometry.setAttribute('position',new T.Float32BufferAttribute(wallVertices,3));
    geometry.computeVertexNormals();
    const walls=new T.Mesh(geometry,buildingMat);
    walls.castShadow=true;walls.receiveShadow=true;walls.name='M5 yapı dış duvarları · tekil kot geçişleri';footprints.add(walls);
  }
  const trees=new T.Group();trees.name='M5 ağaç sembollerinden temsili bitki örtüsü';site.add(trees);
  const containsRing=(ring,x,y)=>{
    let inside=false;
    for(let i=0,j=ring.length-1;i<ring.length;j=i++){
      const a=ring[i],b=ring[j];
      if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;
    }
    return inside;
  };
  const onTerrain=([x,y])=>surfaceLayers.terrain.some(s=>
    containsRing(s.outer,x,y)&&!(s.holes||[]).some(h=>containsRing(h,x,y)));
  // Old tree symbols are retained in site-data.json. The 2026-derived paving
  // and water own their regions, so their 59 conflicting tree models are culled.
  const positions=(data.treeClusters||[]).filter(c=>onTerrain(c.xy)).map(c=>({p:c.xy,id:c.sourceIds[0]}));
  trees.userData.culledSourceTreeCount=(data.treeClusters||[]).length-positions.length;
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
    d.position.set(p[0],p[1],-.24+h*.33);d.rotation.set(Math.PI/2,0,0);d.scale.set(1.12,h*.66,1.12);d.updateMatrix();trunks.setMatrixAt(i,d.matrix);
    for(let l=0;l<3;l++){
      const a=((seed%360)*Math.PI/180)+l*2.09,offset=l===0?0:r*.42;
      d.position.set(p[0]+Math.cos(a)*offset,p[1]+Math.sin(a)*offset,-.24+h*(l===0?.77:.84));
      d.scale.set(r*(l===0?.9:.65),r*(l===0?.82:.7),r*(l===0?.83:.62));d.rotation.set(0,0,a*.22);d.updateMatrix();
      crowns.setMatrixAt(i*3+l,d.matrix);
      crowns.setColorAt(i*3+l,new T.Color(leafColors[(seed+l)%leafColors.length]));
    }
    i++;
  }
  trunks.instanceMatrix.needsUpdate=true;crowns.instanceMatrix.needsUpdate=true;crowns.instanceColor.needsUpdate=true;
  trunks.castShadow=true;crowns.castShadow=true;trees.add(trunks,crowns);
  trees.add(woodlandEdgePlanting(roadBoundaryRings,surfaceLayers.path,data,currentPlan));
  const cage=makeCage(surfaceData.cageLocal);site.add(cage);
  return {site,cage,trees,footprints};
}

export {CAGE};
