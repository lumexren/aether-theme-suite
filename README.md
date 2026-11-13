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

### Desktop & Core

| Target | Path | Description |
| :--- | :--- | :--- |
| **Palette** | [`palette/`](palette/) | Canonical `palette.json`, `palette.css` & semantic tokens |
| **KDE Plasma 6** | [`plasma/`](plasma/) | Global Theme, Color Scheme, Desktop Theme & 4K Wallpaper |
| **Kvantum** | [`plasma/kvantum/`](plasma/kvantum/) | Translucent SVG widget style (`kvantum-dark`) |
| **Aurorae v2** | [`plasma/aurorae/`](plasma/aurorae/) | Minimalist borderless window decoration |
| **GTK 3 / 4 & Libadwaita** | [`gtk/`](gtk/) | `Aether-Dark` theme & user CSS overrides |
| **Fontconfig** | [`fontconfig/`](fontconfig/) | Subpixel RGB & slight hinting configuration |

### Editors

| Target | Path | Description |
| :--- | :--- | :--- |
| **VS Code / VSCodium / Cursor** | [`vscode/`](vscode/) | `lumexren.aether-dark` extension (`.vsix` + preset settings) |
| **Zed** | [`zed/`](zed/) | `Aether Dark` editor & terminal theme |
| **Neovim** | [`neovim/`](neovim/) | Lua colorscheme (Treesitter, LSP, Telescope) & Lualine theme |
| **Kate / KWrite** | [`kate/`](kate/) | `Aether Dark` KSyntaxHighlighting `.theme` |

### Terminals & Shell

| Target | Path | Description |
| :--- | :--- | :--- |
| **Konsole** | [`konsole/`](konsole/) | `Aether.colorscheme` + profile setup |
| **Ghostty** | [`terminals/ghostty/`](terminals/ghostty/) | Native `aether-dark` palette theme |
| **Kitty** | [`terminals/kitty/`](terminals/kitty/) | `aether-dark.conf` colors & tab bar styling |
| **Alacritty** | [`terminals/alacritty/`](terminals/alacritty/) | `aether-dark.toml` color scheme |
| **WezTerm** | [`terminals/wezterm/`](terminals/wezterm/) | `aether-dark.toml` scheme & tab bar |
| **Fish / Zsh / Bash** | [`install.sh`](install.sh) | `FZF_DEFAULT_OPTS` Aether color configuration |

### CLI & TUI

| Target | Path | Description |
| :--- | :--- | :--- |
| **Starship** | [`starship/`](starship/) | Minimalist prompt with Aether accent tokens |
| **Btop** | [`btop/`](btop/) | System monitor `aether.theme` |
| **Bat** | [`bat/`](bat/) | Custom `Aether Dark.tmTheme` & pager config |
| **Git Delta** | [`install.sh`](install.sh) | Diff styling paired with `Aether Dark` syntax theme |
| **Fastfetch** | [`cli/fastfetch/`](cli/fastfetch/) | `aether.jsonc` system info layout & colors |
| **Eza** | [`cli/eza/`](cli/eza/) | `theme.yml` file, permission, size & git colors |
| **Lazygit** | [`cli/lazygit/`](cli/lazygit/) | `aether-dark.yml` UI & diff theme |
| **Yazi** | [`cli/yazi/`](cli/yazi/) | `theme.toml` file manager & MIME rules |
| **Tmux** | [`cli/tmux/`](cli/tmux/) | `aether.conf` status bar, panes & copy mode |

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
