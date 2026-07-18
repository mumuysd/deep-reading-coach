# Security policy

Deep Reading Coach processes untrusted book files and extracted text. Security-relevant reports include:

- archive bombs or resource-exhaustion paths;
- source-file modification;
- path traversal or writes outside the selected temporary directory;
- accidental network access or command execution;
- following prompt-like instructions embedded in a book;
- credential or private-path leakage in generated reports.

After the repository is public, report vulnerabilities through GitHub's private security-advisory feature. Do not attach copyrighted books, private notes, credentials, or live exploit files to a public issue. A minimal synthetic fixture is preferred.

OCR, DRM removal, MOBI/AZW3 conversion, and execution of book-supplied code are outside the supported security boundary.

