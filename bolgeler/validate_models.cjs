// Local Khronos validator runner. No network, publishing or browser upload.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
let validator;
try{validator=require('./_qa/gltf-check/node_modules/gltf-validator');}
catch(error){console.error('Install the pinned local verifier: npm install --prefix bolgeler/_qa/gltf-check --ignore-scripts --no-audit --no-fund gltf-validator@2.0.0-dev.3.10');process.exit(1);}
const targets=[
  ['15-penguen/model/hayvan/african-penguin.glb','gltf-validation.json'],
  ['29-boz-ayi/model/boz-ayi-havuz-kiyisi.glb','gltf-validation.json'],
  ['09-habes-maymunu/model/habes-maymunu-adasi.glb','gltf-validation.json'],
  ['31-pelikan-goleti/model/su-kuslari-kubbesi-yakin.glb','gltf-validation-yakin.json'],
  ['31-pelikan-goleti/model/su-kuslari-kubbesi-uzak.glb','gltf-validation-uzak.json'],
  ['30-turk-koyu/model/turk-koyu.glb','gltf-validation.json'],
  ['15-penguen/model/penguen-havuzu.glb','gltf-validation.json'],
  ['12-afrika-savana/model/savanna-ahsap-platform.glb','gltf-validation.json'],
  ['11-lemur/model/lemur-adasi.glb','gltf-validation.json'],
  ['14-afrika-koyu/model/afrika-koyu.glb','gltf-validation.json'],
  ['13-afrika-kafe/model/afrika-kafe.glb','gltf-validation.json'],
  ['_ortak/peyzaj/model/generic-broadleaf-tree.glb','gltf-validation.json'],
];
(async()=>{
  for(const [relative,reportName] of targets){
    const file=path.join(root,'bolgeler',relative),bytes=fs.readFileSync(file);
    const report=await validator.validateBytes(new Uint8Array(bytes),{uri:path.basename(file),maxIssues:5000});
    report.localEvidence={assetSha256:crypto.createHash('sha256').update(bytes).digest('hex'),
      validatorPackage:'gltf-validator@'+require('./_qa/gltf-check/node_modules/gltf-validator/package.json').version,
      specification:'https://github.com/KhronosGroup/glTF-Validator'};
    fs.writeFileSync(path.join(path.dirname(file),reportName),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify({asset:relative,errors:report.issues.numErrors,warnings:report.issues.numWarnings,infos:report.issues.numInfos,hints:report.issues.numHints}));
    if(report.issues.numErrors||report.issues.numWarnings)process.exitCode=1;
  }
})().catch(error=>{console.error(error.message);process.exitCode=1;});
