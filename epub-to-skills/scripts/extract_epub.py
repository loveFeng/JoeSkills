#!/usr/bin/env python3
"""extract_epub.py — 可靠的 EPUB -> 纯文本提取。

特性:
- 标准库 only (zipfile + html.parser + xml.etree)，无需安装依赖
- spine 感知: 优先按 OPF <spine> 顺序拼接章节；失败回退文件名自然排序
- 中文路径安全: 全程用 pathlib，不依赖 cwd
- 输出 ASCII 工作目录下的 _book_text.txt，章节以 '=== <relpath> ===' 分隔

用法:
    python extract_epub.py --epub "D:/Downloads/被讨厌的勇气.epub" \
                           --out "./books/bei-taoyan-de-yongqi" \
                           --slug bei-taoyan-de-yongqi
"""
import argparse
import os
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET


class TextExtractor(HTMLParser):
    BLOCK = {"p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6",
             "li", "tr", "section", "blockquote"}
    SKIP = {"script", "style", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        if tag in self.BLOCK:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip > 0:
            self._skip -= 1
        if tag in self.BLOCK:
            self._parts.append("\n")

    def handle_data(self, data):
        if self._skip == 0:
            self._parts.append(data)

    def text(self):
        txt = "".join(self._parts)
        txt = re.sub(r"\n{3,}", "\n\n", txt)
        return txt.strip()


def natural_key(name):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", name)]


def find_opf(zf):
    try:
        container = zf.read("META-INF/container.xml").decode("utf-8", "ignore")
    except KeyError:
        return None
    m = re.search(r'href="([^"]+\.opf)"', container)
    return m.group(1) if m else None


def spine_order(zf, opf_path):
    """返回按 spine 顺序排列的内容文件相对 zip 根的路径列表。"""
    try:
        opf = zf.read(opf_path).decode("utf-8", "ignore")
        root = ET.fromstring(opf)
        ns = "http://www.idpf.org/2007/opf"
        manifest = {}
        for it in root.iter(f"{{{ns}}}item"):
            iid = it.get("id")
            href = it.get("href")
            if iid and href:
                manifest[iid] = href
        spine = [r.get("idref") for r in root.iter(f"{{{ns}}}itemref")]
        base = os.path.dirname(opf_path)
        ordered = []
        for ref in spine:
            href = manifest.get(ref)
            if href:
                ordered.append(os.path.normpath(os.path.join(base, href)))
        return ordered
    except Exception:
        return []


def all_html(zf):
    return [n for n in zf.namelist()
            if n.lower().endswith((".xhtml", ".html", ".htm"))
            and "META-INF" not in n]


def main():
    ap = argparse.ArgumentParser(description="EPUB -> 纯文本提取")
    ap.add_argument("--epub", required=True, help="EPUB 绝对路径（可含中文）")
    ap.add_argument("--out", required=True, help="ASCII 输出工作目录")
    ap.add_argument("--slug", default="", help="目录名(ASCII)，默认用 out 最后一段")
    args = ap.parse_args()

    epub = Path(args.epub)
    if not epub.exists():
        print(f"[错误] EPUB 不存在: {epub}", file=sys.stderr)
        sys.exit(2)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(epub, "r") as zf:
        opf = find_opf(zf)
        order = spine_order(zf, opf) if opf else []
        if not order:
            order = sorted(all_html(zf), key=natural_key)
        chapters = []
        for rel in order:
            try:
                raw = zf.read(rel).decode("utf-8", "ignore")
            except KeyError:
                continue
            te = TextExtractor()
            te.feed(raw)
            txt = te.text()
            if txt.strip():
                chapters.append((rel, txt))

    out_file = out_dir / "_book_text.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        for rel, txt in chapters:
            f.write(f"\n=== {rel} ===\n\n")
            f.write(txt)
            f.write("\n")

    total = sum(len(t) for _, t in chapters)
    print(f"[完成] 章节数={len(chapters)} 总字符≈{total}")
    print(f"[输出] {out_file}")


if __name__ == "__main__":
    main()
