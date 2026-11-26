---
name: doc-writer
description: Write or change a theory, architecture, design or verification-and-validation document so that it follows the documentation standards, ASD-STE100 and the PDF layout, then build and check the rendered output. Use whenever you create, move or edit a file under the documentation folder.
---

Write one document, or change one. AGENTS.md *Documentation* has the rules. This skill adds the standards,
the page layout and the checks. A repository rule in *Domain* or *Exceptions* overrides this skill.

## Standards

| Document kind               | Folder                         | Standard that sets its content                                  |
|-----------------------------|--------------------------------|-----------------------------------------------------------------|
| All                         | —                              | ISO/IEC/IEEE 15289 (information items), ASD-STE100 (language)   |
| Theory                      | `theory/`                      | —                                                               |
| Architecture                | `architecture/`                | ISO/IEC/IEEE 42010 (views, including the deployment view)       |
| Component design            | `design/`                      | IEEE 1016 (design viewpoints)                                   |
| Test plan, test design      | `verification_and_validation/` | ISO/IEC/IEEE 29119-3 (test documentation)                       |
| Requirements                | `verification_and_validation/` | ISO/IEC/IEEE 29148 (one `shall` per requirement, no solution)   |

Apply the content each standard asks for. Do not copy its clause structure when the template has its own.

A toolbox keeps a reference library instead: one `doc/<domain>/<Name>.md` per algorithm, from its `TEMPLATE.md`.
A reference document names the API it documents and has no front matter. *Language* and the no-Open-Questions rule
apply to it; the design rules do not.

## Steps

1. Find the document kind. Choose the folder from the table. A test strategy goes to
   `verification_and_validation/`, never to `design/`.
2. Check that the material does not belong to an existing document. If it does, change that document.
3. Create the file from its template in the templates folder. Keep the template's `##` headings exactly.
4. Write the front matter: `title`, `type`, `status`, `version`, `date`, and the fields the template adds.
5. Write the body. Obey *Content* and *Language* below.
6. Add the document to the index that the PDF build reads.
7. Run `python3 .claude/skills/doc-writer/doc_lint.py .`. Fix each error. Shorten each sentence it warns about
   in the text you changed. CI runs the same check (`verify` with the `docs` bundle).
8. Build the PDFs and check them with *Render check*. Fix each failure, then build again.
9. Report changed files, lint and build pass/fail, and each render-check failure that you could not fix.

A term that the lint reports but that is correct (for example a wire-contract message name) goes on its own line
in `<docs>/.doc-lint-allow`. Do not add a class, function or file name to it.

## Content

- Design: describe the component, not the code or the hardware. No MCU, board, vendor peripheral, register,
  clock frequency, class, function, method or file name. Use the component's own words: "the duty cycles",
  not the type that holds them; "the power stage", not the timer peripheral.
- Use "the target" for the processor. Use "on the reference board" for a measured figure.
- Architecture: the deployment view names the target family. Keep part numbers in the build documentation.
- `## Responsibilities` is the first section of a design document. It has one list. Do not add a
  "not responsible for" list. Put what the component needs from others in *Interfaces* (Required).
- No "Open Questions", "TBD" or "Future work" section. Record decisions in `## Decisions`: one row per decision
  with the options considered, the status and the rationale. A row that is still open links its issue.
  Put a known limitation in *Constraints & Limitations*.
- No source code. Express behaviour with Mermaid (`flowchart`, `stateDiagram-v2`, `sequenceDiagram`),
  ASCII, or the other visuals that AGENTS.md *Exceptions* allows.
- Keep each table cell short. Put a long explanation in prose under the table. Put no long inline code
  in a cell: it does not wrap.

## Language (ASD-STE100)

- One word, one meaning. Use the same term for the same thing in all documents.
- Active voice. Present tense for behaviour.
- One instruction per sentence. One topic per paragraph.
- Sentences: ≤ 20 words in a procedure, ≤ 25 words in a description. Paragraphs: ≤ 6 sentences.
- Use articles ("the", "a"). Do not omit them to make the text shorter.
- Write a procedure as a numbered list, one action per step.

## Page layout

Every PDF, the complete booklet and each document, opens with this front matter, two-sided:

1. Title page: title, author, date (and version and status for a document).
2. Blank page.
3. Contents.
4. Blank page.
5. Body, from a right-hand page.

The metadata table and template notes after the front matter are for readers of the source. The PDF omits them.

## Render check

Open the built PDF and do these checks on each page the change touches:

1. Each Mermaid diagram shows as a figure, not as code. Flowchart and state labels show their text.
2. Each sequence diagram shows all participants and messages. No label is cut off.
3. Each image shows. No image is missing, blank or larger than the page.
4. No table column runs into the next. No text runs past the page margin.
5. The front matter has the five pages in the order above.
6. The contents list each `##` heading of the document.

A diagram that does not parse fails the build. Do not mark a check as done that you did not see in the PDF.
If you cannot build the PDF, say so in the report.
