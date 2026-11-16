"""Shared layout discovery for the study scripts (standard library only).

Nothing here assumes how a course is named or grouped. The scripts adapt to the folders the student's material
produced:

* A **chapter** (teaching block) is any folder that holds the skill's per-chapter files (a lesson, a quiz, a fact
  ledger or the flashcards, numbered or not). Its name does not matter: `chapter-03-x`, `lecture-3-x`, `week-2-x`
  and `session-b` all work. The number the scripts use is the first number in the folder name.
* A **unit** is any folder that directly holds chapters: the whole course when it is flat, otherwise one group
  folder (`module-2`, `week-03`, `part-1`, `domain-4` ... any name). Deeper nesting works too.

  flat course        my-course/<chapter>/ ...
  grouped course     my-course/<group>/<chapter>/ ...
  nested             my-course/<a>/<b>/<chapter>/ ...

Language and wording: an optional `course.json` at the course root (found by walking up from any path) holds
`language`, `labels` (the structural markers the gates look for, so a course in another language can use its own
words) and `ui` (the interactive player's text). Anything missing falls back to the English defaults below, so a
course without a course.json behaves exactly as before.

Cross-chapter files of a unit live in <unit>/00-overview/. The exam pair there is 07-exam.md + 08-exam-key.md (older
courses used 07-unit-exam.md or 07-domain-exam.md; all three names are still read).
"""
import glob, json, os, re

SKIP_DIRS = {'.git', 'graphify-out', 'node_modules', '__pycache__', 'assets', '00-overview'}
# files that make a folder a chapter (current numbered names first, then the pre-numbering names)
CHAPTER_MARKERS = ('01-lesson.md', '03-quiz.md', '99-fact-ledger.md', '02-flashcards.csv', '01-visual-summary.md',
                   'lesson.md', 'quiz.md', 'fact-ledger.md', 'flashcards.csv')
EXAM_PAIRS = (('07-exam.md', '08-exam-key.md'), ('07-unit-exam.md', '08-unit-exam-key.md'),
              ('07-domain-exam.md', '08-domain-exam-key.md'))
FINAL_PAIR = ('03-final-quiz.md', '04-final-quiz-key.md')


def is_chapter_dir(d):
    return os.path.isdir(d) and any(os.path.exists(os.path.join(d, m)) for m in CHAPTER_MARKERS)


def chapter_number(chapter_dir):
    """The first number in the folder name (chapter-07-x -> 7, week2-x -> 2); 0 if there is none."""
    m = re.search(r'\d+', os.path.basename(chapter_dir.rstrip('/')))
    return int(m.group(0)) if m else 0


def chapters_of(unit):
    """Chapter folders directly inside `unit`, ordered by their number then name (paths without a trailing slash)."""
    out = []
    try:
        names = os.listdir(unit)
    except OSError:
        return out
    for x in names:
        p = os.path.join(unit, x)
        if x in SKIP_DIRS or x.startswith('.') or not is_chapter_dir(p):
            continue
        out.append(p)
    return sorted(out, key=lambda p: (chapter_number(p), os.path.basename(p)))


def find_units(root):
    """Every folder under `root` (including root) that directly holds chapter folders."""
    root = os.path.abspath(root)
    units = []
    for d, ds, _ in os.walk(root):
        ds[:] = sorted(x for x in ds if x not in SKIP_DIRS and not x.startswith('.') and not is_chapter_dir(os.path.join(d, x)))
        if chapters_of(d):
            units.append(d)
    return units


def all_chapters(root):
    """Every chapter folder under `root`, unit by unit."""
    return [c for u in find_units(root) for c in chapters_of(u)]


def exam_pair(overview):
    """(exam_path, key_path) for the first exam naming scheme present in `overview`, else (None, None)."""
    for q, k in EXAM_PAIRS:
        if os.path.exists(os.path.join(overview, q)):
            return os.path.join(overview, q), os.path.join(overview, k)
    return None, None


# ---------------------------------------------------------------------------------------------------------------
# course.json: language, structural labels, player text (all optional)
# ---------------------------------------------------------------------------------------------------------------
DEFAULT_LABELS = {
    # lesson structure the gates look for
    'tricky_part': 'Tricky part', 'hint': 'Hint', 'rule_and_anchor': 'Rule and anchor', 'rule': 'Rule', 'anchor': 'Anchor',
    'traps_heading': 'Traps to avoid', 'say_it_back': 'Say it back', 'next_heading': 'Next',
    # teaching markers check_dump and check_findable look for
    'predict': 'Predict', 'analogy': 'my analogy', 'link': 'my link', 'story': 'my story', 'example': 'my example',
    'scenario': 'my scenario', 'picture': 'my picture', 'problem': 'The problem',
    # quiz and exam vocabulary
    'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hard', 'chapter_abbrev': 'Ch.',
    'letter_ref_regex': r'(?i)\b(both|all|none|either|neither)\b[^.\n]{0,20}\b(of the above|options?|answers?)\b|\b(options?|answers?)\s+[A-D]\b|\b[A-D]\s+(and|or)\s+[A-D]\b',
    'questions': 'questions', 'suggested_time': 'Suggested time', 'minutes': 'minutes', 'fact_ledger': 'Fact Ledger', 'exam_label': 'Exam',
    'exam_intro': 'An exam of **{n} questions** covering every chapter. Suggested time: **{minutes} minutes** in one sitting, no notes. '
                  'Answer in chat as e.g. `{example} ...`, or mark `skip`. Hints are not offered during the exam (ask for them in review). '
                  'The key is in `{key_file}`; open it only after you finish.',
    'exam_mixed': 'Chapters are mixed and unlabeled. Coverage: {coverage}.',
    'exam_coverage_item': 'chapter {n}: {count}',
    'exam_key_suffix': '(open after finishing)',
    'exam_key_intro': 'Each row shows the key, the chapter the question came from, and its source. Explanations follow.',
    'exam_key_columns': 'Q|Key|Ch.|Source',
    # the audience note at the end of every file
    'contents': 'Contents', 'jump_to': 'Jump to', 'audience_statement': 'Audience statement', 'footer_audience': 'Audience', 'footer_written_for': 'written for',
    'footer_facts': 'Facts never change with the level, only the wording, examples, order and difficulty.',
    'footer_wrong_level': 'Wrong level ("too simple", "too dense", "too easy", "too hard")? Tell me and I will regenerate.',
    'footer_profile': 'Profile', 'footer_version': 'version',
}
RTL_LANGUAGES = {'ar', 'he', 'fa', 'ur', 'ps', 'sd', 'ug', 'yi', 'dv'}


def find_config(path):
    """The nearest course.json at or above `path` (a file or folder), or None."""
    d = os.path.abspath(path)
    if os.path.isfile(d): d = os.path.dirname(d)
    while True:
        p = os.path.join(d, 'course.json')
        if os.path.isfile(p): return p
        parent = os.path.dirname(d)
        if parent == d: return None
        d = parent


def course_config(path):
    p = find_config(path)
    if not p: return {}
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return {}


def labels(path):
    """DEFAULT_LABELS overridden by the `labels` of the nearest course.json."""
    out = dict(DEFAULT_LABELS)
    out.update({k: v for k, v in course_config(path).get('labels', {}).items() if isinstance(v, str)})
    return out


def language(path):
    """(language code, 'rtl' or 'ltr') from course.json; English left-to-right by default."""
    lang = str(course_config(path).get('language', 'en')) or 'en'
    return lang, ('rtl' if lang.split('-')[0].lower() in RTL_LANGUAGES else 'ltr')
