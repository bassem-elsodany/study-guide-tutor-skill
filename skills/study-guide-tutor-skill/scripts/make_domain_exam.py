#!/usr/bin/env python3
"""Deprecated name of make_exam.py, kept so older instructions keep working.

Usage: make_domain_exam.py UNIT_DIR [same options as make_exam.py]
Writes the older file names 07-domain-exam.md and 08-domain-exam-key.md. New courses should use make_exam.py,
which writes 07-exam.md and 08-exam-key.md and works for courses with no domains or units at all.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_exam

if __name__ == '__main__':
    sys.argv += ['--kind', 'domain-exam']
    make_exam.main()
