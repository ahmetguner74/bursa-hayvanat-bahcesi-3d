import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import validator from '../../_qa/gltf-check/node_modules/gltf-validator/index.js';
for(const name of ['gergedan-yasam-alani','hayvan/white-rhinoceros','../../15-penguen/model/penguen-havuzu']){
  const uri=new URL('./'+name+'.glb',import.meta.url);
  const report=await validator.validateBytes(new Uint8Array(readFileSync(uri)),{uri:uri.pathname,maxIssues:200});
  const reportName=name.includes('penguen-havuzu')?'../../15-penguen/model/gltf-validation.json':name+'-validation.json';
  writeFileSync(new URL('./'+reportName,import.meta.url),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({name,errors:report.issues.numErrors,warnings:report.issues.numWarnings}));
  assert.equal(report.issues.numErrors,0);assert.equal(report.issues.numWarnings,0);
}
