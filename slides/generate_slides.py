#!/usr/bin/env python3
"""
generate_slides.py
==================
Generates one .odp slide deck per .md chapter file in the course_redhat project.

Usage:
    python3 slides/generate_slides.py          # from project root
    python3 generate_slides.py                 # from slides/ directory

Output:
    slides/<mirror-of-source-tree>/<chapter>.odp

Theme: RHEL dark/red — near-black background, Red Hat red titles, off-white body
Dimensions: 16:9 widescreen (33.87 × 19.05 cm)
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from odf.opendocument import OpenDocumentPresentation
from odf.style import (
    Style,
    MasterPage,
    PageLayout,
    PageLayoutProperties,
    DrawingPageProperties,
    TextProperties,
    GraphicProperties,
    FontFace,
    ParagraphProperties,
)
from odf.draw import Page, Frame, TextBox
from odf.text import P

# ---------------------------------------------------------------------------
# THEME CONSTANTS
# ---------------------------------------------------------------------------

BG_COLOR    = "#1a1a1a"   # near-black background
TITLE_COLOR = "#ee0000"   # Red Hat red
BODY_COLOR  = "#f0f0f0"   # off-white body text
CODE_BG     = "#2d2d2d"   # dark code block background
CODE_FG     = "#f8f8f2"   # code text colour
MUTED_COLOR = "#888888"   # footer / slide numbers
SLIDE_W     = "33.87cm"
SLIDE_H     = "19.05cm"

TITLE_FONT  = "Liberation Sans"
BODY_FONT   = "Liberation Sans"
CODE_FONT   = "Liberation Mono"

# Slide geometry (all in cm)
MARGIN      = 1.0
CONTENT_Y   = 4.0         # y-start of content area below heading bar
FOOTER_Y    = 17.8
SLIDE_W_CM  = 33.87
SLIDE_H_CM  = 19.05
CONTENT_W   = SLIDE_W_CM - 2 * MARGIN
CONTENT_H   = SLIDE_H_CM - CONTENT_Y - 1.5

# ---------------------------------------------------------------------------
# MARKDOWN PARSER
# ---------------------------------------------------------------------------

@dataclass
class CodeBlock:
    lang: str
    lines: list[str]


@dataclass
class Section:
    heading: str
    level: int
    bullets: list[str] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)


@dataclass
class ParsedDoc:
    title: str
    intro: list[str]
    sections: list[Section]
    raw_path: Path


def _clean(line: str) -> str:
    line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
    line = re.sub(r'\*(.+?)\*',     r'\1', line)
    line = re.sub(r'`(.+?)`',       r'\1', line)
    line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
    line = re.sub(r'^#+\s*',        '',    line)
    line = re.sub(r'^>\s*',         '',    line)
    line = re.sub(r'^\s*[-*+]\s+',  '',    line)
    line = re.sub(r'^\s*\d+\.\s+',  '',    line)
    return line.strip()


def _table_to_bullets(lines: list[str]) -> list[str]:
    result = []
    for line in lines:
        if re.match(r'^\|[-| :]+\|', line):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        cells = [_clean(c) for c in cells if c.strip()]
        if len(cells) >= 2:
            result.append(f"{cells[0]}: {cells[1]}")
        elif len(cells) == 1 and cells[0]:
            result.append(cells[0])
    return result


def parse_markdown(path: Path) -> ParsedDoc:
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    title = path.stem.replace("-", " ").replace("_", " ").title()
    intro: list[str] = []
    sections: list[Section] = []
    current: Optional[Section] = None

    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    in_table = False
    table_buf: list[str] = []

    SKIP_HEADINGS = {"further reading", "next step", "next steps",
                     "table of contents"}

    for line in lines:
        # Skip TOC anchor and Back-to-TOC nav links — markdown-only navigation
        if '<a name="toc">' in line:
            continue
        if '[↑ Back to TOC]' in line or '[^ Back to TOC]' in line:
            continue

        m1 = re.match(r'^#\s+(.+)', line)
        if m1 and not in_code:
            title = _clean(m1.group(1))
            continue

        m23 = re.match(r'^(#{2,3})\s+(.+)', line)
        if m23 and not in_code:
            if in_table and table_buf:
                (current.bullets if current else intro).extend(
                    _table_to_bullets(table_buf))
                table_buf = []; in_table = False
            heading_text = _clean(m23.group(2))
            if heading_text.lower() in SKIP_HEADINGS:
                current = None
                continue
            current = Section(heading=heading_text, level=len(m23.group(1)))
            sections.append(current)
            continue

        fence = re.match(r'^```(\w*)', line)
        if fence:
            if not in_code:
                in_code = True
                code_lang = fence.group(1) or "text"
                code_buf = []
            else:
                in_code = False
                if code_buf and current:
                    current.code_blocks.append(CodeBlock(lang=code_lang, lines=code_buf[:]))
                code_buf = []
            continue

        if in_code:
            code_buf.append(line)
            continue

        if re.match(r'^---+\s*$', line):
            in_table = False; table_buf = []
            continue

        if line.strip().startswith('|'):
            in_table = True
            table_buf.append(line)
            continue
        elif in_table:
            (current.bullets if current else intro).extend(_table_to_bullets(table_buf))
            table_buf = []; in_table = False

        stripped = line.strip()
        if not stripped:
            continue
        cleaned = _clean(stripped)
        if not cleaned or cleaned.startswith('→') or cleaned.startswith('->'):
            continue
        if '↑ Back to TOC' in cleaned or 'Back to TOC' in cleaned:
            continue
        if current is None:
            intro.append(cleaned)
        else:
            if current is not None:
                current.bullets.append(cleaned)

    if in_table and table_buf:
        (current.bullets if current else intro).extend(_table_to_bullets(table_buf))

    return ParsedDoc(title=title, intro=intro, sections=sections, raw_path=path)


# ---------------------------------------------------------------------------
# ODP DOCUMENT HELPERS
# ---------------------------------------------------------------------------

def _cm(v: float) -> str:
    return f"{v:.4f}cm"


# ---------------------------------------------------------------------------
# THEME / STYLE OBJECTS
# key insight: Frame(stylename=...) requires a Style *object*, not a string.
# P(stylename=...) also requires a Style object.
# We therefore store Style objects in the styles dict.
# ---------------------------------------------------------------------------

class Styles:
    """All Style objects needed for building slides."""

    def __init__(self, doc: OpenDocumentPresentation):
        self._doc = doc
        self._setup(doc)

    def _mk_graphic(self, name: str, fill_color: Optional[str] = None) -> Style:
        s = Style(name=name, family="graphic")
        self._doc.automaticstyles.addElement(s)
        gp_kw: dict = {"stroke": "none"}
        if fill_color:
            gp_kw["fill"] = "solid"
            gp_kw["fillcolor"] = fill_color
        else:
            gp_kw["fill"] = "none"
        GraphicProperties(parent=s, **gp_kw)
        return s

    def _mk_para(self, name: str, *, color: str, size: str,
                 bold: bool = False, font: str = BODY_FONT,
                 align: str = "left", margin_top: str = "0cm") -> Style:
        s = Style(name=name, family="paragraph")
        self._doc.automaticstyles.addElement(s)
        ParagraphProperties(parent=s, textalign=align, margintop=margin_top)
        kw: dict = {"color": color, "fontsize": size, "fontname": font}
        if bold:
            kw["fontweight"] = "bold"
        TextProperties(parent=s, **kw)
        return s

    def _mk_drawing_page(self, name: str, bg: str) -> Style:
        s = Style(name=name, family="drawing-page")
        self._doc.automaticstyles.addElement(s)
        DrawingPageProperties(parent=s, fill="solid", fillcolor=bg,
                              backgroundsize="border")
        return s

    def _setup(self, doc: OpenDocumentPresentation):
        # slide background
        self.bg          = self._mk_drawing_page("SlideBackground", BG_COLOR)

        # graphic boxes
        self.red_fill    = self._mk_graphic("RedBar",       fill_color=TITLE_COLOR)
        self.trans_fill  = self._mk_graphic("TransBox")
        self.code_box    = self._mk_graphic("CodeBox",      fill_color=CODE_BG)

        # paragraph styles
        self.p_title     = self._mk_para("PTitleMain",  color=TITLE_COLOR, size="48pt",
                                         bold=True, font=TITLE_FONT)
        self.p_track     = self._mk_para("PTrack",      color=MUTED_COLOR, size="16pt")
        self.p_h2        = self._mk_para("PSectionH2",  color=TITLE_COLOR, size="32pt",
                                         bold=True, font=TITLE_FONT)
        self.p_body      = self._mk_para("PBody",       color=BODY_COLOR,  size="18pt",
                                         margin_top="0.12cm")
        self.p_bullet    = self._mk_para("PBullet",     color=BODY_COLOR,  size="17pt",
                                         margin_top="0.18cm")
        self.p_code      = self._mk_para("PCode",       color=CODE_FG,     size="11pt",
                                         font=CODE_FONT)
        self.p_footer    = self._mk_para("PFooter",     color=MUTED_COLOR, size="12pt")


def _new_doc() -> tuple[OpenDocumentPresentation, Styles]:
    doc = OpenDocumentPresentation()

    # Fonts
    for fname in (TITLE_FONT, CODE_FONT):
        doc.fontfacedecls.addElement(FontFace(name=fname, fontfamily=fname))

    # Page layout 16:9
    pl = PageLayout(name="WS169")
    doc.automaticstyles.addElement(pl)
    pl.addElement(PageLayoutProperties(
        pagewidth=SLIDE_W, pageheight=SLIDE_H,
        printorientation="landscape",
        margintop="0cm", marginbottom="0cm",
        marginleft="0cm", marginright="0cm",
    ))

    # Master page
    doc.masterstyles.addElement(MasterPage(name="RHEL", pagelayoutname="WS169"))

    styles = Styles(doc)
    return doc, styles


# ---------------------------------------------------------------------------
# LOW-LEVEL SLIDE PRIMITIVES
# ---------------------------------------------------------------------------

def _new_page(doc: OpenDocumentPresentation, st: Styles) -> Page:
    page = Page(masterpagename="RHEL", stylename=st.bg)
    doc.presentation.addElement(page)
    return page


def _red_bar(page: Page, st: Styles, height: float = 0.55) -> None:
    """Full-width red bar at top of slide."""
    f = Frame(stylename=st.red_fill,
              width=_cm(SLIDE_W_CM), height=_cm(height),
              x="0cm", y="0cm")
    f.addElement(TextBox())
    page.addElement(f)


def _text_frame(page: Page, st_graphic: Style, *,
                x: float, y: float, w: float, h: float) -> TextBox:
    f = Frame(stylename=st_graphic,
              width=_cm(w), height=_cm(h),
              x=_cm(x), y=_cm(y))
    tb = TextBox()
    f.addElement(tb)
    page.addElement(f)
    return tb


def _p(tb: TextBox, txt: str, st_para: Style) -> None:
    para = P(stylename=st_para)
    para.addText(txt)
    tb.addElement(para)


def _section_header(page: Page, heading: str, st: Styles) -> None:
    _red_bar(page, st, height=0.5)
    tb = _text_frame(page, st.trans_fill, x=MARGIN, y=0.62, w=CONTENT_W, h=2.9)
    _p(tb, heading, st.p_h2)


def _trunc_bullets(bullets: list[str], n: int = 10, max_ch: int = 115) -> list[str]:
    out = []
    for b in bullets[:n]:
        out.append(b[:max_ch - 1] + "…" if len(b) > max_ch else b)
    return out


def _trunc_code(lines: list[str], n: int = 14) -> list[str]:
    if len(lines) > n:
        return lines[:n] + [f"… ({len(lines) - n} more lines)"]
    return lines


COPYRIGHT = "© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0"


def _footer_path(pd: ParsedDoc) -> str:
    track_dirs = {'00-preface','01-getting-started','02-foundations',
                  '03-rhcsa','04-rhce','05-rhca','90-labs','98-reference'}
    for i, part in enumerate(pd.raw_path.parts):
        if part in track_dirs:
            return "/".join(pd.raw_path.parts[i:])
    return pd.raw_path.name


def _footer_copyright(page: Page, st: Styles) -> None:
    """Add copyright line at the bottom of any slide."""
    tb = _text_frame(page, st.trans_fill, x=MARGIN, y=FOOTER_Y, w=CONTENT_W, h=0.7)
    _p(tb, COPYRIGHT, st.p_footer)


# ---------------------------------------------------------------------------
# SLIDE FACTORIES
# ---------------------------------------------------------------------------

TRACK_LABELS = {
    "00-preface":         "Course Preface",
    "01-getting-started": "Track 1 — Getting Started",
    "02-foundations":     "Track 2 — Linux Foundations",
    "03-rhcsa":           "Track 3 — RHCSA Administration",
    "04-rhce":            "Track 4 — RHCE Automation",
    "05-rhca":            "Track 5 — RHCA Advanced Infrastructure",
    "90-labs":            "Lab Environment Setup",
    "98-reference":       "Reference Materials",
}


def _track_label(md_path: Path, root: Path) -> str:
    parts = md_path.relative_to(root).parts
    label = TRACK_LABELS.get(parts[0], parts[0])
    if len(parts) > 2:
        label += f" / {parts[1].replace('-', ' ').title()}"
    return label


def slide_title(doc: OpenDocumentPresentation, pd: ParsedDoc,
                track_label: str, st: Styles) -> None:
    page = _new_page(doc, st)

    # top bar
    _red_bar(page, st, height=0.7)

    # thin bottom bar
    f = Frame(stylename=st.red_fill,
              width=_cm(SLIDE_W_CM), height=_cm(0.12),
              x="0cm", y=_cm(SLIDE_H_CM - 0.12))
    f.addElement(TextBox())
    page.addElement(f)

    # track breadcrumb
    tb = _text_frame(page, st.trans_fill, x=MARGIN, y=1.1, w=CONTENT_W, h=0.9)
    _p(tb, track_label.upper(), st.p_track)

    # main title
    tb = _text_frame(page, st.trans_fill, x=MARGIN, y=2.3, w=CONTENT_W, h=5.5)
    _p(tb, pd.title, st.p_title)

    # intro excerpt
    intro = " ".join(pd.intro[:4])
    if len(intro) > 220:
        intro = intro[:217] + "…"
    if intro:
        tb = _text_frame(page, st.trans_fill, x=MARGIN, y=8.8, w=CONTENT_W, h=3.5)
        _p(tb, intro, st.p_body)

    # footer: file path (line 1) + copyright (line 2)
    tb = _text_frame(page, st.trans_fill, x=MARGIN, y=FOOTER_Y, w=CONTENT_W, h=1.0)
    _p(tb, _footer_path(pd), st.p_footer)
    _p(tb, COPYRIGHT, st.p_footer)


def slide_objectives(doc: OpenDocumentPresentation, pd: ParsedDoc,
                     st: Styles) -> None:
    headings = [s.heading for s in pd.sections
                if s.level == 2
                and s.heading.lower() not in {"further reading", "next step",
                                              "next steps", "summary"}][:8]
    if not headings:
        return
    page = _new_page(doc, st)
    _section_header(page, "Objectives — What You Will Learn", st)
    tb = _text_frame(page, st.trans_fill, x=MARGIN, y=CONTENT_Y,
                     w=CONTENT_W, h=CONTENT_H)
    for h in headings:
        _p(tb, f"▶  {h}", st.p_bullet)
    _footer_copyright(page, st)


def slide_content(doc: OpenDocumentPresentation, heading: str,
                  bullets: list[str], code: Optional[CodeBlock],
                  st: Styles) -> None:
    page = _new_page(doc, st)
    _section_header(page, heading, st)

    if code and not bullets:
        # full-width code
        lines = "\n".join(_trunc_code(code.lines))
        tb = _text_frame(page, st.code_box, x=MARGIN, y=CONTENT_Y,
                         w=CONTENT_W, h=CONTENT_H)
        _p(tb, lines, st.p_code)

    elif bullets and code:
        # left bullets, right code
        half = (CONTENT_W - 0.4) / 2
        tb_b = _text_frame(page, st.trans_fill, x=MARGIN, y=CONTENT_Y,
                           w=half, h=CONTENT_H)
        for b in _trunc_bullets(bullets, n=7):
            _p(tb_b, f"• {b}", st.p_bullet)
        lines = "\n".join(_trunc_code(code.lines, n=12))
        tb_c = _text_frame(page, st.code_box,
                           x=MARGIN + half + 0.4, y=CONTENT_Y,
                           w=half, h=CONTENT_H)
        _p(tb_c, lines, st.p_code)

    else:
        tb = _text_frame(page, st.trans_fill, x=MARGIN, y=CONTENT_Y,
                         w=CONTENT_W, h=CONTENT_H)
        for b in _trunc_bullets(bullets):
            _p(tb, f"• {b}", st.p_bullet)

    _footer_copyright(page, st)


def slide_summary(doc: OpenDocumentPresentation, pd: ParsedDoc,
                  st: Styles) -> None:
    takeaways = []
    for sec in pd.sections:
        if sec.level != 2:
            continue
        if sec.bullets:
            first = sec.bullets[0]
            if len(first) > 100:
                first = first[:97] + "…"
            takeaways.append(f"✓  {sec.heading}: {first}")
        elif sec.code_blocks:
            takeaways.append(f"✓  {sec.heading}")
        if len(takeaways) >= 7:
            break
    if not takeaways:
        return
    page = _new_page(doc, st)
    _section_header(page, f"Summary — {pd.title}", st)
    tb = _text_frame(page, st.trans_fill, x=MARGIN, y=CONTENT_Y,
                     w=CONTENT_W, h=CONTENT_H)
    for t in takeaways:
        _p(tb, t, st.p_bullet)
    _footer_copyright(page, st)


# ---------------------------------------------------------------------------
# PER-FILE BUILD
# ---------------------------------------------------------------------------

SKIP_H = {"further reading", "next step", "next steps"}


def build_odp(md_path: Path, out_path: Path, root: Path) -> None:
    pd = parse_markdown(md_path)
    track_label = _track_label(md_path, root)

    doc, st = _new_doc()

    # 1. title
    slide_title(doc, pd, track_label, st)

    # 2. objectives
    slide_objectives(doc, pd, st)

    # 3. content (one slide per H2)
    for sec in pd.sections:
        if sec.level > 2:
            continue
        if sec.heading.lower() in SKIP_H:
            continue
        if not sec.bullets and not sec.code_blocks:
            continue

        if not sec.code_blocks:
            slide_content(doc, sec.heading, sec.bullets, None, st)
        elif not sec.bullets:
            for cb in sec.code_blocks:
                slide_content(doc, sec.heading, [], cb, st)
        else:
            # first code block paired with bullets
            slide_content(doc, sec.heading, sec.bullets, sec.code_blocks[0], st)
            for cb in sec.code_blocks[1:]:
                slide_content(doc, f"{sec.heading} (cont.)", [], cb, st)

    # 4. summary
    slide_summary(doc, pd, st)

    doc.save(str(out_path))


# ---------------------------------------------------------------------------
# READ ORDER  (matches README.md table of contents exactly)
# ---------------------------------------------------------------------------

README_ORDER: list[str] = [
    "README.md",
    # Preface
    "00-preface/01-about.md",
    "00-preface/02-labs.md",
    "00-preface/03-conventions.md",
    # Getting Started
    "01-getting-started/01-vm-install.md",
    "01-getting-started/02-first-boot.md",
    "01-getting-started/03-sudo-updates.md",
    "01-getting-started/04-help-system.md",
    # Linux Foundations
    "02-foundations/01-shell-basics.md",
    "02-foundations/02-files-and-text.md",
    "02-foundations/03-pipes-redirection.md",
    "02-foundations/04-editors.md",
    "02-foundations/05-permissions.md",
    "02-foundations/06-acls.md",
    "02-foundations/labs/01-shared-team-dir.md",
    # RHCSA
    "03-rhcsa/01-packages-dnf.md",
    "03-rhcsa/02-storage-overview.md",
    "03-rhcsa/03-filesystems-fstab.md",
    "03-rhcsa/04-lvm.md",
    "03-rhcsa/05-systemd-basics.md",
    "03-rhcsa/06-logging-journald.md",
    "03-rhcsa/07-scheduling.md",
    "03-rhcsa/08-networking-basics.md",
    "03-rhcsa/09-networkmanager-nmcli.md",
    "03-rhcsa/10-dns-resolution.md",
    "03-rhcsa/11-firewalld.md",
    "03-rhcsa/12-ssh.md",
    "03-rhcsa/13-selinux-fundamentals.md",
    "03-rhcsa/14-selinux-avc-basics.md",
    "03-rhcsa/labs/01-static-ip-dns.md",
    "03-rhcsa/labs/02-systemd-service.md",
    "03-rhcsa/labs/03-lvm-xfs-grow.md",
    "03-rhcsa/labs/04-selinux-label-fix.md",
    # RHCE
    "04-rhce/01-automation-mindset.md",
    "04-rhce/02-bash-fundamentals.md",
    "04-rhce/03-ansible-setup-inventory.md",
    "04-rhce/04-ansible-playbooks.md",
    "04-rhce/05-ansible-vars-templates.md",
    "04-rhce/06-ansible-roles.md",
    "04-rhce/07-ansible-service-deploy.md",
    "04-rhce/08-ansible-patching.md",
    "04-rhce/labs/01-first-playbook.md",
    "04-rhce/labs/02-role-web-deploy.md",
    # RHCA — core
    "05-rhca/01-troubleshooting-playbook.md",
    "05-rhca/02-systemd-advanced.md",
    "05-rhca/03-systemd-hardening.md",
    "05-rhca/04-journald-retention.md",
    # RHCA — SELinux deep dive
    "05-rhca/selinux/01-fix-taxonomy.md",
    "05-rhca/selinux/02-semanage.md",
    "05-rhca/selinux/03-audit-workflow.md",
    "05-rhca/selinux/labs/01-nondefault-port.md",
    # RHCA — Networking deep dive
    "05-rhca/networking/01-nmcli-profiles.md",
    "05-rhca/networking/02-routing-method.md",
    "05-rhca/networking/03-tcpdump.md",
    "05-rhca/networking/04-l2-concepts.md",
    "05-rhca/networking/labs/01-debug-triad.md",
    # RHCA — Containers
    "05-rhca/containers/01-podman-fundamentals.md",
    "05-rhca/containers/02-rootless.md",
    "05-rhca/containers/03-volumes.md",
    "05-rhca/containers/04-secrets.md",
    "05-rhca/containers/05-systemd-integration.md",
    "05-rhca/containers/06-selinux-containers.md",
    "05-rhca/containers/labs/01-rootless-web.md",
    "05-rhca/containers/labs/02-secrets-rotate.md",
    # RHCA — Performance
    "05-rhca/perf/01-resource-triage.md",
    "05-rhca/perf/02-tuned.md",
    "05-rhca/perf/03-recovery-patterns.md",
    # Lab environments
    "90-labs/01-index.md",
    "90-labs/02-single-vm.md",
    "90-labs/03-multi-vm.md",
    # Reference
    "98-reference/01-objective-map.md",
    "98-reference/02-glossary.md",
    "98-reference/03-cheatsheets.md",
    "98-reference/04-further-reading.md",
]


def _slug(rel: str) -> str:
    """Convert a relative path like '03-rhcsa/labs/lvm.md' → '03-rhcsa-labs-lvm'."""
    return rel.replace("/", "-").replace(".md", "")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main() -> None:
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent if script_dir.name == "slides" else script_dir

    slides_root = root / "slides"
    slides_root.mkdir(exist_ok=True)

    # Wipe ALL existing .odp files (flat and in any subdirs) so stale files
    # from the previous subdirectory layout are removed.
    stale = list(slides_root.rglob("*.odp"))
    for f in stale:
        f.unlink()
    if stale:
        print(f"Removed {len(stale)} stale .odp file(s).")

    # Validate the order list covers every source .md exactly once
    all_md = {
        str(p.relative_to(root))
        for p in root.rglob("*.md")
        if "slides" not in p.parts
    }
    order_set = set(README_ORDER)
    missing  = all_md - order_set
    extra    = order_set - all_md
    if missing:
        print(f"WARNING: {len(missing)} .md file(s) not in README_ORDER — will be skipped:")
        for m in sorted(missing):
            print(f"  {m}")
    if extra:
        print(f"WARNING: {len(extra)} README_ORDER entry(s) not found on disk:")
        for e in sorted(extra):
            print(f"  {e}")

    # Build only what exists on disk, in README order
    ordered = [r for r in README_ORDER if (root / r).exists()]
    total   = len(ordered)

    print(f"\nGenerating {total} slide decks (flat) …")
    print(f"  Source root : {root}")
    print(f"  Output root : {slides_root}")
    print()

    errors: list[tuple[str, str]] = []
    for i, rel in enumerate(ordered, 1):
        md  = root / rel
        slug = _slug(rel)
        out = slides_root / f"{i:03d}-{slug}.odp"
        try:
            build_odp(md, out, root)
            print(f"  [{i:>3}/{total}] ✓  {out.name}")
        except Exception as exc:
            import traceback
            errors.append((rel, str(exc)))
            print(f"  [{i:>3}/{total}] ✗  {rel}  ERROR: {exc}")
            if "--debug" in sys.argv:
                traceback.print_exc()

    print()
    if errors:
        print(f"Completed with {len(errors)} error(s):")
        for p, e in errors:
            print(f"  {p}: {e}")
        sys.exit(1)
    else:
        print(f"All {total} decks generated successfully.")


if __name__ == "__main__":
    main()
