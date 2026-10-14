"use strict";

// Verify the actual Three.js Float32 triangulation used by the browser.
import * as T from './vendor/three.module.js';
import {readFileSync} from 'node:fs';

const shell=JSON.parse(readFileSync(new URL('./building-shell.json',import.meta.url),'utf8'));
if(shell.schema!=='bursa-zoo-building-shell/v1')throw Error('Unexpected building shell schema');

function makeShape(outer,holes){
  const shape=new T.Shape();
  outer.forEach(([x,y],i)=>i?shape.lineTo(x,y):shape.moveTo(x,y));shape.closePath();
  for(const ring of holes){
    const hole=new T.Path();
    ring.forEach(([x,y],i)=>i?hole.lineTo(x,y):hole.moveTo(x,y));hole.closePath();
    shape.holes.push(hole);
  }
  return shape;
}

function ringArea(ring){
  let twice=0;
  for(let i=0;i<ring.length-1;i++)twice+=ring[i][0]*ring[i+1][1]-ring[i+1][0]*ring[i][1];
  return Math.abs(twice)/2;
}

let capTriangles=0,capArea=0;
for(const kind of ['roofs','bases'])for(const [partIndex,part] of shell[kind].entries()){
  const geometry=new T.ShapeGeometry(makeShape(part.outer,part.holes));
  const position=geometry.getAttribute('position'),index=geometry.getIndex();
  if(!index||index.count%3)throw Error(`${kind} ${partIndex}: invalid triangle index`);
  let meshArea=0;
  for(let i=0;i<index.count;i+=3){
    const a=index.getX(i),b=index.getX(i+1),c=index.getX(i+2);
    const ax=position.getX(a),ay=position.getY(a);
    const bx=position.getX(b),by=position.getY(b);
    const cx=position.getX(c),cy=position.getY(c);
    const triangleArea=Math.abs((bx-ax)*(cy-ay)-(by-ay)*(cx-ax))/2;
    if(!Number.isFinite(triangleArea)||triangleArea===0)
      throw Error(`${kind} ${partIndex}: zero-area Float32 triangle ${i/3}`);
    meshArea+=triangleArea;capTriangles++;
  }
  const polygonArea=ringArea(part.outer)-part.holes.reduce((sum,hole)=>sum+ringArea(hole),0);
  if(Math.abs(meshArea-polygonArea)>0.005)
    throw Error(`${kind} ${partIndex}: triangulated area changed by ${Math.abs(meshArea-polygonArea)} m2`);
  capArea+=meshArea;
  geometry.dispose();
}

let wallTriangles=0;
for(const [wallIndex,wall] of shell.walls.entries()){
  const [ax,ay]=wall.a.map(Math.fround),[bx,by]=wall.b.map(Math.fround);
  const z0=Math.fround(wall.bottom),z1=Math.fround(wall.top);
  const length=Math.hypot(bx-ax,by-ay),height=z1-z0;
  if(!Number.isFinite(length*height)||length*height<=1e-8)
    throw Error(`wall ${wallIndex}: zero-area Float32 triangle`);
  wallTriangles+=2;
}
console.log(`Float32 mesh verified: ${capTriangles} cap triangles, ${wallTriangles} wall triangles, ${capArea.toFixed(6)} m2 cap area, 0 degenerate`);
