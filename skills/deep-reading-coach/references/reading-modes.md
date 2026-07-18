# Reading Modes

## Contents

1. Mode selection
2. Relationship between modes and phases
3. Guided reading
4. Reading-note review
5. Whole-book map
6. Whole-book integration

## 1. Mode Selection

Select one mode from the user's material and intent. If the user names a mode, use it directly.

- Guided reading: the user has just read a chapter, has incomplete notes, or wants understanding checked step by step.
- Reading-note review: the user supplies their own notes and wants accuracy, omissions, structural gaps, external claims, or personal judgments checked.
- Whole-book map: the user supplies a complete book and wants its central problem, architecture, argument route, and reading priorities after complete body inspection.
- Whole-book integration: the user has read multiple chapters or supplied multiple notes and wants a coherent knowledge system.

State the chosen mode and evidence briefly. Do not force all modes into one response.

## 2. Relationship Between Modes and Phases

Modes describe the interaction format; phases describe the evidence goal. They are not a single sequence.

- Whole-book map belongs to Phase 1 source reconstruction and may be output only after every readable body unit has been actually inspected.
- Guided reading can reconstruct a chapter in Phase 1, verify a selected claim in Phase 2, or test transfer in Phase 3.
- Reading-note review uses notes as navigation: source summaries route to Phase 1, external claims to Phase 2, and personal judgments or applications to Phase 3.
- Whole-book integration normally belongs to Phase 3, but complete any necessary claim verification under Phase 2 before incorporating it.

State both only when the distinction helps: for example, `当前模式：带读；当前阶段：原书重建`. Do not make users complete every mode or every phase.

## 3. Guided Reading

If the user has not summarized the chapter, first ask them to explain in their own words:

- what the chapter discusses;
- what problem it solves;
- which concept matters most;
- what remains difficult.

Ask only one main question in the current turn. Do not provide a chapter summary first.

Then:

1. Check the problem the author addresses.
2. Check why the concept or method is needed.
3. Check how the conclusion or procedure follows.
4. Test a changed condition, counterexample, or new application.
5. After understanding is established, build the chapter model: central problem, most important idea, likely misunderstanding, recurring concept, rereading target, and role in the book.

## 4. Reading-Note Review

Preserve the user's original path. Do not rewrite, polish, or complete the notes unless explicitly requested.

Choose the evidence route first:

- Book plus notes: inspect both. Diagnose the notes first, then use them to target source checks. Do not require a new whole-book map when the notes already provide a usable structure.
- Notes only: allow a provisional review of structure, reasoning, uncertainty, and learning gaps. Mark claims about what the author said as `【无法确认】` unless the notes contain a verifiable quotation or supplied locator. Request only the necessary chapter or excerpt, not the whole book.

Treat notes as a navigation and diagnosis layer, not automatic proof of the book. Classify note material without rewriting it:

- source summary or quotation → Phase 1 reconstruction or checking;
- outside study, current fact, or comparison → Phase 2 verification when authorized;
- personal judgment, application, counterexample, or open question → Phase 3 integration.

First identify:

- the core problem already captured;
- understood concepts and causal links;
- cross-chapter connections;
- personal judgments and applications;
- uncertainties that should remain visible.

Classify issues:

- understood but concise;
- conclusion remembered without reason;
- missing relationship between concepts;
- explicit misunderstanding;
- important content absent but not yet confirmed missing from understanding;
- safe to defer;
- ambiguity or weakness in the book itself.

Initial review output uses exactly four sections:

1. `材料与证据范围` — note whether the book is present and what can or cannot be checked
2. `我已经理解的内容`
3. `关键缺口与可保留问题` — one to three consequential items only
4. `当前诊断问题` — exactly one question

Before treating an omitted note item as missing understanding, ask whether the user can explain it.

## 5. Whole-Book Map

Inspect every readable `body` unit in source order before producing a whole-book map. Extraction, a table of contents, an introduction, chapter openings, a conclusion, selected chapters, or any other sample is insufficient. Use the table of contents for navigation only. Keep an internal coverage ledger for long books.

Before full-body inspection completes, output only the material report and any necessary reading-status or blocking notice. Do not provide a provisional structure, problem awareness, core question, core claims, or argument route.

After complete body inspection, output exactly:

1. `文件读取情况`
2. `书籍基本信息`
3. `全书结构`
4. `作者的问题意识`
5. `作者试图回答的核心问题`
6. `全书论证路线`
7. `建议重点精读或重新阅读的章节`
8. `一个需要我先思考的问题`

Build the map around the actual book rather than a fixed number of points. Identify:

- the observed problem and shortcomings of prior explanations or methods;
- the main question and subordinate questions;
- the central conclusion or capability target;
- the progression from problem through concepts and evidence to conclusion, application, and limits;
- each section's function;
- the reason the problem matters to the author;
- chapters to read closely or revisit later.

If any substantive body unit is unreadable or missing, do not issue the eight-section response as a complete whole-book analysis. State the limitation and smallest next action.

## 6. Whole-Book Integration

Do not concatenate chapter summaries. Analyze:

- development of the central question;
- changing definitions or uses of recurring concepts;
- later corrections to earlier models;
- prerequisite, extension, application, and limitation relationships between chapters;
- contradictions across the user's notes;
- missing bridge concepts.

After complete whole-book Phase 1 reconstruction, output:

1. 作者模型：问题主线、概念发展和章节关系
2. 领域位置：已核实的思想谱系、竞争解释和争议
3. 我的判断：依据、保留意见和适用边界
4. 迁移地图：写作、生活观察、工作与人际、自我反思、跨书联系
5. 尚未解决的关键问题
6. 最值得重新阅读的章节

Assess all five transfer domains, deepen only the genuinely useful ones, and follow [perspective-transfer.md](perspective-transfer.md). End with one question or one next action, not both.
