#!/usr/bin/env python3
"""The student's notes file: `06-notes.md` beside a chapter's lesson (standard library only).

The notes are the student's own words, so the Markdown file is their source of truth, like the lesson and the quiz
are for what the tutor wrote. The study player reads it when it is built and writes it back (straight into the
folder in browsers that allow it, or as a download). The tutor reads it when it reviews the student's progress.

Format, one block per note, in lesson order. Hand-written notes work too: only the "> quote" line is needed, because
the quote is how a note finds its place in the lesson.

    # Notes: Ch. 1 The four stages

    <!-- study-notes: ... -->

    ## Note 1: 1. What happens to the puddle when the sun comes out?

    > puddle in a school yard tells the st

    Why does the loop never stop?

    <!-- note {"id":"n1a2b","start":4,"end":40,"prefix":"One ","suffix":"ory: the","ts":1763000000000} -->

The player (assets/player.html) has the same two functions in JavaScript, with the same output; the self-test
compares them. The content hash is FNV-1a over the UTF-8 bytes, so both sides can tell whether the file changed.
"""
import json, re

FILE = '06-notes.md'
INTRO = ('<!-- study-notes: written by the study player and read back by it. Edit it by hand if you like. '
         'Keep each note\'s "> quote" line: it is how the note finds its place in the lesson. -->')
META_KEYS = ('id', 'start', 'end', 'prefix', 'suffix', 'ts')


def fnv(text):
    """FNV-1a (32 bit) of the UTF-8 bytes, as 8 hex digits. The player computes the same value."""
    h = 0x811c9dc5
    for b in text.encode('utf-8'):
        h = ((h ^ b) * 0x01000193) & 0xffffffff
    return '%08x' % h


def _meta(note):
    s = json.dumps({k: note.get(k) for k in META_KEYS if note.get(k) is not None}, separators=(',', ':'), ensure_ascii=False)
    return s.replace('--', '-\\u002d')


def _escape(line):
    return '\\' + line if re.match(r'^(#|>)', line) else line


def _unescape(line):
    return line[1:] if re.match(r'^\\(#|>)', line) else line


def render(title, notes):
    """-> the notes file text for these notes (sorted by position in the lesson)."""
    out = ['# ' + title, '', INTRO, '']
    for i, n in enumerate(sorted(notes, key=lambda x: (x.get('start') or 0, x.get('ts') or 0)), 1):
        out.append('## Note %d%s' % (i, ': ' + n['sec'] if n.get('sec') else ''))
        out += ['', '> ' + re.sub(r'\s+', ' ', n['quote']).strip(), '']
        if (n.get('note') or '').strip():
            out += [_escape(l) for l in n['note'].strip().split('\n')] + ['']
        out += ['<!-- note %s -->' % _meta(n), '']
    return '\n'.join(out)


def parse(text):
    """-> list of notes (dicts with id, quote, note, sec, start, end, prefix, suffix, ts) found in a notes file."""
    notes = []
    for part in re.split(r'(?m)^## ', text.replace('\r\n', '\n'))[1:]:
        head, _, body = part.partition('\n')
        meta = {}
        m = re.search(r'<!--\s*note\s+(\{.*?\})\s*-->', body, re.S)
        if m:
            try:
                meta = json.loads(m.group(1))
            except ValueError:
                meta = {}
            body = body.replace(m.group(0), '')
        quote, rest = [], []
        for l in body.split('\n'):
            (quote if l.startswith('>') else rest).append(l)
        q = re.sub(r'\s+', ' ', ' '.join(re.sub(r'^>\s?', '', l) for l in quote)).strip()
        if not q:
            continue
        sec = re.match(r'Note\s+\d+\s*:\s*(.+)$', head.strip())
        n = {'id': meta.get('id') or 'h' + fnv(q), 'quote': q, 'note': '\n'.join(_unescape(l) for l in rest).strip(),
             'sec': sec.group(1).strip() if sec else '', 'start': meta.get('start', 0), 'end': meta.get('end', 0),
             'prefix': meta.get('prefix', ''), 'suffix': meta.get('suffix', ''), 'ts': meta.get('ts', 0)}
        notes.append(n)
    return notes
