# 先行研究のデータセットとコードを取ってくる
#
# 使い方（minireport3 のフォルダで）:
#   .\scripts\fetch_external.ps1             # 全部取ってくる
#   .\scripts\fetch_external.ps1 -SkipData   # AIDER（約276MB）を飛ばす
#
# 取ってくるもの（どれも GitHub には入れない。.gitignore の data/raw/ と external/）
#   data/raw/AIDER/          論文6 EmergencyNet の災害空撮データセット（Zenodo, CC BY 4.0）
#   external/EmergencyNet/   論文6 のコード（ライセンス記載なし）
#   external/ddnn/           論文2 DDNN のコード（ライセンス記載なし）
#   external/noscope/        論文1 NoScope のコード（ライセンス記載なし）
#   external/zhao-plastic-mulch/  論文4 Zhao らのコード（Zenodo, MIT）
#
# すでにあるものは取り直さない。取り直すときは、そのフォルダを消してから実行する。

param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [switch]$SkipData
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"   # 進み具合の表示を止めるとダウンロードが速くなる
$tar = Join-Path $env:SystemRoot "System32\tar.exe"   # Windows 付属の tar（zip と rar も展開できる）

# GitHub のコードは、動作を確かめたコミットに固定する
$repos = @(
    @{ Name = "EmergencyNet"; Repo = "ckyrkou/EmergencyNet";       Commit = "b9f65ab4d22df3b4098c6e941a70827fd4dc7038" },
    @{ Name = "ddnn";         Repo = "kunglab/ddnn";               Commit = "adbe5c20f2f6b2c3d875af8b651cce22138928ff" },
    @{ Name = "noscope";      Repo = "stanford-futuredata/noscope"; Commit = "6c6aa72e09280530dfdcf87871c1ac43df3b6cc3" }
)

function Expand-Archive2($archive, $dest, [string[]]$exclude = @()) {
    New-Item -ItemType Directory -Force $dest | Out-Null
    $targs = @("-xf", $archive, "-C", $dest)
    foreach ($e in $exclude) { $targs += @("--exclude", $e) }
    & $tar @targs
    if ($LASTEXITCODE -ne 0) { throw "展開に失敗しました: $archive" }
}

$ext = Join-Path $Root "external"
New-Item -ItemType Directory -Force $ext | Out-Null
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("minireport3_fetch_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force $tmp | Out-Null

try {
    # 1. AIDER
    $aider = Join-Path $Root "data\raw\AIDER"
    if ($SkipData) {
        Write-Host "AIDER: -SkipData なので飛ばします"
    } elseif (Test-Path $aider) {
        Write-Host "AIDER: すでにあります ($aider)"
    } else {
        Write-Host "AIDER: Zenodo からダウンロードします（約276MB、数分かかります）"
        $zip = Join-Path $tmp "AIDER.zip"
        Invoke-WebRequest "https://zenodo.org/records/3888300/files/AIDER.zip?download=1" -OutFile $zip
        Expand-Archive2 $zip (Join-Path $Root "data\raw")
    }

    # 2. GitHub のコード（git clone ではなく zip で取る。EmergencyNet には Windows で作れない名前のファイル data/... があるため）
    foreach ($r in $repos) {
        $dest = Join-Path $ext $r.Name
        if (Test-Path $dest) { Write-Host "$($r.Name): すでにあります"; continue }
        Write-Host "$($r.Name): $($r.Repo) @ $($r.Commit.Substring(0, 7)) を取ってきます"
        $zip = Join-Path $tmp "$($r.Name).zip"
        Invoke-WebRequest "https://codeload.github.com/$($r.Repo)/zip/$($r.Commit)" -OutFile $zip
        Expand-Archive2 $zip $tmp @("*/data/...")
        $top = Get-ChildItem $tmp -Directory | Where-Object { $_.Name -like "$($r.Repo.Split('/')[1])-*" } | Select-Object -First 1
        Move-Item $top.FullName $dest
    }

    # 3. Zhao らのコード（Zenodo の rar）
    $zhao = Join-Path $ext "zhao-plastic-mulch"
    if (Test-Path $zhao) {
        Write-Host "zhao-plastic-mulch: すでにあります"
    } else {
        Write-Host "zhao-plastic-mulch: Zenodo から取ってきます"
        $rar = Join-Path $tmp "plastic-mulch-edge-cloud.rar"
        Invoke-WebRequest "https://zenodo.org/records/21635293/files/plastic-mulch-edge-cloud.rar?download=1" -OutFile $rar
        Expand-Archive2 $rar $zhao
    }
} finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}

# 確認
if (Test-Path (Join-Path $Root "data\raw\AIDER")) {
    Get-ChildItem (Join-Path $Root "data\raw\AIDER") -Directory |
        ForEach-Object { "AIDER/{0}: {1} 枚" -f $_.Name, (Get-ChildItem $_.FullName -File).Count }
}
Get-ChildItem $ext -Directory | ForEach-Object { "external/{0}" -f $_.Name }
Write-Host "完了しました"
