#!/usr/bin/env python3
"""
One-click installer for OpenCode (TUI + Desktop) Absolutely theme & Noto Serif SC font.
Reads theme definitions from ./themes/ in the same directory.
Usage:
  python3 install-opencode-appearance.py
"""
import glob
import hashlib
import json
import os
import plistlib
import re
import shutil
import sqlite3
import struct
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TUI_THEME_SRC = os.path.join(SCRIPT_DIR, "themes", "absolutely.json")
DESKTOP_THEME_SRC = os.path.join(SCRIPT_DIR, "themes", "absolutely-desktop.json")

HOME = os.path.expanduser("~")
OPENCODE_CFG_DIR = os.path.join(HOME, ".config", "opencode")
TUI_THEME_DST = os.path.join(OPENCODE_CFG_DIR, "themes", "absolutely.json")
TUI_JSON_PATH = os.path.join(OPENCODE_CFG_DIR, "tui.json")
SQLITE_PATH = os.path.join(HOME, "Library", "Application Support", "ai.opencode.desktop", "drafts.sqlite")
APP_PATH = "/Applications/OpenCode.app"


def install_tui():
    os.makedirs(os.path.dirname(TUI_THEME_DST), exist_ok=True)
    shutil.copy2(TUI_THEME_SRC, TUI_THEME_DST)
    tui_cfg = {}
    if os.path.exists(TUI_JSON_PATH):
        with open(TUI_JSON_PATH, "r", encoding="utf-8") as f:
            tui_cfg = json.load(f)
    tui_cfg["theme"] = "absolutely"
    with open(TUI_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(tui_cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("[1/3] Installed TUI theme ->", TUI_THEME_DST)


def install_font_sqlite():
    if not os.path.exists(SQLITE_PATH):
        print("[2/3] Skipped drafts.sqlite (not found yet, default font stack in app.asar will still use Noto Serif SC)")
        return
    conn = sqlite3.connect(SQLITE_PATH, timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT value FROM state WHERE name='default.dat' AND key='settings.v3'")
    row = cur.fetchone()
    if row:
        settings = json.loads(row[0])
        settings.setdefault("appearance", {})
        settings["appearance"]["sans"] = "Noto Serif SC"
        settings["appearance"]["fontSize"] = 14
        cur.execute(
            "UPDATE state SET value=? WHERE name='default.dat' AND key='settings.v3'",
            (json.dumps(settings, separators=(",", ":")),),
        )
        conn.commit()
    conn.close()
    print("[2/3] Updated UI font to Noto Serif SC (14px) in", SQLITE_PATH)


def install_desktop_asar():
    if not os.path.exists(APP_PATH):
        print("[3/3] Skipped /Applications/OpenCode.app (not installed)")
        return

    with open(DESKTOP_THEME_SRC, "r", encoding="utf-8") as f:
        abs_theme_obj = json.load(f)
    abs_theme_js = "var AbsTheme=" + json.dumps(abs_theme_obj, separators=(",", ":")) + ";"

    staged_app = "/tmp/OpenCode-appearance-stage.app"
    if os.path.exists(staged_app):
        shutil.rmtree(staged_app)
    subprocess.run(["cp", "-cR", APP_PATH, staged_app], check=True)

    asar_path = os.path.join(staged_app, "Contents/Resources/app.asar")
    plist_path = os.path.join(staged_app, "Contents/Info.plist")

    with open(asar_path, "rb") as f:
        asar_bytes = f.read()

    p1, p2, p3, p4 = struct.unpack("<IIII", asar_bytes[:16])
    header = json.loads(asar_bytes[16 : 16 + p4].decode("utf-8"))
    base_offset = 8 + p2
    payload = asar_bytes[base_offset:]

    def get_entry(parts):
        cur = header["files"]
        for p in parts[:-1]:
            cur = cur[p]["files"]
        return cur[parts[-1]]

    assets_files = header["files"]["out"]["files"]["renderer"]["files"]["assets"]["files"]
    main_js_name = next(k for k in assets_files if k.startswith("main-") and k.endswith(".js"))
    css_names = [k for k in assets_files if (k.startswith("settings-") or k.startswith("main-")) and k.endswith(".css")]

    # 1. Patch index.html
    html_entry = get_entry(["out", "renderer", "index.html"])
    html_off, html_sz = int(html_entry["offset"]), int(html_entry["size"])
    html_str = payload[html_off : html_off + html_sz].decode("utf-8")
    if "opencode-absolutely-v3" not in html_str:
        html_str = html_str.replace(
            'var key = "opencode-theme-id"\n  var themeId = localStorage.getItem(key) || "oc-2"',
            'var key = "opencode-theme-id"\n  if (!localStorage.getItem("opencode-absolutely-v3")) { localStorage.setItem(key, "absolutely"); localStorage.removeItem("opencode-theme-css-light"); localStorage.removeItem("opencode-theme-css-dark"); localStorage.setItem("opencode-absolutely-v3", "1"); }\n  var themeId = localStorage.getItem(key) || "absolutely"',
        )
    html_bytes_patched = html_str.encode("utf-8")

    # 2. Patch main-*.js (regex-based across version minifications)
    js_entry = get_entry(["out", "renderer", "assets", main_js_name])
    js_off, js_sz = int(js_entry["offset"]), int(js_entry["size"])
    js_str = payload[js_off : js_off + js_sz].decode("utf-8")
    if "var AbsTheme=" not in js_str:
        js_str, c1 = re.subn(
            r'(function [A-Za-z0-9_$]+\(\)\{return [A-Za-z0-9_$]+\|\|\([A-Za-z0-9_$]+=Object\.assign\(\{)("\./themes/amoled\.json")',
            lambda m: abs_theme_js + m.group(1) + '"./themes/absolutely.json":()=>G(()=>Promise.resolve().then(()=>({default:AbsTheme})),void 0,import.meta.url),' + m.group(2),
            js_str,
            count=1,
        )
        js_str, c2 = re.subn(
            r'(var [A-Za-z0-9_$]+=\{"oc-2":`OpenCode`,)(amoled:`AMOLED`)',
            r'\1absolutely:`Absolutely`,\2',
            js_str,
            count=1,
        )
        js_str, c3 = re.subn(
            r'(let t=[A-Za-z0-9_$]+\([A-Za-z0-9_$]+\.THEME_ID\)\?\?e\.defaultTheme)(,n=[A-Za-z0-9_$]+\(t\);t&&t!==n&&\([A-Za-z0-9_$]+\([A-Za-z0-9_$]+\.THEME_ID,n\),[A-Za-z0-9_$]+\(\)\);let r=[A-Za-z0-9_$]+\([A-Za-z0-9_$]+\.COLOR_SCHEME\)\?\?`system`,i=r===`system`\?[A-Za-z0-9_$]+\(\):r,\[a,o\]=[A-Za-z0-9_$]+\(\{themes:\{"oc-2":[A-Za-z0-9_$]+)(\},themeId:n)',
            r'\1??`absolutely`\2,absolutely:AbsTheme\3',
            js_str,
            count=1,
        )
        js_str, c4 = re.subn(
            r'(let t=[A-Za-z0-9_$]+\([A-Za-z0-9_$]+\.THEME_ID\)\?\?e\.defaultTheme)(,n=[A-Za-z0-9_$]+\(t,a\.themes\))',
            r'\1??`absolutely`\2',
            js_str,
            count=1,
        )
        js_str, c5 = re.subn(
            r'([A-Za-z0-9_$]+)=`Inter`,([A-Za-z0-9_$]+=`JetBrainsMono Nerd Font Mono`,[A-Za-z0-9_$]+=`"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace`,[A-Za-z0-9_$]+=`)"Inter"(, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`)',
            r'\1=`Noto Serif SC`,\2"Noto Serif SC", "Inter"\3',
            js_str,
            count=1,
        )
        js_str, c6 = re.subn(
            r'appearance:\{fontSize:14,mono:``,sans:``,terminal:``,tabLayout:`horizontal`\}',
            'appearance:{fontSize:14,mono:``,sans:`Noto Serif SC`,terminal:``,tabLayout:`horizontal`}',
            js_str,
            count=1,
        )
        assert all([c1, c2, c3, c4, c5, c6]), f"JS patch counts mismatch: {[c1, c2, c3, c4, c5, c6]}"
    js_bytes_patched = js_str.encode("utf-8")

    # 3. Patch main-*.css & settings-*.css for disabled vs active submit button
    old_disabled = ":is([data-component=button-v2][data-variant=submit],[data-component=icon-button-v2]:is([data-variant=submit],[data-variant=contrast])):is(:disabled,[data-state=disabled]){opacity:.4;cursor:not-allowed}"
    new_disabled = ":is([data-component=button-v2][data-variant=submit],[data-component=icon-button-v2]:is([data-variant=submit],[data-variant=contrast])):is(:disabled,[data-state=disabled]){--v2-background-bg-icon-button-contrast:var(--v2-grey-900);opacity:.4;cursor:not-allowed}"
    css_patched_map = {}
    for css_name in css_names:
        css_entry = get_entry(["out", "renderer", "assets", css_name])
        css_off, css_sz = int(css_entry["offset"]), int(css_entry["size"])
        css_str = payload[css_off : css_off + css_sz].decode("utf-8")
        if old_disabled in css_str:
            css_str = css_str.replace(old_disabled, new_disabled)
            css_patched_map[css_name] = css_str.encode("utf-8")

    packed_files = []

    def walk_tree(node, path_tuple=()):
        for name, info in node.get("files", {}).items():
            cur_path = path_tuple + (name,)
            if "files" in info:
                walk_tree(info, cur_path)
            elif not info.get("unpacked", False) and "offset" in info:
                packed_files.append((int(info["offset"]), int(info["size"]), cur_path, info))

    walk_tree(header)
    packed_files.sort(key=lambda x: x[0])

    block_size = 4 * 1024 * 1024

    def update_integrity(info, content_bytes):
        info["size"] = len(content_bytes)
        if "integrity" in info:
            info["integrity"]["hash"] = hashlib.sha256(content_bytes).hexdigest()
            blocks = [
                hashlib.sha256(content_bytes[i : i + block_size]).hexdigest()
                for i in range(0, len(content_bytes), block_size)
            ]
            info["integrity"]["blocks"] = blocks or [hashlib.sha256(b"").hexdigest()]

    new_payload = bytearray()
    for old_off, old_sz, path_tuple, info in packed_files:
        if path_tuple == ("out", "renderer", "index.html"):
            file_bytes = html_bytes_patched
            update_integrity(info, file_bytes)
        elif path_tuple == ("out", "renderer", "assets", main_js_name):
            file_bytes = js_bytes_patched
            update_integrity(info, file_bytes)
        elif len(path_tuple) == 4 and path_tuple[:3] == ("out", "renderer", "assets") and path_tuple[3] in css_patched_map:
            file_bytes = css_patched_map[path_tuple[3]]
            update_integrity(info, file_bytes)
        else:
            file_bytes = payload[old_off : old_off + old_sz]
        info["offset"] = str(len(new_payload))
        new_payload.extend(file_bytes)

    new_header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    new_header_hash = hashlib.sha256(new_header_bytes).hexdigest()

    new_p4 = len(new_header_bytes)
    aligned_p4 = ((new_p4 + 3) // 4) * 4
    padding_len = aligned_p4 - new_p4

    with open(asar_path, "wb") as f:
        f.write(struct.pack("<IIII", 4, 8 + aligned_p4, 4 + aligned_p4, new_p4))
        f.write(new_header_bytes)
        if padding_len:
            f.write(b"\x00" * padding_len)
        f.write(new_payload)

    with open(plist_path, "rb") as f:
        plist_data = plistlib.load(f)
    plist_data["ElectronAsarIntegrity"]["Resources/app.asar"]["hash"] = new_header_hash
    with open(plist_path, "wb") as f:
        plistlib.dump(plist_data, f)

    subprocess.run(
        ["codesign", "--force", "--deep", "--preserve-metadata=entitlements", "--sign", "-", staged_app],
        check=True,
    )
    subprocess.run(["codesign", "--verify", "--deep", "--strict", staged_app], check=True)
    shutil.rmtree(APP_PATH)
    shutil.move(staged_app, APP_PATH)
    print("[3/3] Installed Desktop theme & font into /Applications/OpenCode.app (hash:", new_header_hash[:12] + "...)")


if __name__ == "__main__":
    install_tui()
    install_font_sqlite()
    install_desktop_asar()
