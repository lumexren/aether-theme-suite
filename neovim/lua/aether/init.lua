-- Aether Dark — Neovim colorscheme
local M = {}

M.palette = {
  crust = "#0c0d11",
  mantle = "#0e0f13",
  base = "#111216",
  surface0 = "#16181d",
  surface1 = "#171920",
  surface2 = "#1a1d24",
  overlay0 = "#1f2228",
  overlay1 = "#262a33",
  overlay2 = "#3b404a",
  comment = "#5c6370",
  subtext0 = "#707888",
  subtext1 = "#8e96a5",
  subtext2 = "#9199a8",
  text = "#abb2bf",
  text_bright = "#f4f4f4",
  white = "#ffffff",
  blue = "#3c78ff",
  blue_bright = "#6296ff",
  blue_dim = "#3062d6",
  cyan = "#10a6d4",
  cyan_bright = "#38c6f0",
  teal = "#269e9c",
  red = "#f13460",
  yellow = "#e5c07b",
  peach = "#d19a66",
  purple = "#a673f5",
  diff_add = "#132033",
  diff_warn = "#282214",
  diff_delete = "#2a121a",
}

function M.setup()
  vim.cmd("hi clear")
  if vim.fn.exists("syntax_on") == 1 then
    vim.cmd("syntax reset")
  end
  vim.o.termguicolors = true
  vim.o.background = "dark"
  vim.g.colors_name = "aether"

  local p = M.palette
  local hl = function(group, opts)
    vim.api.nvim_set_hl(0, group, opts)
  end

  -- Editor UI
  hl("Normal", { fg = p.text, bg = p.base })
  hl("NormalNC", { fg = p.text, bg = p.base })
  hl("NormalFloat", { fg = p.text, bg = p.surface0 })
  hl("FloatBorder", { fg = p.overlay1, bg = p.surface0 })
  hl("FloatTitle", { fg = p.cyan, bg = p.surface0, bold = true })
  hl("Cursor", { fg = p.base, bg = p.blue })
  hl("CursorLine", { bg = p.surface1 })
  hl("CursorColumn", { bg = p.surface1 })
  hl("ColorColumn", { bg = p.surface0 })
  hl("LineNr", { fg = p.comment })
  hl("CursorLineNr", { fg = p.blue, bold = true })
  hl("SignColumn", { fg = p.comment, bg = p.base })
  hl("FoldColumn", { fg = p.comment, bg = p.base })
  hl("Folded", { fg = p.subtext1, bg = p.surface0 })
  hl("VertSplit", { fg = p.overlay0 })
  hl("WinSeparator", { fg = p.overlay0 })
  hl("StatusLine", { fg = p.text, bg = p.mantle })
  hl("StatusLineNC", { fg = p.comment, bg = p.mantle })
  hl("TabLine", { fg = p.subtext1, bg = p.surface0 })
  hl("TabLineFill", { bg = p.mantle })
  hl("TabLineSel", { fg = p.white, bg = p.blue, bold = true })
  hl("Pmenu", { fg = p.text, bg = p.surface0 })
  hl("PmenuSel", { fg = p.white, bg = p.blue, bold = true })
  hl("PmenuSbar", { bg = p.surface1 })
  hl("PmenuThumb", { bg = p.overlay1 })
  hl("Visual", { bg = p.diff_add })
  hl("Search", { fg = p.base, bg = p.cyan })
  hl("IncSearch", { fg = p.white, bg = p.blue, bold = true })
  hl("CurSearch", { fg = p.white, bg = p.blue, bold = true })
  hl("MatchParen", { fg = p.cyan_bright, bg = p.overlay1, bold = true })
  hl("NonText", { fg = p.overlay2 })
  hl("Whitespace", { fg = p.overlay1 })
  hl("SpecialKey", { fg = p.overlay2 })
  hl("Directory", { fg = p.blue, bold = true })
  hl("Title", { fg = p.blue, bold = true })
  hl("ErrorMsg", { fg = p.red, bold = true })
  hl("WarningMsg", { fg = p.yellow, bold = true })
  hl("MoreMsg", { fg = p.teal })
  hl("Question", { fg = p.cyan })

  -- Diff
  hl("DiffAdd", { bg = p.diff_add })
  hl("DiffChange", { bg = p.diff_warn })
  hl("DiffDelete", { fg = p.red, bg = p.diff_delete })
  hl("DiffText", { bg = p.overlay1, bold = true })

  -- Syntax
  hl("Comment", { fg = p.comment, italic = true })
  hl("Constant", { fg = p.peach })
  hl("String", { fg = p.teal })
  hl("Character", { fg = p.teal })
  hl("Number", { fg = p.peach })
  hl("Boolean", { fg = p.peach })
  hl("Float", { fg = p.peach })
  hl("Identifier", { fg = p.text })
  hl("Function", { fg = p.blue })
  hl("Statement", { fg = p.purple })
  hl("Conditional", { fg = p.purple })
  hl("Repeat", { fg = p.purple })
  hl("Label", { fg = p.purple })
  hl("Operator", { fg = p.cyan })
  hl("Keyword", { fg = p.purple })
  hl("Exception", { fg = p.purple })
  hl("PreProc", { fg = p.purple })
  hl("Include", { fg = p.purple })
  hl("Define", { fg = p.purple })
  hl("Type", { fg = p.yellow })
  hl("StorageClass", { fg = p.purple })
  hl("Structure", { fg = p.yellow })
  hl("Typedef", { fg = p.yellow })
  hl("Special", { fg = p.cyan_bright })
  hl("SpecialChar", { fg = p.cyan_bright })
  hl("Tag", { fg = p.red })
  hl("Delimiter", { fg = p.subtext1 })
  hl("SpecialComment", { fg = p.subtext0, italic = true })
  hl("Error", { fg = p.white, bg = p.red })
  hl("Todo", { fg = p.base, bg = p.yellow, bold = true })

  -- Treesitter
  hl("@comment", { link = "Comment" })
  hl("@comment.documentation", { fg = p.subtext0, italic = true })
  hl("@string", { link = "String" })
  hl("@string.escape", { fg = p.cyan_bright })
  hl("@string.regexp", { fg = p.cyan_bright })
  hl("@number", { link = "Number" })
  hl("@boolean", { link = "Boolean" })
  hl("@constant", { link = "Constant" })
  hl("@constant.builtin", { fg = p.peach })
  hl("@keyword", { link = "Keyword" })
  hl("@keyword.operator", { fg = p.cyan })
  hl("@function", { link = "Function" })
  hl("@function.method", { fg = p.blue_bright })
  hl("@function.builtin", { fg = p.blue_bright })
  hl("@type", { link = "Type" })
  hl("@type.builtin", { fg = p.yellow })
  hl("@operator", { link = "Operator" })
  hl("@variable", { fg = p.text })
  hl("@variable.builtin", { fg = p.red })
  hl("@variable.member", { fg = p.red })
  hl("@property", { fg = p.red })
  hl("@tag", { fg = p.red })
  hl("@tag.attribute", { fg = p.peach })
  hl("@punctuation", { fg = p.subtext1 })
  hl("@markup.heading", { fg = p.blue, bold = true })
  hl("@markup.strong", { fg = p.peach, bold = true })
  hl("@markup.italic", { fg = p.purple, italic = true })
  hl("@markup.raw", { fg = p.teal })

  -- Diagnostics & LSP
  hl("DiagnosticError", { fg = p.red })
  hl("DiagnosticWarn", { fg = p.yellow })
  hl("DiagnosticInfo", { fg = p.blue })
  hl("DiagnosticHint", { fg = p.cyan })
  hl("DiagnosticUnderlineError", { undercurl = true, sp = p.red })
  hl("DiagnosticUnderlineWarn", { undercurl = true, sp = p.yellow })
  hl("DiagnosticUnderlineInfo", { undercurl = true, sp = p.blue })
  hl("DiagnosticUnderlineHint", { undercurl = true, sp = p.cyan })
  hl("LspReferenceText", { bg = p.surface2 })
  hl("LspReferenceRead", { bg = p.surface2 })
  hl("LspReferenceWrite", { bg = p.overlay0 })

  -- Plugins (GitSigns, Telescope, Neo-tree, NvimTree, WhichKey, IndentBlankline)
  hl("GitSignsAdd", { fg = p.teal })
  hl("GitSignsChange", { fg = p.cyan })
  hl("GitSignsDelete", { fg = p.red })
  hl("TelescopeBorder", { fg = p.overlay1, bg = p.surface0 })
  hl("TelescopePromptBorder", { fg = p.blue, bg = p.surface0 })
  hl("TelescopeSelection", { fg = p.white, bg = p.surface2, bold = true })
  hl("TelescopeMatching", { fg = p.cyan, bold = true })
  hl("NeoTreeNormal", { fg = p.text, bg = p.surface0 })
  hl("NeoTreeNormalNC", { fg = p.text, bg = p.surface0 })
  hl("NvimTreeNormal", { fg = p.text, bg = p.surface0 })
  hl("WhichKey", { fg = p.cyan })
  hl("WhichKeyGroup", { fg = p.blue })
  hl("WhichKeyDesc", { fg = p.text })
  hl("IblIndent", { fg = p.overlay0 })
  hl("IblScope", { fg = p.blue })

  -- Terminal ANSI colors
  vim.g.terminal_color_0 = "#3b404a"
  vim.g.terminal_color_1 = "#f13460"
  vim.g.terminal_color_2 = "#269e9c"
  vim.g.terminal_color_3 = "#e5c07b"
  vim.g.terminal_color_4 = "#3c78ff"
  vim.g.terminal_color_5 = "#a673f5"
  vim.g.terminal_color_6 = "#10a6d4"
  vim.g.terminal_color_7 = "#abb2bf"
  vim.g.terminal_color_8 = "#707888"
  vim.g.terminal_color_9 = "#ff557a"
  vim.g.terminal_color_10 = "#38c4c0"
  vim.g.terminal_color_11 = "#f6d28a"
  vim.g.terminal_color_12 = "#6296ff"
  vim.g.terminal_color_13 = "#c094ff"
  vim.g.terminal_color_14 = "#38c6f0"
  vim.g.terminal_color_15 = "#f4f4f4"
end

return M
