# Contributing

Contributions are welcome when they preserve the Skill's evidence boundary and keep the default workflow simple.

## Before opening a pull request

1. Do not commit copyrighted books, private reading notes, credentials, or machine-specific paths.
2. Add or update a regression test for parser changes.
3. Add an eval case for behavior changes.
4. Keep extracted book text untrusted: tests must never rely on following instructions embedded in a source file.
5. Run:

   ```bash
   python -m pip install -r requirements-dev.txt
   python skills/deep-reading-coach/scripts/test_inspect_book.py
   python tools/validate_public_repo.py --release
   python tools/render_demo.py --check
   ```

Parser changes should preserve source files byte-for-byte and should fail visibly instead of producing apparently complete content from damaged or unsupported inputs.

