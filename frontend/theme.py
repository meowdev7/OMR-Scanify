import sys
import tkinter as tk


PALETTES = {
    "dark": {"window": "#080A0D", "sidebar": "#111418", "panel": "#15181D", "panel_alt": "#11151B", "border": "#2A2F36", "text": "#F4F7FB", "muted": "#A7A7A7", "blue": "#1769E8", "hover": "#1C2128"},
    "light": {"window": "#F4F6F9", "sidebar": "#E8ECF2", "panel": "#FFFFFF", "panel_alt": "#F8FAFC", "border": "#D5DCE6", "text": "#17202B", "muted": "#667384", "blue": "#1769E8", "hover": "#DCE8FA"},
}


def system_theme():
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                return "light" if winreg.QueryValueEx(key, "AppsUseLightTheme")[0] else "dark"
        except (OSError, ImportError):
            pass
    return "dark"


def resolve_theme(mode):
    return system_theme() if mode == "system" else mode


def _replace_color(value, palette, option):
    if not isinstance(value, str):
        return value
    is_background = option in ("bg", "background", "activebackground", "highlightbackground")
    light_surface = palette["panel"] if is_background else palette["text"]
    colors = {"BLACK": palette["window"] if is_background else palette["text"], "WHITE": light_surface, "#080A0D": palette["window"], "#080D17": palette["window"], "#111418": palette["sidebar"], "#15181D": palette["panel"], "#101722": palette["panel"], "#11151B": palette["panel_alt"], "#22272E": palette["panel_alt"], "#151E2B": palette["panel_alt"], "#0B1423": palette["panel_alt"], "#0D1116": palette["panel_alt"], "#090C10": palette["panel_alt"], "#2A2F36": palette["border"], "#263242": palette["border"], "#252B34": palette["border"], "#242A33": palette["border"], "#F4F7FB": palette["text"], "#FFFFFF": light_surface, "#E8EDF4": palette["text"], "#DCEAFF": palette["text"], "#A7A7A7": palette["muted"], "#A9AFB8": palette["muted"], "#AEB7C5": palette["muted"], "#B9C1CC": palette["muted"], "#8B939E": palette["muted"], "#7C8591": palette["muted"], "#68717D": palette["muted"], "#1C2128": palette["hover"], "#171D25": palette["hover"], "#202D3E": palette["hover"], "#172943": palette["hover"], "#F4F6F9": palette["window"], "#E8ECF2": palette["sidebar"], "#F8FAFC": palette["panel_alt"], "#D5DCE6": palette["border"], "#17202B": palette["text"], "#667384": palette["muted"], "#DCE8FA": palette["hover"]}
    return colors.get(value.upper(), value)


def apply_theme(widget, mode):
    palette = PALETTES[resolve_theme(mode)]
    try:
        widget.configure(bg=palette["window"])
    except tk.TclError:
        pass
    for child in widget.winfo_children():
        try:
            config = {}
            for option in ("bg", "background", "fg", "foreground", "activebackground", "activeforeground", "insertbackground", "highlightbackground"):
                if option in child.keys():
                    config[option] = _replace_color(child.cget(option), palette, option)
            if config:
                child.configure(**config)
            if isinstance(child, (tk.Button, tk.Menubutton)):
                text = str(child.cget("text")).lower()
                is_action = any(label in text for label in ("create", "new project", "generate omr", "upload answer key"))
                base_background = _replace_color(child.master.cget("bg"), palette, "bg") if is_action else _replace_color(child.cget("bg"), palette, "bg")
                hover_background = palette["blue"] if is_action else palette["hover"]
                child._theme_base_background = base_background
                child._theme_hover_background = hover_background
                child.configure(highlightthickness=1, highlightbackground=palette["border"], highlightcolor=palette["blue"], bg=base_background)

                def on_enter(event, button=child):
                    button.configure(bg=button._theme_hover_background)

                def on_leave(event, button=child):
                    button.configure(bg=button._theme_base_background)

                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)
            if "menu" in child.keys() and child.cget("menu"):
                menu = child.nametowidget(child.cget("menu"))
                menu.configure(bg=palette["panel_alt"], fg=palette["text"], activebackground=palette["blue"], activeforeground=palette["text"])
            if isinstance(child, tk.Menu):
                child.configure(bg=palette["panel_alt"], fg=palette["text"], activebackground=palette["blue"], activeforeground=palette["text"])
        except tk.TclError:
            pass
        apply_theme(child, mode)