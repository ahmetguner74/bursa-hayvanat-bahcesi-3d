param([switch]$UseCyclesFallback, [string]$WebGlAtlas)
$ErrorActionPreference = 'Stop'
$treeModelRoot = $PSScriptRoot
$treeRepositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $treeModelRoot '..\..\..\..'))
$treeBlenderExecutable = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$treePythonExecutable = 'C:\Program Files\Python312\python.exe'
$treeNodeExecutable = 'C:\Program Files\nodejs\node.exe'
$treeOriginalSource = Join-Path $treeRepositoryRoot 'bolgeler\_qa\tree-assets\jacaranda-source\jacaranda_tree_1k.blend'
if (-not (Test-Path -LiteralPath $treeOriginalSource)) { throw 'Verified Poly Haven source is missing. See source-manifest.json.' }
if ((Get-FileHash -LiteralPath $treeOriginalSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'e28e9ea0deb782a830420126b3c5536bde44d1b532cbfb4dccbcc0e46119a0ce') { throw 'Tree source checksum mismatch.' }
Push-Location -LiteralPath $treeRepositoryRoot
try {
    & $treePythonExecutable (Join-Path $treeModelRoot 'prepare_tree_textures.py')
    if ($LASTEXITCODE) { throw 'Texture preparation failed.' }
    & $treeBlenderExecutable --background --factory-startup --disable-autoexec $treeOriginalSource --python-exit-code 1 --python (Join-Path $treeModelRoot 'build_forest_tree.py')
    if ($LASTEXITCODE) { throw 'Tree mesh build failed.' }
    if ($UseCyclesFallback) {
        & $treeBlenderExecutable --background --factory-startup --disable-autoexec (Join-Path $treeModelRoot 'generic-broadleaf-tree.blend') --python-exit-code 1 --python (Join-Path $treeModelRoot 'bake_tree_impostors.py') -- 16
        if ($LASTEXITCODE) { throw 'Tree frame rendering failed.' }
        & $treePythonExecutable (Join-Path $treeModelRoot 'pack_tree_impostors.py')
        if ($LASTEXITCODE) { throw 'Tree atlas packing failed.' }
    } else {
        if (-not $WebGlAtlas) { $WebGlAtlas = Join-Path $treeModelRoot 'browser-atlas-source.png' }
        & $treePythonExecutable (Join-Path $treeModelRoot 'import_tree_webgl_atlas.py') $WebGlAtlas
        if ($LASTEXITCODE) { throw 'Render the new GLB at http://127.0.0.1:8768/model-review/?model=forest&bake=1 and import its PNG. The renderer must have the newly built GLB and build-report.json.' }
    }
    & $treePythonExecutable (Join-Path $treeModelRoot 'verify_tree_assets.py')
    if ($LASTEXITCODE) { throw 'Tree asset verification failed.' }
    & $treeNodeExecutable 'bolgeler/validate_models.cjs'
    if ($LASTEXITCODE) { throw 'glTF validation failed.' }
    & $treePythonExecutable 'publish_local.py' --local-only
    if ($LASTEXITCODE) { throw 'Local viewer build failed.' }
} finally { Pop-Location }
