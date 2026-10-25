"""Phone-readable guide, with explicit coverage of the live binding snapshot."""
from pathlib import Path
from xml.sax.saxutils import escape
import json, re, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
ROOT=Path('/home/lookfrost/.local/share/frost-hyprland-setup')
DEST=ROOT/'output/shortcuts'; DEST.mkdir(parents=True,exist_ok=True)
OUT=DEST/'Frost-Hyprland-shortcuts.pdf'
# Each row is visible keys | action | exact live chords. Braces expand ranges.
DATA=r'''
@Windows|Focus, move, resize, float|Meta+L focuses right. Direct lock and sleep shortcuts are disabled.
#Focus and switch
Meta + H / J / K / L|Focus left / down / up / right.|Meta+{H J K L}
Meta + arrows|Focus in that direction.|Meta+{Left Down Up Right}
Meta + Alt + arrows|Alternative directional focus.|Meta+Alt+{Left Down Up Right}
Alt + Tab / Meta + Tab|Cycle windows on this desktop.|Alt+Tab;Meta+Tab
Add Shift to either Tab chord|Cycle windows backward.|Alt+Shift+Tab;Meta+Shift+Tab
Alt + ` / Meta + `|Cycle windows of the same app.|Alt+grave;Meta+grave
Add Shift to either ` chord|Cycle same-app windows backward.|Alt+Shift+grave;Meta+Shift+grave
#Move and resize
Meta + Shift + arrows|Move the window in that direction.|Meta+Shift+{Left Down Up Right}
Meta + Ctrl + H/J/K/L\nor Meta + Ctrl + arrows|Resize by 20 px; hold to repeat.|Meta+Ctrl+{H J K L Left Down Up Right}
Meta + left-drag|Drag the window.|Meta+mouse:272
Meta + right-drag|Resize. Floats first only if it is the sole window on this desktop.|Meta+mouse:273
Meta + X|Start resizing with the mouse.|Meta+X
#Window state
Meta + I / Meta + Alt + F10|Toggle floating.|Meta+I;Meta+Alt+F10
Meta + F|Toggle fullscreen.|Meta+F
Meta + Alt + F / Meta + PgUp|Toggle maximized.|Meta+Alt+F;Meta+Page_Up
Meta + PgDown|Minimize the active window.|Meta+Page_Down
Meta + Backspace|Restore all minimized windows to their original desktops.|Meta+BackSpace
Meta + D|Show desktop; press again to restore.|Meta+D
Meta + P|Toggle pinning across desktops.|Meta+P
Meta + W / Alt + F4|Close the active window.|Meta+W;Alt+F4
@Desktops & apps|Your number keys select desktops|Spotify hides in the music workspace. Meta+M brings it back.
#Virtual desktops
Meta + 1…9 / 0|Go to desktop 1…10 in this group. Zero means 10.|Meta+{1 2 3 4 5 6 7 8 9 0}
Meta + Shift + 1…9 / 0|Move the window to that desktop.|Meta+Shift+{1 2 3 4 5 6 7 8 9 0}
Ctrl + F1…F4 / Meta + F1…F4|Go directly to desktop 1…4.|Ctrl+{F1 F2 F3 F4};Meta+{F1 F2 F3 F4}
Meta + wheel up / down|Previous / next desktop.|Meta+mouse_up;Meta+mouse_down
Meta + Ctrl + Shift + ← / ↑|Move window to the previous desktop.|Meta+Ctrl+Shift+Left;Meta+Ctrl+Shift+Up
Meta + Ctrl + Shift + → / ↓|Move window to the next desktop.|Meta+Ctrl+Shift+Right;Meta+Ctrl+Shift+Down
#Launch your apps
Meta, press and release|Open the app launcher.|Meta+SUPER_L
Meta + R / Meta + Space|Open the app launcher.|Meta+R;Meta+Space
Alt + Space / Alt + F2\nor Search key|Alternative launcher shortcuts.|Alt+Space;Alt+F2;XF86Search
Meta + Enter / Meta + T|Open WezTerm.|Meta+Return;Meta+T
Meta + Alt + Enter|Open Foot.|Meta+Alt+Return
Meta + B / E / C / Z|Brave / Dolphin / VSCodium / ROG Control Center, respectively.|Meta+{B E C Z}
Ctrl + Alt + V|Open audio settings.|Ctrl+Alt+V
#Hidden / special desktops
Meta + S|Show / hide the general special workspace.|Meta+S
Meta + M|Show / hide the music workspace.|Meta+M
Meta + Alt + D|Show / hide the communication workspace.|Meta+Alt+D
Ctrl + Shift + Esc|Show / hide the system monitor workspace.|Ctrl+Shift+Escape
Meta + Alt + S|Move window into the general special workspace.|Meta+Alt+S
Meta + Ctrl + Alt + S|Move window out to the active normal desktop.|Meta+Ctrl+Alt+S
@Capture & appearance|Screenshots, recordings, wallpaper, clipboard|Meta+Shift+S takes a screenshot. Meta+S opens the special workspace.
#Screenshots and recordings
Print Screen|Take a screenshot.|Print
Meta + Shift + S|Freeze the screen and select a screenshot region.|Meta+Shift+S
Ctrl + Shift + S\nor Meta + Alt + Shift + S|Select a screenshot region.|Ctrl+Shift+S;Meta+Alt+Shift+S
Ctrl + Alt + R|Start / stop a fullscreen recording.|Ctrl+Alt+R
Meta + Alt + R|Start / stop recording with sound.|Meta+Alt+R
Meta + Shift + R\nor Meta + Alt + Shift + R|Start / stop a region recording.|Meta+Shift+R;Meta+Alt+Shift+R
Meta + Shift + C|Pick a screen color and copy its hex value.|Meta+Shift+C
#Wallpaper and theme
Meta + Alt + W|Open the wallpaper picker.|Meta+Alt+W
Meta + Shift + W|Choose a random wallpaper.|Meta+Shift+W
Launcher: wa|Find wallpapers without typing the full word.|
Launcher: th / sc|Find themes / color schemes.|
Tab in the launcher|Complete the wallpaper or theme keyword.|
Launcher: wallpaper forest|Filter wallpapers by their names.|
#Clipboard and emoji
Meta + V|Open clipboard history.|Meta+V
Meta + Alt + V|Open clipboard history in delete mode.|Meta+Alt+V
Ctrl + Alt + Shift + V|Paste the newest clipboard entry.|Ctrl+Alt+Shift+V
Meta + .|Open the emoji picker.|Meta+Period
@Media & gestures|Sound, light, touchpad|Hold Shift with volume or screen-brightness keys for fine 1% steps.
#Music and sound
Play / Pause media keys|Toggle playback.|XF86AudioPlay;XF86AudioPause
Meta + Ctrl + Space|Toggle playback from the keyboard.|Meta+Ctrl+Space
Next / Previous media keys|Skip to the next / previous track.|XF86AudioNext;XF86AudioPrev
Meta + Ctrl + = / -|Next / previous track.|Meta+Ctrl+Equal;Meta+Ctrl+Minus
Stop media key\nor Meta + Ctrl + Backspace|Stop playback.|XF86AudioStop;Meta+Ctrl+BackSpace
Mute key / Meta + Shift + M|Toggle output mute.|XF86AudioMute;Meta+Shift+M
Microphone mute key|Toggle microphone mute.|XF86AudioMicMute
Volume up / down keys|Change output volume by 10%.|XF86AudioRaiseVolume;XF86AudioLowerVolume
Shift + volume keys|Change output volume by 1%.|Shift+XF86AudioRaiseVolume;Shift+XF86AudioLowerVolume
#Brightness
Screen-brightness keys|Raise / lower screen brightness.|XF86MonBrightnessUp;XF86MonBrightnessDown
Shift + screen-brightness keys|Raise / lower brightness by 1%.|Shift+XF86MonBrightnessUp;Shift+XF86MonBrightnessDown
Keyboard-brightness keys|Raise / lower keyboard backlight.|XF86KbdBrightnessUp;XF86KbdBrightnessDown
#Touchpad gestures
3 fingers ← / →|Slide between virtual desktops.|
3 fingers ↑ / ↓|Show / hide the general special workspace.|
@Panels & advanced|Shell controls, groups, layout|Stop shell hides the panels. Use Restart shell to bring them back.
#Panels and session
Meta + N|Toggle the sidebar.|Meta+N
Meta + Alt + K|Toggle shell panels.|Meta+Alt+K
Ctrl + Alt + C|Clear notifications.|Ctrl+Alt+C
Ctrl + Alt + Delete|Open the session / power menu.|Ctrl+Alt+Delete
Meta + Ctrl + Alt + R|Restart the Caelestia shell; runs on release.|Meta+Ctrl+Alt+R
Meta + Ctrl + Shift + R|Stop the Caelestia shell; runs on release.|Meta+Ctrl+Shift+R
Meta + Alt + F12|Send a test notification.|Meta+Alt+F12
#Window groups
Meta + ,|Toggle a window group.|Meta+Comma
Meta + Shift + ,|Toggle the active group lock.|Meta+Shift+Comma
Meta + U|Move the window out of its group.|Meta+U
Ctrl + Alt + Tab|Next window in the group.|Ctrl+Alt+Tab
Ctrl + Alt + Shift + Tab|Previous window in the group.|Ctrl+Alt+Shift+Tab
#Layout and workspace groups
Meta + Ctrl + \|Center the window.|Meta+Ctrl+Backslash
Meta + Ctrl + Alt + \|Size to 55% × 70% of the screen, then center.|Meta+Ctrl+Alt+Backslash
Meta + Alt + \|Picture-in-picture: float, pin and resize.|Meta+Alt+Backslash
Meta + Ctrl + Alt + - / =|Decrease / increase window width.|Meta+Ctrl+Alt+Minus;Meta+Ctrl+Alt+Equal
Meta + Ctrl + Shift + - / =|Decrease / increase window height.|Meta+Ctrl+Shift+Minus;Meta+Ctrl+Shift+Equal
Meta + Ctrl + wheel ↑ / ↓|Previous / next workspace group (±10).|Meta+Ctrl+mouse_up;Meta+Ctrl+mouse_down
Meta + Ctrl + Alt + 1…9 / 0|Jump to workspace group 1…10.|Meta+Ctrl+Alt+{1 2 3 4 5 6 7 8 9 0}
Add Shift to group numbers|Move window to that workspace group.|Meta+Ctrl+Alt+Shift+{1 2 3 4 5 6 7 8 9 0}
@Launcher & terminal|Search commands and your shell conveniences|Type a launcher command, choose its result, then press Enter to run it.
#Launcher controls and power commands
↑ / ↓ · Enter · Esc|Select a result · open it · close launcher.|
Tab|Complete the selected command keyword.|
>|Browse launcher actions; >calc opens calculator.|
shutdown / power off / turn off|Shut down the computer.|
reboot / restart|Restart the computer.|
logout / log out / sign out|Log out of this session.|
lock / lock screen|Lock this session.|
sleep / suspend / hibernate|Sleep uses suspend-then-hibernate; the others request their named modes.|
>light / >dark / >variant|Choose light, dark or a palette variant.|
#Fish and zoxide
cd name / z name|Use a path or jump to a remembered directory.|
cdi / zi|Pick a remembered directory interactively.|
↑ / ↓ after typing|Search command history by the typed prefix.|
Ctrl + F|Accept the autosuggestion.|
Ctrl + W / Ctrl + D|Delete the previous word / delete or exit.|
Ctrl + ← / →|Move backward / forward by one word.|
.. / ...|Expand to cd .. / cd ../..|
ll / la / lt · cat · top|Detailed / all / tree listings · bat · btop.|
gs / gd / gl / lg|Git status / diff / graph / lazygit.|
reload · pipapp|Reload Fish config · manage Python CLI apps through pipx.|
#Terminal-specific controls
WezTerm: Shift + Enter|Send the alternate Enter sequence (Esc + Enter).|
Foot: PgUp / PgDown|Scroll one page up / down.|
Foot: Ctrl + Shift + F|Search scrollback.|
Foot search: F3 / Ctrl + G|Next match; Shift+F3 goes to previous match.|
Foot search: Esc|Leave scrollback search.|
'''
covered=set(); pages=[]
for line in DATA.strip().splitlines():
    if line.startswith('@'):
        title,subtitle,note=line[1:].split('|');pages.append([title,subtitle,note,[]])
    elif line.startswith('#'):
        pages[-1][3].append([line[1:],[]])
    else:
        keys,action,specs=line.split('|')
        pages[-1][3][-1][1].append((keys.replace(r'\n','\n'),action))
        for spec in filter(None,specs.split(';')):
            match=re.fullmatch(r'(.*)\{(.*)\}',spec)
            expanded=[match[1]+key for key in match[2].split()] if match else [spec]
            for item in expanded:
                parts=item.split('+');bits={'Meta':64,'Ctrl':4,'Alt':8,'Shift':1}
                covered.add((sum(bits[p] for p in parts[:-1]),parts[-1].lower()))
live=json.loads((ROOT/'current-bindings-for-sheet.json').read_text())
internal={'caps_lock','num_lock',''}
actual={(b['modmask'],b['key'].lower()) for b in live if b['key'].lower() not in internal}
assert not actual-covered, f'Undocumented: {sorted(actual-covered)}'
assert not covered-actual, f'Absent from live bindings: {sorted(covered-actual)}'
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Keys','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/TTF/'+file))
W,H=540,1200; M=30; COL=245
colors={k:HexColor(v) for k,v in dict(bg='#F5F3ED',ink='#192C3B',muted='#536875',accent='#315D79',gold='#B58A48',cap='#E6EBEC',line='#D4DBDC').items()}
c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle("Frost's complete Hyprland shortcuts");c.setAuthor('LookFrost')
ks=ParagraphStyle('keys',fontName='Keys',fontSize=10.4,leading=14.3,textColor=colors['ink'])
bs=ParagraphStyle('body',fontName='Body',fontSize=11.1,leading=15.1,textColor=colors['ink'])
ns=ParagraphStyle('note',fontName='Body',fontSize=11.2,leading=15.5,textColor=colors['ink'])
def para(text,style,width):
    p=Paragraph(escape(text).replace('\n','<br/>'),style);_,h=p.wrap(width,1000);return p,h
bottoms=[]
for number,(title,subtitle,note,sections) in enumerate(pages,1):
    c.setFillColor(colors['bg']);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(colors['accent']);c.roundRect(M,H-61,37,31,7,fill=1,stroke=0)
    c.setFillColor(HexColor('#FFFFFF'));c.setFont('Bold',14);c.drawCentredString(M+18.5,H-51,'LF')
    c.setFillColor(colors['accent']);c.setFont('Bold',10);c.drawString(M+48,H-42,'FROST / HYPRLAND')
    c.setFillColor(colors['muted']);c.setFont('Body',9);c.drawString(M+48,H-57,'YOUR CUSTOM SHORTCUTS · 25 OCT 2026')
    c.setFillColor(colors['gold']);c.setFont('Bold',28);c.drawRightString(W-M,H-56,f'{number:02}')
    c.setFillColor(colors['ink']);c.setFont('Bold',29);c.drawString(M,H-109,title)
    c.setFillColor(colors['muted']);c.setFont('Body',11);c.drawString(M,H-131,subtitle)
    p,ph=para(note,ns,W-2*M-24);nh=ph+22;top=H-149
    c.setFillColor(HexColor('#E6DDD0'));c.roundRect(M,top-nh,W-2*M,nh,7,fill=1,stroke=0)
    p.drawOn(c,M+12,top-ph-10);y=top-nh-25
    for heading,rows in sections:
        c.setFillColor(colors['accent']);c.setFont('Bold',12);c.drawString(M,y,heading);y-=9
        c.setStrokeColor(colors['gold']);c.setLineWidth(1);c.line(M,y,W-M,y);y-=9
        for keys,action in rows:
            kp,kh=para(keys,ks,COL-18);ap,ah=para(action,bs,W-2*M-COL-12)
            rh=max(kh,ah)+(11 if number==6 else 14)
            c.setFillColor(colors['cap']);c.roundRect(M,y-rh+4,COL-9,rh-8,4,fill=1,stroke=0)
            kp.drawOn(c,M+8,y-7-kh);ap.drawOn(c,M+COL+3,y-7-ah);y-=rh
            c.setStrokeColor(colors['line']);c.setLineWidth(.35);c.line(M+COL+3,y,W-M,y)
        y-=22
    bottoms.append(round(y,1));assert y>52,(number,title,y)
    c.setStrokeColor(colors['line']);c.setLineWidth(.6);c.line(M,46,W-M,46)
    c.setFillColor(colors['muted']);c.setFont('Body',9)
    c.drawString(M,29,'Meta = Windows / Super key.  + = hold together.  / = alternatives.')
    c.drawString(M,15,'All live desktop bindings, plus custom terminal controls. App defaults vary.')
    c.setFont('Bold',9);c.drawRightString(W-M,29,f'{number} / {len(pages)}');c.showPage()
c.save();reader=PdfReader(str(OUT));assert len(reader.pages)==len(pages)
text='\n'.join(p.extract_text() for p in reader.pages)
for token in ['Meta + H / J / K / L','Meta + X','Meta + Shift + 1','Foot search','cdi / zi']:assert token in text,token
copy=ROOT/'output/pdf'/OUT.name;copy.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OUT,copy)
(DEST/'coverage.json').write_text(json.dumps({'live_user_bindings':len(actual),'documented_bindings':len(covered),'excluded_internal_keys':sorted(internal),'pages':len(pages),'bottom_margins_pt':bottoms},indent=2)+'\n')
print(f'{OUT}\n{len(pages)} pages; {len(actual)} live user bindings covered. Bottoms: {bottoms}')
