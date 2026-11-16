#!/usr/bin/env python3
"""Unit tests for the lesson renderer (scripts/_md.py): structure, safety and the lesson-specific boxes. No browser needed."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'skills', 'study-guide-tutor-skill', 'scripts'))
import _md

fails = []


def check(name, cond):
    print(('ok   ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)


def R(text, **ctx):
    return _md.render(text, ctx)


h, title, heads = R('# Title\n\n## Contents\n\n### Sub *one*\n\n## Contents\n')
check('headings get ids, h1 is the title', title == 'Title' and '<h2 id="contents">' in h and '<h3 id="sub-one">' in h)
check('duplicate headings get unique ids', 'id="contents-1"' in h)
check('only h2/h3 go to the contents list', [x[0] for x in heads] == [2, 3, 2])
check('prefix on ids', 'id="l9-contents"' in R('## Contents', prefix='l9-')[0])

h = R('| A | B |\n|---|:-:|\n| 1 \\| x | **2** |\n')[0]
check('table with escaped pipe, bold and alignment',
      '<th>A</th>' in h and 'text-align:center' in h and '1 | x' in h and '<strong>2</strong>' in h and 'tablewrap' in h)

h = R('- one\n  - nested\n- two\n\n1. first\n2. second\n')[0]
check('nested and ordered lists',
      '<ul><li>one<ul><li>nested</li></ul></li><li>two</li></ul>' in h and '<ol><li>first</li><li>second</li></ol>' in h)

h = R('> **⚠ Tricky part: x**\n> Both swap.\n> **Hint:** look.\n')[0]
check('tricky part becomes a callout with line breaks', 'class="callout"' in h and '<br>' in h)
h = R('<!-- audience-banner:end -->\n> **Audience:** for you\n<!-- /audience-banner -->\n')[0]
check('audience note recognised', 'class="audience"' in h)
check('plain quote stays plain', '<blockquote><p>' in R('> hello\n')[0])

h = R('<details>\n<summary><b>Predict:</b> q?</summary>\n\nanswer\n</details>\n')[0]
check('details and summary kept, html in summary limited to safe tags',
      '<details>' in h and '<summary><b>Predict:</b> q?</summary>' in h and '<p>answer</p>' in h and '</details>' in h)

h = R('<script>alert(1)</script>\n\ntext <img src=x onerror=y> <b onclick=z>x</b> `<i>`')[0]
check('raw script and attributes are escaped', '<script' not in h and '<img' not in h and '<b onclick' not in h)
check('javascript: links are dead',
      'href="javascript' not in R('[x](javascript:alert(1))')[0] and 'deadlink' in R('[x](javascript:alert(1))')[0])
check('external links open safely', 'rel="noopener noreferrer"' in R('[x](https://example.com)')[0])
check('code span keeps markup literal', '<code>&lt;i&gt;</code>' in R('`<i>`')[0])
check('snake_case is not italic', '<em>' not in R('use snake_case_name here')[0])
check('emphasis and strong', '<em>a</em>' in R('*a*')[0] and '<strong>b</strong>' in R('**b**')[0])

h = R('```mermaid\nflowchart LR\nA-->B\n```\n\n```python\nx = "<1>"\n```\n',
      diagram=lambda c: '<div class="diagram">%s</div>' % c.split('\n')[0])[0]
check('mermaid goes to the diagram callback, other fences are code',
      '<div class="diagram">flowchart LR</div>' in h and '<pre><code>x = &quot;&lt;1&gt;&quot;' in h)


def go(href):
    if href == '03-quiz.md':
        return ('go', 'quiz:3')
    return ('href', 'x/' + href) if href.endswith('.md') else ('text', None)


h = R('[quiz](03-quiz.md) [other](a.md) [none](zzz) [jump](#sec)', link=go, prefix='l1-')[0]
check('relative links resolve through the callback, anchors get the prefix',
      'data-go="quiz:3"' in h and 'href="x/a.md"' in h and 'class="deadlink"' in h and 'href="#l1-sec"' in h)

h = R('<!-- toc -->\n## Contents\n\n- [a](#a)\n<!-- /toc -->\n\n## A\n')[0]
check('the generated contents block is dropped (the player builds its own)', 'Contents' not in h and 'id="a"' in h)
check('empty input is fine', R('')[0] == '')
sys.exit(1 if fails else 0)
