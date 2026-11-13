#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Aether theme..."

# Directories
mkdir -p "$HOME/.local/share/color-schemes" \
         "$HOME/.local/share/plasma/look-and-feel" \
         "$HOME/.local/share/plasma/desktoptheme" \
         "$HOME/.local/share/aurorae/themes" \
         "$HOME/.local/share/konsole" \
         "$HOME/.local/share/wallpapers" \
         "$HOME/.config/Kvantum" \
         "$HOME/.config/fontconfig" \
         "$HOME/.config/gtk-3.0" \
         "$HOME/.config/gtk-4.0" \
         "$HOME/.themes" \
         "$HOME/.config/zed/themes" \
         "$HOME/.config/btop/themes" \
         "$HOME/.config/bat"

# KDE Plasma 6
cp -rf "$DIR/plasma/color-schemes/Aether.colors" "$HOME/.local/share/color-schemes/"
rm -rf "$HOME/.local/share/plasma/look-and-feel/Aether"
cp -rf "$DIR/plasma/look-and-feel/Aether" "$HOME/.local/share/plasma/look-and-feel/"
rm -rf "$HOME/.local/share/plasma/desktoptheme/Aether"
cp -rf "$DIR/plasma/desktoptheme/Aether" "$HOME/.local/share/plasma/desktoptheme/"
rm -rf "$HOME/.local/share/aurorae/themes/Aether"
cp -rf "$DIR/plasma/aurorae/Aether" "$HOME/.local/share/aurorae/themes/"
rm -rf "$HOME/.local/share/wallpapers/Aether"
cp -rf "$DIR/plasma/wallpaper/Aether" "$HOME/.local/share/wallpapers/"
rm -rf "$HOME/.config/Kvantum/Aether"
cp -rf "$DIR/plasma/kvantum/Aether" "$HOME/.config/Kvantum/"

command -v plasma-apply-colorscheme >/dev/null 2>&1 && plasma-apply-colorscheme Aether >/dev/null 2>&1 || true
command -v plasma-apply-desktoptheme >/dev/null 2>&1 && plasma-apply-desktoptheme Aether >/dev/null 2>&1 || true

WALLPAPER="$HOME/.local/share/wallpapers/Aether/contents/images/3840x2160.png"
if [ -f "$WALLPAPER" ] && command -v plasma-apply-wallpaperimage >/dev/null 2>&1; then
    plasma-apply-wallpaperimage "$WALLPAPER" >/dev/null 2>&1 || true
fi

if command -v kwriteconfig6 >/dev/null 2>&1; then
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key ColorScheme "Aether"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key accentColorFromWallpaper "true"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group KDE --key LookAndFeelPackage "Aether"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group KDE --key widgetStyle "kvantum-dark"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group Icons --key Theme "Papirus-Dark"
    kwriteconfig6 --file "$HOME/.config/kcminputrc" --group Mouse --key cursorTheme "Bibata-Modern-Ice"
    kwriteconfig6 --file "$HOME/.config/ksplashrc" --group KSplash --key Engine "none"
    kwriteconfig6 --file "$HOME/.config/ksplashrc" --group KSplash --key Theme "None"

    # Font rendering
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key font "Google Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key menuFont "Google Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key toolBarFont "Google Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key smallestReadableFont "Google Sans,8,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key activeFont "Google Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group WM --key activeFont "Google Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key fixed "JetBrainsMono Nerd Font,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key XftAntialias "true"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key XftHintStyle "hintslight"
    kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key XftSubPixel "rgb"

    # Window decoration & Alt+Tab thumbnail grid
    kwriteconfig6 --file "$HOME/.config/kwinrc" --group org.kde.kdecoration2 --key library "org.kde.kwin.aurorae.v2"
    kwriteconfig6 --file "$HOME/.config/kwinrc" --group org.kde.kdecoration2 --key theme "__aurorae__svg__Aether"
    kwriteconfig6 --file "$HOME/.config/kwinrc" --group WindowSwitcher --key LayoutName "thumbnail_grid"
fi

[ -x "/usr/lib/plasma-apply-aurorae" ] && /usr/lib/plasma-apply-aurorae "__aurorae__svg__Aether" >/dev/null 2>&1 || true
command -v kvantummanager >/dev/null 2>&1 && kvantummanager --set Aether >/dev/null 2>&1 || true

# Konsole
cp -rf "$DIR/konsole/Aether.colorscheme" "$HOME/.local/share/konsole/"
for profile in "$HOME/.local/share/konsole/"*.profile; do
    if [ -f "$profile" ] && grep -q "\[Appearance\]" "$profile"; then
        sed -i 's/^ColorScheme=.*/ColorScheme=Aether/' "$profile"
        sed -i 's/^Font=.*/Font=JetBrainsMono Nerd Font,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0/' "$profile"
    fi
done

# GTK 3 & GTK 4 & Libadwaita
if [ -d "$DIR/gtk/Aether-Dark" ]; then
    rm -rf "$HOME/.themes/Aether-Dark"
    cp -rf "$DIR/gtk/Aether-Dark" "$HOME/.themes/"
    [ -d "/usr/share/themes/Breeze-Dark/assets" ] && ln -sfn "/usr/share/themes/Breeze-Dark/assets" "$HOME/.themes/Aether-Dark/assets"
    [ -d "/usr/share/themes/Breeze-Dark/gtk-2.0" ] && ln -sfn "/usr/share/themes/Breeze-Dark/gtk-2.0" "$HOME/.themes/Aether-Dark/gtk-2.0"
fi
command -v qdbus6 >/dev/null 2>&1 && qdbus6 org.kde.GtkConfig /GtkConfig setGtkTheme "Aether-Dark" >/dev/null 2>&1 || true
command -v gsettings >/dev/null 2>&1 && gsettings set org.gnome.desktop.interface gtk-theme "Aether-Dark" >/dev/null 2>&1 || true
for gtk_ini in "$HOME/.config/gtk-3.0/settings.ini" "$HOME/.config/gtk-4.0/settings.ini"; do
    if [ -f "$gtk_ini" ]; then
        sed -i 's/^gtk-font-name=.*/gtk-font-name=Google Sans, 10/' "$gtk_ini" 2>/dev/null || true
        sed -i 's/^gtk-theme-name=.*/gtk-theme-name=Aether-Dark/' "$gtk_ini" 2>/dev/null || true
    fi
done
cp -f "$DIR/gtk/gtk.css" "$HOME/.config/gtk-3.0/gtk.css"
cp -f "$DIR/gtk/gtk.css" "$HOME/.config/gtk-4.0/gtk.css"

# Fontconfig
cp -f "$DIR/fontconfig/fonts.conf" "$HOME/.config/fontconfig/fonts.conf"
if [ -w "/etc/fonts" ] && [ -f "$DIR/fontconfig/local.conf" ]; then
    cp -f "$DIR/fontconfig/local.conf" "/etc/fonts/local.conf"
    ln -sf /usr/share/fontconfig/conf.avail/10-sub-pixel-rgb.conf /etc/fonts/conf.d/10-sub-pixel-rgb.conf 2>/dev/null || true
fi
command -v fc-cache >/dev/null 2>&1 && fc-cache -f "$HOME/.local/share/fonts" "$HOME/.fonts" >/dev/null 2>&1 || true

# VS Code / Antigravity IDE / VSCodium / Cursor
AETHER_VSIX="$DIR/vscode/aether-dark-1.0.0.vsix"
if [ -f "$AETHER_VSIX" ]; then
    for ide_cli in antigravity-ide codium code cursor; do
        if command -v "$ide_cli" >/dev/null 2>&1; then
            "$ide_cli" --install-extension "$AETHER_VSIX" >/dev/null 2>&1 || true
        fi
    done
fi

AETHER_VSCODE="$DIR/vscode/aether-settings.json"
if command -v python3 >/dev/null 2>&1 && [ -f "$AETHER_VSCODE" ]; then
    for settings_file in \
        "$HOME/.config/Antigravity IDE/User/settings.json" \
        "$HOME/.config/VSCodium/User/settings.json" \
        "$HOME/.config/Code/User/settings.json" \
        "$HOME/.config/Cursor/User/settings.json"; do
        if [ -f "$settings_file" ]; then
            python3 - "$AETHER_VSCODE" "$settings_file" << 'PYEOF'
import json, re, sys

def strip_jsonc(text):
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                i += 1
                out.append(text[i])
            elif ch == '"':
                in_str = False
            i += 1
        elif ch == '"':
            in_str = True
            out.append(ch)
            i += 1
        elif text[i:i+2] == "//":
            i += 2
            while i < n and text[i] not in "\r\n":
                i += 1
        elif text[i:i+2] == "/*":
            i += 2
            while i + 1 < n and text[i:i+2] != "*/":
                i += 1
            i += 2
        else:
            out.append(ch)
            i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))

aether_path, target_path = sys.argv[1], sys.argv[2]
with open(aether_path, "r", encoding="utf-8") as f:
    aether = json.load(f)
try:
    with open(target_path, "r", encoding="utf-8") as f:
        current = json.loads(strip_jsonc(f.read()))
    if not isinstance(current, dict):
        current = {}
except Exception as exc:
    print(f"Skipping {target_path} (invalid JSONC): {exc}", file=sys.stderr)
    sys.exit(0)

current.pop("workbench.colorCustomizations", None)
current.update(aether)
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(current, f, indent=2)
    f.write("\n")
PYEOF
        fi
    done
fi

# Zed Editor
cp -f "$DIR/zed/aether.json" "$HOME/.config/zed/themes/"
ZED_SETTINGS="$HOME/.config/zed/settings.json"
if [ -f "$ZED_SETTINGS" ]; then
    sed -i 's/"dark": *"[^"]*"/"dark": "Aether Dark"/' "$ZED_SETTINGS"
    sed -i 's/"ui_font_family": *"[^"]*"/"ui_font_family": "Google Sans"/' "$ZED_SETTINGS"
    sed -i 's/"buffer_font_family": *"[^"]*"/"buffer_font_family": "JetBrainsMono Nerd Font"/' "$ZED_SETTINGS"
fi

# Terminal Tools
[ -f "$DIR/starship/starship.toml" ] && cp -f "$DIR/starship/starship.toml" "$HOME/.config/starship.toml"
[ -f "$DIR/btop/aether.theme" ] && cp -f "$DIR/btop/aether.theme" "$HOME/.config/btop/themes/"
[ -f "$HOME/.config/btop/btop.conf" ] && sed -i 's/^color_theme = .*/color_theme = "aether"/' "$HOME/.config/btop/btop.conf"
[ -f "$DIR/bat/config" ] && cp -f "$DIR/bat/config" "$HOME/.config/bat/config"

if command -v delta >/dev/null 2>&1; then
    git config --global core.pager "delta"
    git config --global interactive.diffFilter "delta --color-only"
    git config --global delta.navigate true
    git config --global delta.light false
    git config --global delta.line-numbers true
    git config --global delta.syntax-theme "Coldark-Dark"
    git config --global delta.minus-style 'syntax "#441822"'
    git config --global delta.plus-style 'syntax "#143a35"'
    git config --global delta.line-numbers-minus-style "#f13460"
    git config --global delta.line-numbers-plus-style "#269e9c"
    git config --global delta.file-style 'bold "#3c78ff"'
    git config --global delta.file-decoration-style "#3c78ff ul"
    git config --global delta.hunk-header-decoration-style "#10a6d4 box"
fi

FISH_CONFIG="$HOME/.config/fish/config.fish"
if [ -f "$FISH_CONFIG" ] && ! grep -q "FZF_DEFAULT_OPTS" "$FISH_CONFIG"; then
    cat << 'EOF' >> "$FISH_CONFIG"

# Bat alias
if type -q bat
    alias cat="bat --paging=never"
end

# FZF Aether Theme
if type -q fzf
    set -gx FZF_DEFAULT_OPTS " \
    --color=bg+:#16181d,bg:#111216,spinner:#3c78ff,hl:#10a6d4 \
    --color=fg:#abb2bf,header:#10a6d4,info:#3c78ff,pointer:#3c78ff \
    --color=marker:#269e9c,fg+:#ffffff,prompt:#3c78ff,hl+:#10a6d4 \
    --border=rounded --margin=1 --padding=1"
end
EOF
fi

echo "Done."
