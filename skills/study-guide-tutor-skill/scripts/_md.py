#!/usr/bin/env python3
"""A small, safe Markdown-to-HTML renderer for the lessons shown in the study player (standard library only).

It handles what the generated lessons use: headings, paragraphs, GitHub tables, nested lists, block quotes (with the
"Tricky part" box and the audience note recognised), fenced code, ```mermaid diagrams (through a callback), horizontal
rules, `<details>`/`<summary>` boxes, images, links and the usual inline marks. Everything else is escaped, so a lesson
can never inject a script into the page. It is not a full CommonMark implementation and does not try to be.

Used by make_player.py. Callbacks in `ctx` (all optional):
  ctx['prefix']            string put in front of every heading id, so two chapters never collide
  ctx['link'](href)        -> ('go', 'quiz:3') | ('href', 'relative/path') | ('text', None): where a relative link goes
  ctx['image'](src, alt)   -> data URI string, or None to show the alt text only
  ctx['diagram'](code)     -> HTML for one mermaid diagram
"""
import re

ALLOWED_TAGS = ('b', 'i', 'em', 'strong', 'kbd', 'sub', 'sup', 'u', 'br', 'mark')
HEADING = re.compile(r'^(#{1,6})\s+(.+?)\s*#*\s*$')
HR = re.compile(r'^\s{0,3}([-*_])(?:\s*\1){2,}\s*$')
FENCE = re.compile(r'^\s*(```+|~~~+)\s*([\w-]*)')
LIST_ITEM = re.compile(r'^(\s*)([-*+]|\d+[.)])\s+(.*)$')
TABLE_SEP = re.compile(r'^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$')
COMMENT = re.compile(r'^\s*<!--.*?-->\s*$')
DETAILS_OPEN = re.compile(r'^\s*<details(\s+open)?>\s*$', re.I)
DETAILS_CLOSE = re.compile(r'^\s*</details>\s*$', re.I)
SUMMARY = re.compile(r'^\s*<summary>(.*?)</summary>\s*$', re.I)


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def plain(s):
    """Heading text without markup, for ids."""
    s = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', s)
    return re.sub(r'[*_`~]', '', s).strip()


def slugify(text):
    """GitHub-style heading id: lower case, punctuation dropped, spaces to hyphens."""
    t = plain(text).lower()
    t = re.sub(r'[^\w\- ]', '', t, flags=re.UNICODE)
    return t.replace(' ', '-')


class Renderer:
    def __init__(self, ctx=None):
        self.ctx = ctx or {}
        self.prefix = self.ctx.get('prefix', '')
        self.seen = {}
        self.headings = []      # (level, text, id)
        self.title = ''
        self.in_banner = False

    # ---------- inline ----------
    def inline(self, s, br=False):
        keep = []

        def hold(html):
            keep.append(html)
            return '\x00%d\x00' % (len(keep) - 1)

        s = re.sub(r'\\([\\`*_{}\[\]()#+\-.!|<>~])', lambda m: hold(esc(m.group(1))), s)
        s = re.sub(r'(`+)(.+?)\1', lambda m: hold('<code>' + esc(m.group(2).strip()) + '</code>'), s)

        def image(m):
            alt, src = m.group(1), m.group(2)
            uri = self.ctx.get('image', lambda a, b: None)(src, alt)
            return hold('<img src="%s" alt="%s" loading="lazy">' % (uri, esc(alt))) if uri else hold('<em class="noimg">[' + esc(alt or src) + ']</em>')
        s = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)', image, s)

        def link(m):
            label, href = m.group(1), m.group(2).strip()
            a, z = self.anchor(href)
            return hold(a) + label + hold(z)
        s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)', link, s)
        s = re.sub(r'<(https?://[^>\s]+)>', lambda m: hold(self.anchor(m.group(1))[0]) + hold(esc(m.group(1))) + hold('</a>'), s)

        s = esc(s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<![\w_])__(.+?)__(?![\w_])', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])', r'<em>\1</em>', s)
        s = re.sub(r'(?<![\w_])_(?![\s_])(.+?)(?<![\s_])_(?![\w_])', r'<em>\1</em>', s)
        s = re.sub(r'~~(.+?)~~', r'<del>\1</del>', s)
        s = re.sub(r'&lt;(/?)(' + '|'.join(ALLOWED_TAGS) + r')\s*/?&gt;', lambda m: '<' + m.group(1) + m.group(2).lower() + '>', s, flags=re.I)
        if br:
            s = s.replace('\n', '<br>')
        s = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], s)
        return s

    def anchor(self, href):
        """-> (opening tag, closing tag) for a link to href."""
        if href.startswith('#'):
            return '<a href="#%s%s">' % (self.prefix, esc(href[1:])), '</a>'
        if re.match(r'^(https?:|mailto:)', href, re.I):
            return '<a href="%s" target="_blank" rel="noopener noreferrer">' % esc(href), '</a>'
        if re.match(r'^[a-z][a-z0-9+.-]*:', href, re.I):   # javascript:, data:, file: ... never
            return '<span class="deadlink">', '</span>'
        kind, val = self.ctx.get('link', lambda h: ('text', None))(href)
        if kind == 'go':
            return '<a href="#" data-go="%s">' % esc(val), '</a>'
        if kind == 'href':
            return '<a href="%s" target="_blank" rel="noopener">' % esc(val), '</a>'
        return '<span class="deadlink" title="%s">' % esc(href), '</span>'

    # ---------- blocks ----------
    def heading_id(self, text):
        base = slugify(text) or 'section'
        n = self.seen.get(base, 0)
        self.seen[base] = n + 1
        return self.prefix + (base if n == 0 else '%s-%d' % (base, n))

    def render(self, text):
        text = re.sub(r'<!-- toc -->.*?<!-- /toc -->', '', text, flags=re.S)
        lines = text.replace('\r\n', '\n').replace('\t', '    ').split('\n')
        return self.blocks(lines)

    def starts_block(self, lines, i):
        l = lines[i]
        return bool(not l.strip() or FENCE.match(l) or HEADING.match(l) or HR.match(l) or l.lstrip().startswith('>')
                    or LIST_ITEM.match(l) or COMMENT.match(l) or DETAILS_OPEN.match(l) or DETAILS_CLOSE.match(l) or SUMMARY.match(l)
                    or (l.lstrip().startswith('|') and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1])))

    def blocks(self, lines):
        out, i, n = [], 0, len(lines)
        while i < n:
            l = lines[i]
            if not l.strip():
                i += 1; continue
            if COMMENT.match(l):
                if 'audience-banner:end' in l: self.in_banner = True
                if '/audience-banner' in l: self.in_banner = False
                i += 1; continue
            m = FENCE.match(l)
            if m:
                fence, lang = m.group(1), m.group(2).lower()
                i += 1; code = []
                while i < n and not lines[i].strip().startswith(fence[:3]):
                    code.append(lines[i]); i += 1
                i += 1
                body = '\n'.join(code)
                if lang == 'mermaid' and 'diagram' in self.ctx:
                    out.append(self.ctx['diagram'](body))
                else:
                    out.append('<pre><code>%s</code></pre>' % esc(body))
                continue
            m = HEADING.match(l)
            if m:
                level, txt = len(m.group(1)), m.group(2)
                hid = self.heading_id(txt)
                if level == 1 and not self.title:
                    self.title = plain(txt)
                if level in (2, 3):
                    self.headings.append((level, plain(txt), hid))
                out.append('<h%d id="%s">%s</h%d>' % (level, hid, self.inline(txt), level))
                i += 1; continue
            if HR.match(l):
                out.append('<hr>'); i += 1; continue
            if DETAILS_OPEN.match(l):
                out.append('<details%s>' % (' open' if 'open' in l.lower() else '')); i += 1; continue
            if DETAILS_CLOSE.match(l):
                out.append('</details>'); i += 1; continue
            m = SUMMARY.match(l)
            if m:
                out.append('<summary>%s</summary>' % self.inline(m.group(1))); i += 1; continue
            if l.lstrip().startswith('|') and i + 1 < n and TABLE_SEP.match(lines[i + 1]):
                i = self.table(lines, i, out); continue
            if l.lstrip().startswith('>'):
                inner = []
                while i < n and lines[i].lstrip().startswith('>'):
                    inner.append(re.sub(r'^\s*>\s?', '', lines[i])); i += 1
                first = next((x for x in inner if x.strip()), '')
                sub = Renderer(self.ctx)
                sub.prefix, sub.seen, sub.in_banner = self.prefix, self.seen, self.in_banner
                cls = 'audience' if self.in_banner else ('callout' if '⚠' in first else '')
                body = sub.blocks_br(inner) if cls == 'callout' else sub.blocks(inner)
                out.append('<blockquote%s>%s</blockquote>' % (' class="%s"' % cls if cls else '', body))
                continue
            if LIST_ITEM.match(l):
                i = self.list_block(lines, i, out); continue
            para = [l.strip()]
            i += 1
            while i < n and not self.starts_block(lines, i):
                para.append(lines[i].strip()); i += 1
            out.append('<p>%s</p>' % self.inline('\n'.join(para).replace('  \n', '<br>\n').replace('\\\n', '<br>\n')))
        return '\n'.join(out)

    def blocks_br(self, lines):
        """Like blocks(), but a line break inside a paragraph stays a line break (the Tricky-part box reads better so)."""
        html = self.blocks(lines)
        return re.sub(r'<p>.*?</p>', lambda m: m.group(0).replace('\n', '<br>'), html, flags=re.S)

    def table(self, lines, i, out):
        def cells(row):
            row = row.strip()
            if row.startswith('|'): row = row[1:]
            if row.endswith('|') and not row.endswith('\\|'): row = row[:-1]
            return [c.strip().replace('\\|', '|') for c in re.split(r'(?<!\\)\|', row)]
        head = cells(lines[i])
        aligns = []
        for c in cells(lines[i + 1]):
            aligns.append('center' if c.startswith(':') and c.endswith(':') else 'right' if c.endswith(':') else '')
        i += 2
        body = []
        while i < len(lines) and lines[i].strip() and '|' in lines[i]:
            body.append(cells(lines[i])); i += 1

        def cell(tag, txt, k):
            a = aligns[k] if k < len(aligns) and aligns[k] else ''
            return '<%s%s>%s</%s>' % (tag, ' style="text-align:%s"' % a if a else '', self.inline(txt), tag)
        h = ''.join(cell('th', c, k) for k, c in enumerate(head))
        rows = ''.join('<tr>' + ''.join(cell('td', c, k) for k, c in enumerate(r)) + '</tr>' for r in body)
        out.append('<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, rows))
        return i

    def list_block(self, lines, i, out):
        n = len(lines)
        items = []   # dict(indent, ordered, start, text)
        while i < n:
            l = lines[i]
            m = LIST_ITEM.match(l)
            if m:
                ordered = m.group(2)[0].isdigit()
                if items and len(m.group(1)) <= items[0]['indent'] and ordered != items[0]['ordered']:
                    break   # a bullet list followed by a numbered one (or the reverse) is two lists
                items.append({'indent': len(m.group(1)), 'ordered': ordered, 'start': int(re.match(r'\d+', m.group(2)).group(0)) if ordered else 1,
                              'text': [m.group(3)], 'kids': []})
                i += 1; continue
            if not l.strip():
                j = i
                while j < n and not lines[j].strip(): j += 1
                if j < n and (LIST_ITEM.match(lines[j]) or (lines[j].startswith('  ') and items)):
                    i = j; continue
                break
            if l.startswith(' ') and items and not HR.match(l):
                items[-1]['text'].append(l.strip()); i += 1; continue
            break

        def build(seq, base):
            """nest the flat items by indent"""
            tree = []
            for it in seq:
                if tree and it['indent'] > tree[-1]['indent']:
                    tree[-1]['kids'].append(it)
                else:
                    tree.append(it)
            return tree

        def emit(nodes):
            if not nodes: return ''
            tag = 'ol' if nodes[0]['ordered'] else 'ul'
            start = ' start="%d"' % nodes[0]['start'] if tag == 'ol' and nodes[0]['start'] != 1 else ''
            lis = ''
            for nd in nodes:
                kids = build(nd['kids'], nd['indent'])
                lis += '<li>%s%s</li>' % (self.inline(' '.join(nd['text'])), emit(kids))
            return '<%s%s>%s</%s>' % (tag, start, lis, tag)
        out.append(emit(build(items, 0)))
        return i


def render(text, ctx=None):
    """-> (html, title, headings) ; headings is a list of (level, text, id) for levels 2 and 3."""
    r = Renderer(ctx)
    html = r.render(text)
    return html, r.title, r.headings
