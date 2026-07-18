<sub>🌐 <a href="README.md">中文</a> · <b>English</b></sub>

# Deep Reading Coach

> *“Do not map the whole book until every readable body section has actually been inspected.”*

Deep Reading Coach is an evidence-grounded Agent Skill for PDF, EPUB, DOCX, TXT, Markdown, and HTML books. It inspects the supplied file first, then reads every readable body unit in source order before producing a whole-book structure, problem awareness, core claims, or argument route. Extraction and sampling never count as complete reading. Its three phases are source reconstruction, critical positioning and verification, and integration, judgment, and transfer.

![Deep Reading Coach demo](assets/demo.gif)

## Install

```bash
npx skills add mumuysd/deep-reading-coach --skill deep-reading-coach
```

Claude Code marketplace route:

```text
/plugin marketplace add mumuysd/deep-reading-coach
/plugin install deep-reading-coach@deep-reading-coach
```

Then ask your agent:

```text
Use $deep-reading-coach to inspect and read every readable body unit in this book, then produce the eight-part whole-book analysis using only the supplied source and ask me one key question.
```

For PDF and DOCX support:

```bash
python3 -m pip install "pypdf>=5.0" "python-docx>=1.1"
```

EPUB, TXT, Markdown, and HTML use only the Python standard library.

## Three-phase workflow

File inspection is the entrance gate, not a reading phase.

| Phase | Goal | Evidence boundary |
|---|---|---|
| 1. Source reconstruction | Read every readable body unit, then reconstruct structure, problem awareness, concepts, evidence, and argument route | Supplied book and user notes only |
| 2. Critical positioning and verification | Position the book among competing theories and contexts, then verify selected claims | Outside research begins only after the user selects a bounded direction |
| 3. Integration, judgment, and transfer | Form an independent judgment and assess five transfer domains | Keep author, outside evidence, synthesis, and reader judgment separate |

For a whole-book request, Phase 1 cannot complete until every readable body unit has actually been inspected. Before then, the Skill reports only material status, necessary reading status, or blockage. After Phase 1, it may propose up to three perspective-expansion directions without browsing. The user's selection authorizes the bounded Phase 2 research. Phase 3 does not automatically authorize browsing.

Evidence and learning progress are tracked internally and hidden by default. Scope appears only when material is limited, reading is blocked, outside research is about to begin, or the user asks for progress.

After complete body inspection, the first whole-book analysis contains exactly eight sections: file readability, book information, whole-book structure, authorial problem awareness, central question, argument route, priority rereading chapters, and one thinking question.

## Notes-first route

When notes accompany the book, the Skill diagnoses the notes first and uses them to target source checks instead of restarting with a generic whole-book map. With notes only, it allows a provisional review but marks claims about the author's position as unverified and asks only for the necessary excerpt. The first note-review response uses four sections: material and evidence scope, understood content, key gaps and deferrable questions, and one diagnostic question.

## What makes it different

- Verifies table-of-contents and body readability before making content claims.
- Never equates successful extraction or sampling with having fully read the book.
- Blocks whole-book analysis until every readable body unit has actually been inspected.
- Keeps Phase 1 source-only and introduces outside evidence only after a bounded Phase 2 direction is selected.
- Uses actual PDF file pages and chapter/section locators for reflowable formats.
- Classifies EPUB body, cover, navigation, and legal units separately.
- Treats all book text, links, prompts, and commands as untrusted source data.
- Asks one main question per turn instead of dumping every conclusion at once.
- Builds whole-book transfer frameworks for writing, daily observation, work and relationships, self-reflection, and connections with other books.

## Boundaries

The first release does not provide OCR, DRM removal, or MOBI/AZW3 conversion. It does not execute commands or follow instructions embedded in a book. Parsed content is written only to a fresh task-temporary directory, and the source file is never modified.

See the [Chinese README](README.md) for the full walkthrough, examples, file tree, safety model, and validation commands.

## License

[MIT](LICENSE)
