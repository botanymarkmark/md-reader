# -*- coding: utf-8 -*-
"""
MD Reader —— 极简 Markdown 阅读器（启动器版）

不打包浏览器内核：把渲染好的页面交给系统自带的 Edge，用 --app 模式开一个
无地址栏、无标签页的独立窗口。所以整个 exe 只有几 MB。
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import winreg

APP_NAME = 'MD Reader'
WINDOW_SIZE = '1100,860'


def resource(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def read_text(path):
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'gbk', 'utf-16'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', 'replace')


def find_edge():
    keys = [r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe']
    for key in keys:
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(root, key) as k:
                    p = winreg.QueryValue(k, None)
                    if p and os.path.exists(p):
                        return p
            except OSError:
                pass
    for p in (
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    ):
        if os.path.exists(p):
            return p
    return None


def find_chrome():
    for p in (
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    ):
        if os.path.exists(p):
            return p
    return None


def build_page(md_path):
    tpl = read_text(resource('MD Reader.html'))
    if not md_path:
        return tpl

    text = read_text(md_path)
    folder = os.path.dirname(os.path.abspath(md_path)).replace('\\', '/')
    payload = json.dumps(text).replace('</', '<\\/')
    name = json.dumps(os.path.basename(md_path), ensure_ascii=True)

    inject = (
        '<base href="file:///%s/">'
        '<script>window.__MD__=%s;window.__MD_NAME__=%s;window.__MD_DIR__="file:///%s";</script>'
        % (folder, payload, name, folder)
    )
    return tpl.replace('<!--INJECT-->', inject)


def page_name(md_path):
    """每篇文档一个固定文件名：同一篇重复打开复用，改过内容就换新地址避免缓存"""
    if not md_path:
        return 'start.html'
    st = os.stat(md_path)
    key = '%s|%d|%d' % (os.path.abspath(md_path), st.st_mtime_ns, st.st_size)
    digest = hashlib.md5(key.encode('utf-8')).hexdigest()[:10]
    return 'view-%s.html' % digest


def main():
    args = [a for a in sys.argv[1:] if a and not a.startswith('-')]
    md = args[0] if args and os.path.isfile(args[0]) else None

    html = build_page(md)

    out_dir = os.path.join(tempfile.gettempdir(), 'md-reader')
    os.makedirs(out_dir, exist_ok=True)
    page = os.path.join(out_dir, page_name(md))
    with open(page, 'w', encoding='utf-8') as f:
        f.write(html)

    url = 'file:///' + page.replace('\\', '/')

    browser = find_edge() or find_chrome()
    if browser:
        cmd = [browser, '--app=' + url, '--window-size=' + WINDOW_SIZE]
        try:
            subprocess.Popen(cmd, close_fds=True)
            return
        except OSError:
            pass

    os.startfile(page)  # 兜底：用默认浏览器打开


if __name__ == '__main__':
    main()
