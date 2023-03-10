import os
import re
import socket
import subprocess
from libqtile import qtile
from libqtile.config import Click, Drag, Group, KeyChord, Key, Match, Screen
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from typing import List  # noqa: F401

from libqtile.layout.columns import Columns
from libqtile.layout.xmonad import MonadTall, MonadWide
from libqtile.layout.max import Max
from libqtile.layout.stack import Stack
from libqtile.layout.floating import Floating

from qtile_extras import widget
from qtile_extras.widget.decorations import BorderDecoration

from colors import catppuccin

mod = "mod4"
terminal = "alacritty"

keys = [
    # Launch applications
    Key([mod, "control"], "f", lazy.spawn('firefox'), desc="Launch browser"),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "r", lazy.spawn('rofi -show run')),

    # Toggle floating and fullscreen
    Key([mod], "f", lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen mode"),
    Key([mod, "shift"], "space", lazy.window.toggle_floating(),
        desc="Toggle fullscreen mode"),

    # Keybindings for resizing windows in MonadTall layout
    Key([mod], "i", lazy.layout.grow()),
    Key([mod], "m", lazy.layout.shrink()),
    Key([mod], "n", lazy.layout.normalize()),
    Key([mod], "o", lazy.layout.maximize()),
    Key([mod, "control"], "space", lazy.layout.flip()),

    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(),
        desc="Move window focus to other window"),

    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
        desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(),
        desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(),
        desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(),
        desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    # multiple stack panes
    Key([mod, "shift"], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
]

groups = [
    Group('1', label='???', matches=[Match(wm_class='firefox')], layout='max'),
    Group('2', label='????', layout='monadtall'),
    Group('3', label='???', matches=[Match(wm_class='Thunar')], layout='monadtall'),
    Group('4', label='???', matches=[Match(wm_class='Thunar')], layout='monadtall'),
    Group('5', label='????', matches=[Match(wm_class='discord')], layout='monadtall'),
    Group('6', label='????', matches=[Match(wm_class='Spotify')], layout='monadtall'),
]

for i in groups:
    keys.extend(
        [
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
        ]
    )

layouts = [
    Stack(
        border_normal=catppuccin['base'],
        border_focus=catppuccin['lavender'],
        border_width=2,
        num_stacks=1,
        margin=4,
    ),
    MonadTall(
        border_normal=catppuccin['base'],
        border_focus=catppuccin['lavender'],
        margin=4,
        border_width=2,
        single_border_width=2,
        single_margin=4,
    ),
    Columns(
        border_normal=catppuccin['base'],
        border_focus=catppuccin['lavender'],
        border_width=2,
        border_normal_stack=catppuccin['base'],
        border_focus_stack=catppuccin['lavender'],
        border_on_single=2,
        margin=4,
        margin_on_single=4,
    ),
    Max(
        border_normal=catppuccin['base'],
        border_focus=catppuccin['lavender'],
        border_width=2,
        margin=4
    )
]

floating_layout = Floating(
    border_normal=catppuccin['base'],
    border_focus=catppuccin['lavender'],
    border_width=2,
    float_rules=[
        *Floating.default_float_rules,
        Match(wm_class='confirmreset'),  # gitk
        Match(wm_class='makebranch'),  # gitk
        Match(wm_class='maketag'),  # gitk
        Match(wm_class='ssh-askpass'),  # ssh-askpass
        Match(title='branchdialog'),  # gitk
        Match(title='pinentry'),  # GPG key password entry

        Match(title="Android Emulator - pixel5:5554"),
        Match(wm_class="Genymotion Player"),
        Match(title="AICOMS"),
        Match(wm_class="blueman-manager"),
        Match(wm_class="pavucontrol"),
        Match(wm_class="zoom "),
        Match(wm_class="bitwarden"),
        Match(wm_class="xarchiver"),
        Match(wm_class="deepin-calculator")
])

widget_defaults = dict(
    font="FiraCode Nerd Font",
    fontsize=12,
    padding=8,
)
extension_defaults = widget_defaults.copy()

screens = [Screen(top=bar.Bar([
    widget.TextBox(
        text='???',
        fontsize=20,
        foreground=catppuccin['text']
    ),
    widget.TextBox(
        text='????',
        fontsize=25,
        padding=0
    ),
    widget.GroupBox(
        disable_drag=True,
        active=catppuccin['text'],
        inactive=catppuccin['subtext1'],
        highlight_method='line',
        block_highlight_text_color=catppuccin['yellow'],
        borderwidth=0,
        highlight_color=catppuccin['surface2'],
        background=catppuccin['surface2']
    ),
    widget.TextBox(
        text='\uE0B4',
        fontsize=20,
        foreground=catppuccin['surface2'],
        padding=0
    ),
    ], 
    background=['#00000000'], size=24, margin=4,
))]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wl_input_rules = None
wmname = "LG3D"

@ hook.subscribe.startup_once
def autostart():
    home=os.path.expanduser('~/.config/qtile/autostart.sh')
    subprocess.run([home])
