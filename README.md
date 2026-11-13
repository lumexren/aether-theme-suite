<div align="center">

<img src="plasma/look-and-feel/Aether/contents/previews/fullscreenpreview.jpg" alt="Aether Theme Suite Preview" width="360" />

# Aether Theme Suite

*A unified, deep obsidian desktop & developer theme suite with electric royal blue and cyan accents.*

<br/>

[Palette](palette/) · [Components](#coverage) · [Installation](#installation) · [License](LICENSE)

</div>

---

## Overview

**Aether** synchronizes your Linux desktop, editors, terminals, and CLI tools into one cohesive **Deep Obsidian** aesthetic with translucent glass surfaces, crisp typography, and high-contrast electric accents.

* **Palette:** Deep Obsidian (`#111216`) · Surface (`#16181d`) · Royal Blue (`#3c78ff`) · Electric Cyan (`#10a6d4`) · Teal (`#269e9c`) · Crimson (`#f13460`) · Electric Violet (`#a673f5`)
* **Canonical Source:** [`palette/palette.json`](palette/palette.json)
* **Typography:** `Google Sans` (Desktop / UI) · `JetBrainsMono Nerd Font` (Code / Terminal)
* **Font Rendering:** RGB Subpixel Antialiasing · Slight Hinting

---

## Coverage

| Component | Target | Included |
| :--- | :--- | :--- |
| **Palette** | All Ports | [`palette/`](palette/) — `palette.json`, `palette.css`, ANSI & semantic tokens |
| **Desktop** | KDE Plasma 6 | Global Theme (`Look & Feel`), Color Scheme (`Aether.colors`), Desktop Theme, 4K Wallpaper |
| **Widgets** | Kvantum Engine | `Aether` translucent SVG theme (`kvantum-dark`) |
| **Windows** | Aurorae v2 | `Aether` minimalist borderless window decoration |
| **Apps** | GTK 3 · GTK 4 · Libadwaita | `Aether-Dark` GTK theme + user CSS overrides |
| **Editors** | VS Code · VSCodium · Zed · Neovim · Kate | `lumexren.aether-dark` `.vsix`, `zed/aether.json`, Neovim Lua + Lualine, KTextEditor `.theme` |
| **Terminals** | Konsole · Ghostty · Kitty · Alacritty · WezTerm | Native color schemes for all 5 terminal emulators + Fish/Zsh/Bash FZF colors |
| **CLI & TUI** | Btop · Bat · Starship · Delta · Fastfetch · Eza · Lazygit · Yazi · Tmux | Full CLI/TUI styling synced with `palette.json` (`Aether Dark.tmTheme`, `eza`, `yazi`, etc.) |
| **Fonts** | Fontconfig | Subpixel RGB & crisp desktop/code font configuration |

---

## Installation

Clone the repository and run the installer:

```bash
git clone https://github.com/lumexren/aether-theme-suite.git
cd aether-theme-suite
./install.sh
```

Useful installer flags:

```bash
./install.sh --dry-run                   # Preview changes without touching files
./install.sh --only terminals,cli        # Install component groups or individual targets
./install.sh --skip plasma               # Skip specific components or groups
./install.sh --with-shell-aliases        # Also add `alias cat="bat --paging=never"`
./install.sh --uninstall                 # Remove Aether files & restore backups
```

> [!NOTE]
> `install.sh` backs up overwritten configs under `~/.local/state/aether-theme-suite/backups/` and supports Plasma 6, Kvantum, Aurorae, GTK 3/4, Konsole, Ghostty, Kitty, Alacritty, WezTerm, VS Code/VSCodium/Antigravity/Cursor, Zed, Neovim, Kate/KWrite, Starship, Btop, Bat (`Aether Dark.tmTheme`), Delta, Fastfetch, Eza, Lazygit, Yazi, Tmux, and Fish/Zsh/Bash FZF settings.

### Recommended Dependencies

* **KDE Plasma 6** + **Kvantum** (`kvantum-dark` widget style)
* **Icons & Cursor:** `Papirus-Dark` and `Bibata-Modern-Ice`
* **Fonts:** `Google Sans` and `JetBrainsMono Nerd Font`
* **CLI Tools:** `starship`, `btop`, `bat`, `git-delta`, `fzf`

---

<div align="center">

**Built with ❤️ by lumexren**

*Star ⭐ this repo if you find it useful!*

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.

</div>
