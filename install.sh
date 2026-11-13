#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/aether-theme-suite"
BACKUP_ROOT="$STATE_DIR/backups"
BACKUP_DIR=""

ALL_COMPONENTS=(
    plasma sddm konsole ghostty kitty alacritty wezterm
    gtk fonts vscode zed neovim kate jetbrains
    obsidian discord firefox
    waybar rofi fuzzel dunst mako
    starship btop bat delta fastfetch eza lazygit yazi tmux zathura cava shell
)
ONLY_LIST=""
SKIP_LIST=""
DRY_RUN=false
UNINSTALL=false
WITH_SHELL_ALIASES=false

usage() {
    cat << 'EOF'
Usage: ./install.sh [OPTIONS]

Options:
  --only <list>          Comma-separated components or groups to install
                         Components: plasma,sddm,konsole,ghostty,kitty,alacritty,wezterm,
                                     gtk,fonts,vscode,zed,neovim,kate,jetbrains,
                                     obsidian,discord,firefox,
                                     waybar,rofi,fuzzel,dunst,mako,
                                     starship,btop,bat,delta,fastfetch,eza,lazygit,yazi,tmux,zathura,cava,shell
                         Groups:     terminals,editors,apps,wayland,cli
  --skip <list>          Comma-separated components or groups to skip
  --with-shell-aliases   Also add `alias cat="bat --paging=never"` to shell config
  --dry-run              Show what would be done without modifying any files
  --uninstall            Remove installed Aether theme files and restore latest backups
  -h, --help             Show this help message
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --only)
            [ $# -ge 2 ] || { echo "Error: --only requires an argument" >&2; exit 1; }
            ONLY_LIST="$2"
            shift 2
            ;;
        --skip)
            [ $# -ge 2 ] || { echo "Error: --skip requires an argument" >&2; exit 1; }
            SKIP_LIST="$2"
            shift 2
            ;;
        --with-shell-aliases)
            WITH_SHELL_ALIASES=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if [ "${EUID:-$(id -u)}" -eq 0 ] && [ "${AETHER_ALLOW_ROOT:-0}" != "1" ] && [ "$ONLY_LIST" != "sddm" ]; then
    echo "Error: Do not run install.sh as root/sudo; it configures \$HOME." >&2
    echo "Run as your regular user (or run 'sudo ./install.sh --only sddm' / set AETHER_ALLOW_ROOT=1)." >&2
    exit 1
fi

log() {
    if $DRY_RUN; then
        echo "[dry-run] $*"
    else
        echo "$*"
    fi
}

run_cmd() {
    if $DRY_RUN; then
        echo "[dry-run] $*"
    else
        "$@"
    fi
}

try_cmd() {
    local bin="$1"
    shift
    if command -v "$bin" >/dev/null 2>&1; then
        "$bin" "$@" >/dev/null 2>&1 || true
    fi
}

should_run() {
    local comp="$1"
    if [ -n "$ONLY_LIST" ]; then
        case ",$ONLY_LIST," in
            *,"$comp",*) ;;
            *) return 1 ;;
        esac
    fi
    if [ -n "$SKIP_LIST" ]; then
        case ",$SKIP_LIST," in
            *,"$comp",*) return 1 ;;
        esac
    fi
    return 0
}

expand_component_list() {
    local raw="$1"
    [ -z "$raw" ] && return 0
    local out=()
    local items=()
    IFS=',' read -ra items <<< "$raw"
    for item in "${items[@]}"; do
        case "$item" in
            terminals) out+=(konsole ghostty kitty alacritty wezterm) ;;
            editors)   out+=(vscode zed neovim kate jetbrains) ;;
            apps)      out+=(obsidian discord firefox) ;;
            wayland)   out+=(waybar rofi fuzzel dunst mako) ;;
            cli)       out+=(starship btop bat delta fastfetch eza lazygit yazi tmux zathura cava) ;;
            *)
                local valid=false
                for c in "${ALL_COMPONENTS[@]}"; do
                    if [ "$item" = "$c" ]; then
                        valid=true
                        break
                    fi
                done
                if ! $valid; then
                    echo "Error: Unknown component '$item'. Valid: ${ALL_COMPONENTS[*]} (groups: terminals, editors, apps, wayland, cli)" >&2
                    exit 1
                fi
                out+=("$item")
                ;;
        esac
    done
    local IFS=','
    printf '%s\n' "${out[*]}"
}

ONLY_LIST="$(expand_component_list "$ONLY_LIST")"
SKIP_LIST="$(expand_component_list "$SKIP_LIST")"

backup_file() {
    local target="$1"
    [ -e "$target" ] || [ -L "$target" ] || return 0
    if $DRY_RUN; then
        echo "[dry-run] backup $target"
        return 0
    fi
    if [ -z "$BACKUP_DIR" ]; then
        local ts
        ts="$(date +%Y%m%d-%H%M%S)"
        BACKUP_DIR="$BACKUP_ROOT/$ts"
        mkdir -p "$BACKUP_DIR"
        ln -sfn "$BACKUP_DIR" "$BACKUP_ROOT/latest"
    fi
    local rel="${target#"$HOME"/}"
    if [ "$rel" = "$target" ]; then
        rel="_abs${target}"
    fi
    local dest="$BACKUP_DIR/$rel"
    mkdir -p "$(dirname "$dest")"
    cp -a "$target" "$dest"
}

remove_aether_shell_block() {
    local file="$1"
    [ -f "$file" ] || return 0
    if $DRY_RUN; then
        echo "[dry-run] remove Aether block from $file"
        return 0
    fi
    python3 - "$file" << 'PYEOF'
import re, sys
from pathlib import Path

p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
new_text = re.sub(
    r"\n?# >>> Aether Theme >>>.*?# <<< Aether Theme <<<\n?",
    "\n",
    text,
    flags=re.DOTALL,
)
if new_text != text:
    p.write_text(new_text.rstrip() + "\n", encoding="utf-8")
PYEOF
}

upsert_aether_shell_block() {
    local file="$1"
    local block="$2"
    [ -f "$file" ] || return 0
    backup_file "$file"
    if $DRY_RUN; then
        echo "[dry-run] update Aether block in $file"
        return 0
    fi
    python3 - "$file" "$block" << 'PYEOF'
import re, sys
from pathlib import Path

p = Path(sys.argv[1])
block = sys.argv[2].strip("\n")
text = p.read_text(encoding="utf-8")
pattern = re.compile(r"# >>> Aether Theme >>>.*?# <<< Aether Theme <<<", re.DOTALL)
if pattern.search(text):
    new_text = pattern.sub(block, text)
else:
    sep = "\n\n" if text and not text.endswith("\n\n") else ("\n" if text and not text.endswith("\n") else "")
    new_text = text + sep + block + "\n"
p.write_text(new_text, encoding="utf-8")
PYEOF
}

uninstall_aether() {
    log "Uninstalling Aether theme..."
    local targets=(
        "$HOME/.local/share/color-schemes/Aether.colors"
        "$HOME/.local/share/plasma/look-and-feel/Aether"
        "$HOME/.local/share/plasma/desktoptheme/Aether"
        "$HOME/.local/share/aurorae/themes/Aether"
        "$HOME/.local/share/wallpapers/Aether"
        "$HOME/.config/Kvantum/Aether"
        "$HOME/.local/share/konsole/Aether.colorscheme"
        "$HOME/.local/share/konsole/Aether.profile"
        "$HOME/.config/ghostty/themes/aether-dark"
        "$HOME/.config/kitty/themes/aether-dark.conf"
        "$HOME/.config/kitty/aether-dark.conf"
        "$HOME/.config/alacritty/themes/aether-dark.toml"
        "$HOME/.config/wezterm/colors/aether-dark.toml"
        "$HOME/.themes/Aether-Dark"
        "$HOME/.config/zed/themes/aether.json"
        "$HOME/.config/nvim/colors/aether.lua"
        "$HOME/.config/nvim/lua/aether"
        "$HOME/.config/nvim/lua/lualine/themes/aether.lua"
        "$HOME/.local/share/org.kde.syntax-highlighting/themes/Aether Dark.theme"
        "$HOME/.config/btop/themes/aether.theme"
        "$HOME/.config/bat/themes/Aether Dark.tmTheme"
        "$HOME/.config/fastfetch/aether.jsonc"
        "$HOME/.config/eza/theme.yml"
        "$HOME/.config/lazygit/aether-dark.yml"
        "$HOME/.config/yazi/theme.toml"
        "$HOME/.config/tmux/aether.conf"
        "$HOME/.config/zathura/aether-dark"
        "$HOME/.config/cava/themes/aether"
        "$HOME/.config/waybar/aether.css"
        "$HOME/.config/rofi/themes/aether.rasi"
        "$HOME/.config/fuzzel/aether.ini"
        "$HOME/.config/dunst/dunstrc.d/99-aether.conf"
        "$HOME/.config/mako/aether.conf"
        "$HOME/.config/vesktop/themes/aether-dark.theme.css"
        "$HOME/.config/Vencord/themes/aether-dark.theme.css"
        "$HOME/.config/BetterDiscord/themes/aether-dark.theme.css"
        "$HOME/.local/share/aether-theme-suite"
        "$HOME/.config/fontconfig/conf.d/99-aether.conf"
    )
    for t in "${targets[@]}"; do
        if [ -e "$t" ] || [ -L "$t" ]; then
            run_cmd rm -rf "$t"
        fi
    done

    remove_aether_shell_block "$HOME/.config/fish/config.fish"
    remove_aether_shell_block "$HOME/.zshrc"
    remove_aether_shell_block "$HOME/.bashrc"
    remove_aether_shell_block "$HOME/.config/tmux/tmux.conf"
    remove_aether_shell_block "$HOME/.tmux.conf"
    remove_aether_shell_block "$HOME/.config/kitty/kitty.conf"
    remove_aether_shell_block "$HOME/.config/zathura/zathurarc"

    if [ -L "$BACKUP_ROOT/latest" ] && [ -d "$BACKUP_ROOT/latest" ]; then
        local latest
        latest="$(readlink -f "$BACKUP_ROOT/latest")"
        log "Restoring backed up configs from $latest..."
        if ! $DRY_RUN; then
            while IFS= read -r -d '' src; do
                local rel="${src#"$latest"/}"
                local dest="$HOME/$rel"
                mkdir -p "$(dirname "$dest")"
                cp -a "$src" "$dest"
            done < <(find "$latest" \( -type f -o -type l \) -print0)
        fi
    fi

    if command -v bat >/dev/null 2>&1; then
        run_cmd bat cache --build >/dev/null 2>&1 || true
    fi
    log "Uninstall complete."
}

if $UNINSTALL; then
    uninstall_aether
    exit 0
fi

log "Installing Aether theme..."

# 1. KDE Plasma 6
if should_run "plasma"; then
    log "Applying KDE Plasma 6 theme..."
    run_cmd mkdir -p "$HOME/.local/share/color-schemes" \
                     "$HOME/.local/share/plasma/look-and-feel" \
                     "$HOME/.local/share/plasma/desktoptheme" \
                     "$HOME/.local/share/aurorae/themes" \
                     "$HOME/.local/share/wallpapers" \
                     "$HOME/.config/Kvantum"

    run_cmd cp -rf "$DIR/plasma/color-schemes/Aether.colors" "$HOME/.local/share/color-schemes/"
    run_cmd rm -rf "$HOME/.local/share/plasma/look-and-feel/Aether"
    run_cmd cp -rf "$DIR/plasma/look-and-feel/Aether" "$HOME/.local/share/plasma/look-and-feel/"
    run_cmd rm -rf "$HOME/.local/share/plasma/desktoptheme/Aether"
    run_cmd cp -rf "$DIR/plasma/desktoptheme/Aether" "$HOME/.local/share/plasma/desktoptheme/"
    run_cmd rm -rf "$HOME/.local/share/aurorae/themes/Aether"
    run_cmd cp -rf "$DIR/plasma/aurorae/Aether" "$HOME/.local/share/aurorae/themes/"
    run_cmd rm -rf "$HOME/.local/share/wallpapers/Aether"
    run_cmd cp -rf "$DIR/plasma/wallpaper/Aether" "$HOME/.local/share/wallpapers/"
    run_cmd rm -rf "$HOME/.config/Kvantum/Aether"
    run_cmd cp -rf "$DIR/plasma/kvantum/Aether" "$HOME/.config/Kvantum/"

    if ! $DRY_RUN; then
        try_cmd plasma-apply-colorscheme Aether
        try_cmd plasma-apply-desktoptheme Aether

        WALLPAPER="$HOME/.local/share/wallpapers/Aether/contents/images/3840x2160.png"
        if [ -f "$WALLPAPER" ] && command -v plasma-apply-wallpaperimage >/dev/null 2>&1; then
            plasma-apply-wallpaperimage "$WALLPAPER" >/dev/null 2>&1 || true
        fi

        if command -v kwriteconfig6 >/dev/null 2>&1; then
            kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key ColorScheme "Aether"
            kwriteconfig6 --file "$HOME/.config/kdeglobals" --group General --key accentColorFromWallpaper "false"
            kwriteconfig6 --file "$HOME/.config/kdeglobals" --group KDE --key LookAndFeelPackage "Aether"
            kwriteconfig6 --file "$HOME/.config/kdeglobals" --group KDE --key widgetStyle "kvantum-dark"
            kwriteconfig6 --file "$HOME/.config/kdeglobals" --group Icons --key Theme "Papirus-Dark"
            kwriteconfig6 --file "$HOME/.config/kcminputrc" --group Mouse --key cursorTheme "Bibata-Modern-Ice"
            kwriteconfig6 --file "$HOME/.config/ksplashrc" --group KSplash --key Engine "KSplashQML"
            kwriteconfig6 --file "$HOME/.config/ksplashrc" --group KSplash --key Theme "Aether"

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

        if [ -x "/usr/lib/plasma-apply-aurorae" ]; then
            /usr/lib/plasma-apply-aurorae "__aurorae__svg__Aether" >/dev/null 2>&1 || true
        fi
        try_cmd kvantummanager --set Aether
    fi
fi

# 1b. SDDM Login Theme
if should_run "sddm" && [ -d "$DIR/plasma/sddm/Aether" ]; then
    SDDM_DEST="/usr/share/sddm/themes/Aether"
    if [ -w "/usr/share/sddm/themes" ] || { [ ! -e "/usr/share/sddm/themes" ] && [ -w "/usr/share/sddm" ]; } || $DRY_RUN; then
        log "Applying SDDM Login Theme..."
        run_cmd mkdir -p "$SDDM_DEST"
        run_cmd cp -rf "$DIR/plasma/sddm/Aether/"* "$SDDM_DEST/"
        if [ -f "$DIR/plasma/wallpaper/Aether/contents/images/3840x2160.png" ]; then
            run_cmd cp -f "$DIR/plasma/wallpaper/Aether/contents/images/3840x2160.png" "$SDDM_DEST/background.png"
        fi
    else
        log "Skipping SDDM theme ($SDDM_DEST requires root; run: sudo ./install.sh --only sddm)"
    fi
fi

# 2. Konsole
if should_run "konsole"; then
    log "Applying Konsole color scheme..."
    run_cmd mkdir -p "$HOME/.local/share/konsole"
    run_cmd cp -rf "$DIR/konsole/Aether.colorscheme" "$HOME/.local/share/konsole/"

    shopt -s nullglob
    konsole_profiles=("$HOME/.local/share/konsole/"*.profile)
    shopt -u nullglob

    if [ ${#konsole_profiles[@]} -eq 0 ]; then
        if ! $DRY_RUN; then
            cat << 'EOF' > "$HOME/.local/share/konsole/Aether.profile"
[Appearance]
ColorScheme=Aether
Font=JetBrainsMono Nerd Font,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0

[General]
Name=Aether
Parent=FALLBACK/
EOF
            try_cmd kwriteconfig6 --file "$HOME/.config/konsolerc" --group "Desktop Entry" --key DefaultProfile "Aether.profile"
        else
            log "create $HOME/.local/share/konsole/Aether.profile"
        fi
    else
        for profile in "${konsole_profiles[@]}"; do
            backup_file "$profile"
            if ! $DRY_RUN; then
                python3 - "$profile" << 'PYEOF'
import configparser, sys
from pathlib import Path

p = Path(sys.argv[1])
cp = configparser.ConfigParser(interpolation=None)
cp.optionxform = str
cp.read(p, encoding="utf-8")
if not cp.has_section("Appearance"):
    cp.add_section("Appearance")
cp.set("Appearance", "ColorScheme", "Aether")
cp.set("Appearance", "Font", "JetBrainsMono Nerd Font,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0")
with p.open("w", encoding="utf-8") as f:
    cp.write(f, space_around_delimiters=False)
PYEOF
            fi
        done
    fi
fi

# 2b. Ghostty
if should_run "ghostty" && [ -f "$DIR/terminals/ghostty/aether-dark" ]; then
    log "Applying Ghostty theme..."
    run_cmd mkdir -p "$HOME/.config/ghostty/themes"
    run_cmd cp -f "$DIR/terminals/ghostty/aether-dark" "$HOME/.config/ghostty/themes/aether-dark"
    if [ -f "$HOME/.config/ghostty/config" ]; then
        backup_file "$HOME/.config/ghostty/config"
        if ! $DRY_RUN; then
            if grep -q '^theme[[:space:]]*=' "$HOME/.config/ghostty/config"; then
                sed -i 's/^theme[[:space:]]*=.*/theme = aether-dark/' "$HOME/.config/ghostty/config"
            else
                printf '\ntheme = aether-dark\n' >> "$HOME/.config/ghostty/config"
            fi
        fi
    fi
fi

# 2c. Kitty
if should_run "kitty" && [ -f "$DIR/terminals/kitty/aether-dark.conf" ]; then
    log "Applying Kitty theme..."
    run_cmd mkdir -p "$HOME/.config/kitty/themes"
    run_cmd cp -f "$DIR/terminals/kitty/aether-dark.conf" "$HOME/.config/kitty/themes/aether-dark.conf"
    run_cmd cp -f "$DIR/terminals/kitty/aether-dark.conf" "$HOME/.config/kitty/aether-dark.conf"
    if [ -f "$HOME/.config/kitty/kitty.conf" ]; then
        upsert_aether_shell_block "$HOME/.config/kitty/kitty.conf" "# >>> Aether Theme >>>
include aether-dark.conf
# <<< Aether Theme <<<"
    fi
fi

# 2d. Alacritty
if should_run "alacritty" && [ -f "$DIR/terminals/alacritty/aether-dark.toml" ]; then
    log "Applying Alacritty theme..."
    run_cmd mkdir -p "$HOME/.config/alacritty/themes"
    run_cmd cp -f "$DIR/terminals/alacritty/aether-dark.toml" "$HOME/.config/alacritty/themes/aether-dark.toml"
fi

# 2e. WezTerm
if should_run "wezterm" && [ -f "$DIR/terminals/wezterm/aether-dark.toml" ]; then
    log "Applying WezTerm color scheme..."
    run_cmd mkdir -p "$HOME/.config/wezterm/colors"
    run_cmd cp -f "$DIR/terminals/wezterm/aether-dark.toml" "$HOME/.config/wezterm/colors/aether-dark.toml"
fi

# 3. GTK 3 & GTK 4 & Libadwaita
if should_run "gtk"; then
    log "Applying GTK 3/4 & Libadwaita theme..."
    run_cmd mkdir -p "$HOME/.config/gtk-3.0" "$HOME/.config/gtk-4.0" "$HOME/.themes"

    if [ ! -d "/usr/share/themes/Breeze-Dark" ]; then
        echo "Warning: /usr/share/themes/Breeze-Dark not found; Aether-Dark GTK inherits Breeze-Dark assets and base CSS." >&2
    fi

    if [ -d "$DIR/gtk/Aether-Dark" ]; then
        run_cmd rm -rf "$HOME/.themes/Aether-Dark"
        run_cmd cp -rf "$DIR/gtk/Aether-Dark" "$HOME/.themes/"
        if ! $DRY_RUN; then
            [ -d "/usr/share/themes/Breeze-Dark/assets" ] && ln -sfn "/usr/share/themes/Breeze-Dark/assets" "$HOME/.themes/Aether-Dark/assets"
            [ -d "/usr/share/themes/Breeze-Dark/gtk-2.0" ] && ln -sfn "/usr/share/themes/Breeze-Dark/gtk-2.0" "$HOME/.themes/Aether-Dark/gtk-2.0"
        fi
    fi

    if ! $DRY_RUN; then
        try_cmd qdbus6 org.kde.GtkConfig /GtkConfig setGtkTheme "Aether-Dark"
        try_cmd gsettings set org.gnome.desktop.interface gtk-theme "Aether-Dark"
    fi

    for gtk_ini in "$HOME/.config/gtk-3.0/settings.ini" "$HOME/.config/gtk-4.0/settings.ini"; do
        backup_file "$gtk_ini"
        if ! $DRY_RUN; then
            python3 - "$gtk_ini" << 'PYEOF'
import configparser, sys
from pathlib import Path

p = Path(sys.argv[1])
cp = configparser.ConfigParser(interpolation=None)
cp.optionxform = str
if p.is_file():
    cp.read(p, encoding="utf-8")
if not cp.has_section("Settings"):
    cp.add_section("Settings")
cp.set("Settings", "gtk-theme-name", "Aether-Dark")
cp.set("Settings", "gtk-font-name", "Google Sans, 10")
cp.set("Settings", "gtk-application-prefer-dark-theme", "1")
with p.open("w", encoding="utf-8") as f:
    cp.write(f, space_around_delimiters=False)
PYEOF
        fi
    done

    backup_file "$HOME/.config/gtk-3.0/gtk.css"
    backup_file "$HOME/.config/gtk-4.0/gtk.css"
    run_cmd cp -f "$DIR/gtk/gtk.css" "$HOME/.config/gtk-3.0/gtk.css"
    run_cmd cp -f "$DIR/gtk/gtk.css" "$HOME/.config/gtk-4.0/gtk.css"
fi

# 4. Fontconfig
if should_run "fonts"; then
    log "Applying Fontconfig rendering settings..."
    run_cmd mkdir -p "$HOME/.config/fontconfig/conf.d"
    backup_file "$HOME/.config/fontconfig/fonts.conf"
    run_cmd cp -f "$DIR/fontconfig/fonts.conf" "$HOME/.config/fontconfig/fonts.conf"
    if [ -f "$DIR/fontconfig/local.conf" ]; then
        backup_file "$HOME/.config/fontconfig/conf.d/99-aether.conf"
        run_cmd cp -f "$DIR/fontconfig/local.conf" "$HOME/.config/fontconfig/conf.d/99-aether.conf"
        if [ -w "/etc/fonts" ] && ! $DRY_RUN; then
            cp -f "$DIR/fontconfig/local.conf" "/etc/fonts/local.conf"
            ln -sf /usr/share/fontconfig/conf.avail/10-sub-pixel-rgb.conf /etc/fonts/conf.d/10-sub-pixel-rgb.conf 2>/dev/null || true
        fi
    fi
    if ! $DRY_RUN; then
        try_cmd fc-cache -f "$HOME/.local/share/fonts" "$HOME/.fonts"
    fi
fi

# Shared Python JSONC helper for VS Code & Zed
merge_jsonc() {
    local target="$1"
    local mode="$2"
    local src="$3"
    backup_file "$target"
    if $DRY_RUN; then
        echo "[dry-run] merge $mode settings into $target"
        return 0
    fi
    mkdir -p "$(dirname "$target")"
    python3 - "$src" "$target" "$mode" << 'PYEOF'
import json, re, sys
from pathlib import Path

def strip_jsonc(text: str) -> str:
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

src_path, target_path, mode = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]

current = {}
if target_path.is_file():
    try:
        parsed = json.loads(strip_jsonc(target_path.read_text(encoding="utf-8")))
        if isinstance(parsed, dict):
            current = parsed
    except Exception as exc:
        print(f"Skipping {target_path} (invalid JSONC): {exc}", file=sys.stderr)
        sys.exit(0)

if mode == "vscode":
    aether = json.loads(src_path.read_text(encoding="utf-8"))
    current.pop("workbench.colorCustomizations", None)
    current.update(aether)
elif mode == "zed":
    theme = current.get("theme")
    if not isinstance(theme, dict):
        theme = {"mode": "dark", "light": "One Light"}
    theme["mode"] = "dark"
    theme["dark"] = "Aether Dark"
    current["theme"] = theme
    current["ui_font_family"] = "Google Sans"
    current["buffer_font_family"] = "JetBrainsMono Nerd Font"

target_path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
PYEOF
}

# 5. VS Code / Antigravity IDE / VSCodium / Cursor
if should_run "vscode"; then
    log "Applying VS Code family theme & settings..."
    AETHER_VSIX="$DIR/vscode/aether-dark-1.0.0.vsix"
    if [ -f "$AETHER_VSIX" ]; then
        for ide_cli in antigravity antigravity-ide codium code cursor; do
            if command -v "$ide_cli" >/dev/null 2>&1; then
                run_cmd "$ide_cli" --install-extension "$AETHER_VSIX" >/dev/null 2>&1 || true
            fi
        done
    fi

    AETHER_VSCODE="$DIR/vscode/aether-settings.json"
    if [ -f "$AETHER_VSCODE" ]; then
        for settings_file in \
            "$HOME/.config/Antigravity IDE/User/settings.json" \
            "$HOME/.config/Antigravity/User/settings.json" \
            "$HOME/.config/VSCodium/User/settings.json" \
            "$HOME/.config/Code/User/settings.json" \
            "$HOME/.config/Cursor/User/settings.json"; do
            if [ -d "$(dirname "$settings_file")" ]; then
                merge_jsonc "$settings_file" "vscode" "$AETHER_VSCODE"
            fi
        done
    fi
fi

# 6. Zed Editor
if should_run "zed"; then
    log "Applying Zed theme..."
    run_cmd mkdir -p "$HOME/.config/zed/themes"
    run_cmd cp -f "$DIR/zed/aether.json" "$HOME/.config/zed/themes/"
    if [ -d "$HOME/.config/zed" ] || command -v zed >/dev/null 2>&1 || command -v zeditor >/dev/null 2>&1; then
        merge_jsonc "$HOME/.config/zed/settings.json" "zed" "$DIR/zed/aether.json"
    fi
fi

# 6b. Neovim
if should_run "neovim" && [ -f "$DIR/neovim/colors/aether.lua" ]; then
    log "Applying Neovim colorscheme..."
    run_cmd mkdir -p "$HOME/.config/nvim/colors" \
                     "$HOME/.config/nvim/lua/aether" \
                     "$HOME/.config/nvim/lua/lualine/themes"
    backup_file "$HOME/.config/nvim/colors/aether.lua"
    backup_file "$HOME/.config/nvim/lua/aether/init.lua"
    backup_file "$HOME/.config/nvim/lua/lualine/themes/aether.lua"
    run_cmd cp -f "$DIR/neovim/colors/aether.lua" "$HOME/.config/nvim/colors/aether.lua"
    run_cmd cp -f "$DIR/neovim/lua/aether/init.lua" "$HOME/.config/nvim/lua/aether/init.lua"
    run_cmd cp -f "$DIR/neovim/lua/lualine/themes/aether.lua" "$HOME/.config/nvim/lua/lualine/themes/aether.lua"
fi

# 6c. Kate / KTextEditor
if should_run "kate" && [ -f "$DIR/kate/Aether Dark.theme" ]; then
    log "Applying Kate / KTextEditor color theme..."
    run_cmd mkdir -p "$HOME/.local/share/org.kde.syntax-highlighting/themes"
    run_cmd cp -f "$DIR/kate/Aether Dark.theme" "$HOME/.local/share/org.kde.syntax-highlighting/themes/Aether Dark.theme"
    if ! $DRY_RUN; then
        for kde_rc in "$HOME/.config/katerc" "$HOME/.config/kwriterc"; do
            if [ -f "$kde_rc" ]; then
                backup_file "$kde_rc"
                try_cmd kwriteconfig6 --file "$kde_rc" --group "KTextEditor Renderer" --key "Auto Color Theme Selection" "false"
                try_cmd kwriteconfig6 --file "$kde_rc" --group "KTextEditor Renderer" --key "Color Theme" "Aether Dark"
            fi
        done
    fi
fi

# 7. Starship
if should_run "starship" && [ -f "$DIR/starship/starship.toml" ]; then
    log "Applying Starship config..."
    run_cmd mkdir -p "$HOME/.config"
    backup_file "$HOME/.config/starship.toml"
    run_cmd cp -f "$DIR/starship/starship.toml" "$HOME/.config/starship.toml"
fi

# 8. Btop
if should_run "btop" && [ -f "$DIR/btop/aether.theme" ]; then
    log "Applying Btop theme..."
    run_cmd mkdir -p "$HOME/.config/btop/themes"
    run_cmd cp -f "$DIR/btop/aether.theme" "$HOME/.config/btop/themes/"
    if [ -f "$HOME/.config/btop/btop.conf" ]; then
        backup_file "$HOME/.config/btop/btop.conf"
        if ! $DRY_RUN; then
            if grep -q '^color_theme' "$HOME/.config/btop/btop.conf"; then
                sed -i 's/^color_theme *=.*/color_theme = "aether"/' "$HOME/.config/btop/btop.conf"
            else
                echo 'color_theme = "aether"' >> "$HOME/.config/btop/btop.conf"
            fi
        fi
    fi
fi

# 9. Bat
if should_run "bat"; then
    log "Applying Bat theme & config..."
    run_cmd mkdir -p "$HOME/.config/bat/themes"
    if [ -f "$DIR/bat/themes/Aether Dark.tmTheme" ]; then
        run_cmd cp -f "$DIR/bat/themes/Aether Dark.tmTheme" "$HOME/.config/bat/themes/Aether Dark.tmTheme"
        if ! $DRY_RUN && command -v bat >/dev/null 2>&1; then
            bat cache --build >/dev/null 2>&1 || true
        fi
    fi
    if [ -f "$DIR/bat/config" ]; then
        backup_file "$HOME/.config/bat/config"
        run_cmd cp -f "$DIR/bat/config" "$HOME/.config/bat/config"
    fi
fi

# 10. Git Delta
if should_run "delta" && command -v delta >/dev/null 2>&1; then
    log "Applying Git Delta theme..."
    if ! $DRY_RUN; then
        git config --global core.pager "delta"
        git config --global interactive.diffFilter "delta --color-only"
        git config --global delta.navigate true
        git config --global delta.light false
        git config --global delta.line-numbers true
        git config --global delta.syntax-theme "Aether Dark"
        git config --global delta.minus-style 'syntax "#441822"'
        git config --global delta.plus-style 'syntax "#143a35"'
        git config --global delta.line-numbers-minus-style "#f13460"
        git config --global delta.line-numbers-plus-style "#269e9c"
        git config --global delta.file-style 'bold "#3c78ff"'
        git config --global delta.file-decoration-style "#3c78ff ul"
        git config --global delta.hunk-header-decoration-style "#10a6d4 box"
    fi
fi

# 10b. Fastfetch
if should_run "fastfetch" && [ -f "$DIR/cli/fastfetch/aether.jsonc" ]; then
    log "Applying Fastfetch theme..."
    run_cmd mkdir -p "$HOME/.config/fastfetch"
    run_cmd cp -f "$DIR/cli/fastfetch/aether.jsonc" "$HOME/.config/fastfetch/aether.jsonc"
fi

# 10c. Eza
if should_run "eza" && [ -f "$DIR/cli/eza/theme.yml" ]; then
    log "Applying Eza theme..."
    run_cmd mkdir -p "$HOME/.config/eza"
    backup_file "$HOME/.config/eza/theme.yml"
    run_cmd cp -f "$DIR/cli/eza/theme.yml" "$HOME/.config/eza/theme.yml"
fi

# 10d. Lazygit
if should_run "lazygit" && [ -f "$DIR/cli/lazygit/aether-dark.yml" ]; then
    log "Applying Lazygit theme..."
    run_cmd mkdir -p "$HOME/.config/lazygit"
    run_cmd cp -f "$DIR/cli/lazygit/aether-dark.yml" "$HOME/.config/lazygit/aether-dark.yml"
fi

# 10e. Yazi
if should_run "yazi" && [ -f "$DIR/cli/yazi/theme.toml" ]; then
    log "Applying Yazi theme..."
    run_cmd mkdir -p "$HOME/.config/yazi"
    backup_file "$HOME/.config/yazi/theme.toml"
    run_cmd cp -f "$DIR/cli/yazi/theme.toml" "$HOME/.config/yazi/theme.toml"
fi

# 10f. Tmux
if should_run "tmux" && [ -f "$DIR/cli/tmux/aether.conf" ]; then
    log "Applying Tmux theme..."
    run_cmd mkdir -p "$HOME/.config/tmux"
    backup_file "$HOME/.config/tmux/aether.conf"
    run_cmd cp -f "$DIR/cli/tmux/aether.conf" "$HOME/.config/tmux/aether.conf"
    for tmux_rc in "$HOME/.config/tmux/tmux.conf" "$HOME/.tmux.conf"; do
        if [ -f "$tmux_rc" ]; then
            upsert_aether_shell_block "$tmux_rc" "# >>> Aether Theme >>>
source-file ~/.config/tmux/aether.conf
# <<< Aether Theme <<<"
        fi
    done
fi

# 10g. JetBrains IDEs
if should_run "jetbrains" && [ -f "$DIR/jetbrains/Aether_Dark.icls" ]; then
    log "Applying JetBrains color scheme..."
    run_cmd mkdir -p "$HOME/.local/share/aether-theme-suite/jetbrains"
    run_cmd cp -f "$DIR/jetbrains/Aether_Dark.icls" "$HOME/.local/share/aether-theme-suite/jetbrains/Aether_Dark.icls"
    shopt -s nullglob
    jb_dirs=("$HOME/.config/JetBrains/"*/)
    shopt -u nullglob
    for jb_dir in "${jb_dirs[@]}"; do
        run_cmd mkdir -p "${jb_dir}colors"
        run_cmd cp -f "$DIR/jetbrains/Aether_Dark.icls" "${jb_dir}colors/Aether_Dark.icls"
    done
fi

# 10h. Obsidian
if should_run "obsidian" && [ -d "$DIR/obsidian/Aether Dark" ]; then
    log "Staging Obsidian theme..."
    run_cmd mkdir -p "$HOME/.local/share/aether-theme-suite/obsidian/Aether Dark"
    run_cmd cp -rf "$DIR/obsidian/Aether Dark/"* "$HOME/.local/share/aether-theme-suite/obsidian/Aether Dark/"
    shopt -s nullglob
    vault_obs_dirs=("$HOME/Documents/"*/.obsidian "$HOME/Notes/"*/.obsidian "$HOME/Obsidian/"*/.obsidian)
    shopt -u nullglob
    for obs_dir in "${vault_obs_dirs[@]}"; do
        run_cmd mkdir -p "$obs_dir/themes/Aether Dark"
        run_cmd cp -rf "$DIR/obsidian/Aether Dark/"* "$obs_dir/themes/Aether Dark/"
    done
fi

# 10i. Discord / Vesktop / Vencord
if should_run "discord" && [ -f "$DIR/apps/discord/aether-dark.theme.css" ]; then
    log "Applying Discord / Vesktop theme..."
    discord_installed=false
    for client_dir in "$HOME/.config/vesktop" "$HOME/.config/Vencord" "$HOME/.config/BetterDiscord"; do
        if [ -d "$client_dir" ]; then
            run_cmd mkdir -p "$client_dir/themes"
            run_cmd cp -f "$DIR/apps/discord/aether-dark.theme.css" "$client_dir/themes/aether-dark.theme.css"
            discord_installed=true
        fi
    done
    if ! $discord_installed; then
        run_cmd mkdir -p "$HOME/.config/vesktop/themes"
        run_cmd cp -f "$DIR/apps/discord/aether-dark.theme.css" "$HOME/.config/vesktop/themes/aether-dark.theme.css"
    fi
fi

# 10j. Firefox / Zen Browser
if should_run "firefox" && [ -f "$DIR/apps/firefox/userChrome.css" ]; then
    log "Applying Firefox / Zen CSS..."
    run_cmd mkdir -p "$HOME/.local/share/aether-theme-suite/firefox"
    run_cmd cp -f "$DIR/apps/firefox/userChrome.css" "$HOME/.local/share/aether-theme-suite/firefox/userChrome.css"
    run_cmd cp -f "$DIR/apps/firefox/userContent.css" "$HOME/.local/share/aether-theme-suite/firefox/userContent.css"
    shopt -s nullglob
    ff_profiles=("$HOME/.mozilla/firefox/"*.default* "$HOME/.zen/"*.Default*)
    shopt -u nullglob
    for prof in "${ff_profiles[@]}"; do
        [ -d "$prof" ] || continue
        run_cmd mkdir -p "$prof/chrome"
        backup_file "$prof/chrome/userChrome.css"
        backup_file "$prof/chrome/userContent.css"
        run_cmd cp -f "$DIR/apps/firefox/userChrome.css" "$prof/chrome/userChrome.css"
        run_cmd cp -f "$DIR/apps/firefox/userContent.css" "$prof/chrome/userContent.css"
    done
fi

# 10k. Waybar
if should_run "waybar" && [ -f "$DIR/wayland/waybar/aether.css" ]; then
    log "Applying Waybar CSS..."
    run_cmd mkdir -p "$HOME/.config/waybar"
    backup_file "$HOME/.config/waybar/aether.css"
    run_cmd cp -f "$DIR/wayland/waybar/aether.css" "$HOME/.config/waybar/aether.css"
fi

# 10l. Rofi
if should_run "rofi" && [ -f "$DIR/wayland/rofi/aether.rasi" ]; then
    log "Applying Rofi theme..."
    run_cmd mkdir -p "$HOME/.config/rofi/themes"
    run_cmd cp -f "$DIR/wayland/rofi/aether.rasi" "$HOME/.config/rofi/themes/aether.rasi"
fi

# 10m. Fuzzel
if should_run "fuzzel" && [ -f "$DIR/wayland/fuzzel/aether.ini" ]; then
    log "Applying Fuzzel theme..."
    run_cmd mkdir -p "$HOME/.config/fuzzel"
    backup_file "$HOME/.config/fuzzel/aether.ini"
    run_cmd cp -f "$DIR/wayland/fuzzel/aether.ini" "$HOME/.config/fuzzel/aether.ini"
fi

# 10n. Dunst
if should_run "dunst" && [ -f "$DIR/wayland/dunst/aetherrc" ]; then
    log "Applying Dunst theme drop-in..."
    run_cmd mkdir -p "$HOME/.config/dunst/dunstrc.d"
    backup_file "$HOME/.config/dunst/dunstrc.d/99-aether.conf"
    run_cmd cp -f "$DIR/wayland/dunst/aetherrc" "$HOME/.config/dunst/dunstrc.d/99-aether.conf"
fi

# 10o. Mako
if should_run "mako" && [ -f "$DIR/wayland/mako/config" ]; then
    log "Applying Mako theme..."
    run_cmd mkdir -p "$HOME/.config/mako"
    backup_file "$HOME/.config/mako/aether.conf"
    run_cmd cp -f "$DIR/wayland/mako/config" "$HOME/.config/mako/aether.conf"
fi

# 10p. Zathura
if should_run "zathura" && [ -f "$DIR/cli/zathura/aether-dark" ]; then
    log "Applying Zathura theme..."
    run_cmd mkdir -p "$HOME/.config/zathura"
    backup_file "$HOME/.config/zathura/aether-dark"
    run_cmd cp -f "$DIR/cli/zathura/aether-dark" "$HOME/.config/zathura/aether-dark"
    if [ -f "$HOME/.config/zathura/zathurarc" ]; then
        upsert_aether_shell_block "$HOME/.config/zathura/zathurarc" "# >>> Aether Theme >>>
include aether-dark
# <<< Aether Theme <<<"
    fi
fi

# 10q. Cava
if should_run "cava" && [ -f "$DIR/cli/cava/aether.conf" ]; then
    log "Applying Cava theme..."
    run_cmd mkdir -p "$HOME/.config/cava/themes"
    backup_file "$HOME/.config/cava/themes/aether"
    run_cmd cp -f "$DIR/cli/cava/aether.conf" "$HOME/.config/cava/themes/aether"
fi

# 11. Shell FZF (+ optional bat alias)
if should_run "shell"; then
    log "Applying Shell FZF theme..."
    FISH_BLOCK="# >>> Aether Theme >>>
if type -q fzf
    set -gx FZF_DEFAULT_OPTS \" \\
    --color=bg+:#16181d,bg:#111216,spinner:#3c78ff,hl:#10a6d4 \\
    --color=fg:#abb2bf,header:#10a6d4,info:#3c78ff,pointer:#3c78ff \\
    --color=marker:#269e9c,fg+:#ffffff,prompt:#3c78ff,hl+:#10a6d4 \\
    --border=rounded --margin=1 --padding=1\"
end"
    POSIX_BLOCK="# >>> Aether Theme >>>
if command -v fzf >/dev/null 2>&1; then
    export FZF_DEFAULT_OPTS=\" \\
    --color=bg+:#16181d,bg:#111216,spinner:#3c78ff,hl:#10a6d4 \\
    --color=fg:#abb2bf,header:#10a6d4,info:#3c78ff,pointer:#3c78ff \\
    --color=marker:#269e9c,fg+:#ffffff,prompt:#3c78ff,hl+:#10a6d4 \\
    --border=rounded --margin=1 --padding=1\"
fi"

    if $WITH_SHELL_ALIASES; then
        FISH_BLOCK="$FISH_BLOCK
if type -q bat
    alias cat=\"bat --paging=never\"
end"
        POSIX_BLOCK="$POSIX_BLOCK
if command -v bat >/dev/null 2>&1; then
    alias cat=\"bat --paging=never\"
fi"
    fi

    FISH_BLOCK="$FISH_BLOCK
# <<< Aether Theme <<<"
    POSIX_BLOCK="$POSIX_BLOCK
# <<< Aether Theme <<<"

    upsert_aether_shell_block "$HOME/.config/fish/config.fish" "$FISH_BLOCK"
    upsert_aether_shell_block "$HOME/.zshrc" "$POSIX_BLOCK"
    upsert_aether_shell_block "$HOME/.bashrc" "$POSIX_BLOCK"
fi

log "Done."
