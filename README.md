<div align="center">

# Aether Theme Suite

*A unified, deep obsidian desktop & developer theme suite with electric royal blue and cyan accents.*

<br/>

`#111216` &nbsp;✦&nbsp; `#16181d` &nbsp;✦&nbsp; `#3c78ff` &nbsp;✦&nbsp; `#10a6d4` &nbsp;✦&nbsp; `#269e9c` &nbsp;✦&nbsp; `#f13460`

<br/>

[Palette](https://github.com/aether-theme-suite/palette) · [Components](#coverage) · [Installation](#installation) · [License](LICENSE)

</div>

---

## Overview

**Aether** synchronizes your Linux desktop, editors, terminals, and CLI tools into one cohesive **Deep Obsidian** aesthetic with translucent glass surfaces, crisp typography, and high-contrast electric accents.

* **Palette:** Deep Obsidian (`#111216`) · Surface (`#16181d`) · Royal Blue (`#3c78ff`) · Electric Cyan (`#10a6d4`) · Teal (`#269e9c`) · Crimson (`#f13460`) · Electric Violet (`#a673f5`)
* **Canonical Source:** [`aether-theme-suite/palette`](https://github.com/aether-theme-suite/palette)
* **Typography:** `Google Sans` (Desktop / UI) · `JetBrainsMono Nerd Font` (Code / Terminal)
* **Font Rendering:** RGB Subpixel Antialiasing · Slight Hinting

---

## Coverage

| Component | Target | Included |
| :--- | :--- | :--- |
| **Palette** | All Ports | [`palette/`](https://github.com/aether-theme-suite/palette) — `palette.json`, `palette.css`, ANSI & semantic tokens |
| **Desktop** | KDE Plasma 6 | Global Theme (`Look & Feel`), Color Scheme (`Aether.colors`), Desktop Theme, 4K Wallpaper |
| **Widgets** | Kvantum Engine | `Aether` translucent SVG theme (`kvantum-dark`) |
| **Windows** | Aurorae v2 | `Aether` minimalist borderless window decoration |
| **Apps** | GTK 3 · GTK 4 · Libadwaita | `Aether-Dark` GTK theme + user CSS overrides |
| **Editors** | VS Code · VSCodium · Zed | `lumexren.aether-dark` extension (`.vsix` + source) & `zed/aether.json` |
| **Terminals** | Konsole · Fish | `Aether.colorscheme` + FZF Aether colors |
| **CLI & TUI** | Btop · Bat · Starship · Delta | System monitor theme, prompt, syntax pager & Git diff styling |
| **Fonts** | Fontconfig | Subpixel RGB & crisp desktop/code font configuration |

---

## Installation

Clone the repository including submodules and run the installer:

```bash
git clone --recursive https://github.com/aether-theme-suite/aether-theme-suite.git
cd aether-theme-suite
./install.sh
```

> [!NOTE]
> `install.sh` applies Plasma 6, Kvantum, Aurorae, GTK 3/4, Konsole, VS Code/VSCodium/Antigravity IDE, Zed, Starship, Btop, Bat, Delta, and Fish FZF settings for the current user.

### Recommended Dependencies

* **KDE Plasma 6** + **Kvantum** (`kvantum-dark` widget style)
* **Icons & Cursor:** `Papirus-Dark` and `Bibata-Modern-Ice`
* **Fonts:** `Google Sans` and `JetBrainsMono Nerd Font`
* **CLI Tools:** `starship`, `btop`, `bat`, `git-delta`, `fzf`

---

## Repository Structure

```text
aether-theme-suite/
├── palette/         # Submodule -> aether-theme-suite/palette (tokens & CSS variables)
├── plasma/          # KDE Plasma 6 (look-and-feel, desktoptheme, color-schemes, aurorae, kvantum, wallpaper)
├── gtk/             # Aether-Dark GTK 3/4 theme & Libadwaita overrides
├── vscode/          # Aether Dark VS Code extension source, .vsix package & preset
├── zed/             # Zed editor theme (aether.json)
├── konsole/         # Konsole color scheme
├── starship/        # Starship prompt config
├── btop/            # Btop system monitor theme
├── bat/             # Bat pager config
├── fontconfig/      # Font rendering configs
└── install.sh       # Automated installer
```

---

## License

Released under the [MIT License](LICENSE).
