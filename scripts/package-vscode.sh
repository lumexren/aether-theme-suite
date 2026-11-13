#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXT_DIR="$ROOT/vscode/aether-dark-extension"

read -r PKG_NAME PKG_VERSION < <(
    python3 -c 'import json, sys; d=json.load(open(sys.argv[1])); print(d["name"], d["version"])' \
        "$EXT_DIR/package.json"
)
OUT_VSIX="$ROOT/vscode/${PKG_NAME}-${PKG_VERSION}.vsix"

if command -v vsce >/dev/null 2>&1; then
    (cd "$EXT_DIR" && vsce package --out "$OUT_VSIX")
    echo "Packaged via vsce: $OUT_VSIX"
    exit 0
fi

python3 - "$EXT_DIR" "$OUT_VSIX" << 'PYEOF'
import json
import sys
import xml.sax.saxutils as sax
import zipfile
from pathlib import Path

ext_dir = Path(sys.argv[1])
out_vsix = Path(sys.argv[2])
pkg = json.loads((ext_dir / "package.json").read_text(encoding="utf-8"))

content_types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".md" ContentType="text/markdown"/>
  <Default Extension=".png" ContentType="image/png"/>
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
</Types>
"""

esc = sax.escape
keywords = ",".join(pkg.get("keywords", []))
manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="{esc(pkg['name'])}" Version="{esc(pkg['version'])}" Publisher="{esc(pkg['publisher'])}"/>
    <DisplayName>{esc(pkg['displayName'])}</DisplayName>
    <Description xml:space="preserve">{esc(pkg['description'])}</Description>
    <Categories>{esc(','.join(pkg.get('categories', [])))}</Categories>
    <Tags>{esc(keywords)}</Tags>
    <Icon>extension/{esc(pkg['icon'])}</Icon>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
    <Asset Type="Microsoft.VisualStudio.Services.Icons.Default" Path="extension/{esc(pkg['icon'])}" Addressable="true"/>
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"/>
  </Assets>
</PackageManifest>
"""

files = [
    ("package.json", ext_dir / "package.json"),
    ("README.md", ext_dir / "README.md"),
    ("icon.png", ext_dir / "icon.png"),
    ("themes/aether-dark-color-theme.json", ext_dir / "themes" / "aether-dark-color-theme.json"),
]

with zipfile.ZipFile(out_vsix, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("[Content_Types].xml", content_types)
    zf.writestr("extension.vsixmanifest", manifest)
    for rel, src in files:
        zf.write(src, f"extension/{rel}")

print(f"Packaged deterministically: {out_vsix}")
PYEOF
