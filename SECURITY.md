# Security policy

`study-guide-tutor` is a set of Markdown guidance files, Python helper scripts and two agent prompts. It has no hooks and makes no network calls. The scripts read the folder you point them at and write only generated study files (and, for `source_text.py`, a text cache beside your source).

## Reporting a vulnerability

Please **do not open a public issue** for a security problem. Use the repository's private vulnerability reporting ("Report a vulnerability" under the Security tab). Include the file, the command or input that triggers it, what you expected, what happened, and your platform.

You can expect an acknowledgement within a few days and a fix or a written assessment within 30 days. Credit is given in the changelog unless you prefer otherwise.

## In scope

- a script that deletes, overwrites or moves files outside the course folder it was given;
- a script that runs input from a study file (a filename, a chapter title, a PDF's text) as code or as a shell command;
- Mermaid or PDF handling that can be made to execute attacker-controlled content (`make_glance.py` calls `mmdc` when installed; `source_text.py` calls `pdftotext` when installed);
- personal data or secrets accidentally contained in the repository.

## Out of scope

- the content of the guidance (a rule you disagree with): open a normal issue;
- vulnerabilities in third-party tools the scripts can call (`pdftotext`, `mermaid-cli`, a PDF library): report them upstream;
- findings that need an attacker who already controls your shell.

## Notes for users

- Study material you extract may contain text copied from a PDF; the scripts treat it as data. Still, open untrusted PDFs in a sandbox.
- A generated course can contain copyrighted lecture text in its fact ledger and cache. Keep it private unless you have the right to share it.
