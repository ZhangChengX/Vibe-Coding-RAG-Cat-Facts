# Vibe-Coding-RAG-Cat-Facts

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
A conversational assistant that answers cat lovers' questions with surprising and practical cat facts.

![Screenshot of UI](/screenshot.png)

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | dataset | Plain text | https://huggingface.co/ngxson/demo_simple_rag_py/resolve/main/cat-facts.txt |
| 2 | webpage | Article | https://cvillecatcare.com/veterinary-topics/101-amazing-cat-facts-fun-trivia-about-your-feline-friend/ |
| 3 | webpage | Article | https://www.discoverwildlife.com/animal-facts/mammals/cat-facts |
| 4 | webpage | Article | https://www.bjsrawpetfood.com/blogs/all/fascinating-cat-facts-you-didn-t-know |
| 5 | webpage | Article | https://www.mygavet.com/services/cats/blog/50-cat-facts-you-probably-didnt-know |
| 6 | webpage | Article | https://www.animalfriends.co.uk/cat/cat-blog/cat-facts/ |
| 7 | webpage | Article | https://www.goodhousekeeping.com/life/pets/g69020271/shocking-facts-about-cats-you-never-knew/ |
| 8 | webpage | Article | https://petventuresbook.com/blogs/blog/20-interesting-cat-facts |
| 9 | webpage | Article | https://www.nekocatcafe.com/blog/62-facts-about-cats |
| 10 | webpage | Article | https://www.aaha.org/resources/lets-get-purr-sonal-interesting-facts-about-cats/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** dynamic chunk size by each sentence or paragraph

**Overlap:** no overlap

**Why these choices fit your documents:** on the webpages, each paragraph or sentence is a fact. in cat-facts.txt each sentence is a fact.

**Final chunk count:** 474 chunks across the 10 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:** all-MiniLM-L6-v2 is a good fit for this small cat-facts corpus because it is fast, low-cost, and accurate enough for short factual text.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
You are a helpful assistant for answering questions based on cat facts.
Use only the following retrieved context to answer the question directly.
If the answer isn't in the context, say you don't know instead of making something up.
context: [context]
question: [query]

**How source attribution is surfaced in the response:**
After every generated answer we include a short "Sources" block listing the top retrieved documents used to produce the reply.
If the answer cannot be supported by retrieved context the assistant replies "I don't know" and does not fabricate sources.
In the interface, clicking a response opens an accordion that lists every retrieved context behind it, each shown with its similarity score and source file name. The contexts are stored per-answer so the right sources are shown for whichever response is clicked.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Can cats taste sweets? | No, cats can't taste sweets. | "No, cats can't taste sweets." (top score 0.871, cat-facts.txt) | Relevant | Accurate |
| 2 | How long does a cat pregnant? | A cat is pregnant for about 58-65 days. | "A cat is pregnant for about 58-65 days." (top score 0.855, cat-facts.txt) | Relevant | Accurate |
| 3 | How many muscles does cats have to control the outer ear? | Cats have 32 muscles control the outer ear. | "Cats have 32 muscles that control the outer ear." (top score 0.854, 62-facts-about-cats.txt) | Relevant | Accurate |
| 4 | What is the smallest pedigreed cat? | Singapura | "The smallest pedigreed cat is a Singapura, which can weigh just 4 lbs. (1.8 kg)." (top score 0.723, discover-wildlife) | Relevant | Accurate |
| 5 | What is the biggest wildcat? | Siberian Tiger | "The biggest wildcat today is the Siberian Tiger." (top score 0.815, cat-facts.txt) | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

All five planning questions retrieved a relevant top chunk (top similarity 0.72–0.87,
all above the 0.6 grounding threshold) and produced an accurate answer that matches the
expected answer. Question 4 had the lowest top score (0.723) because the corpus phrases
the fact as a "Singapura" wild-cat trivia item rather than using the words "smallest
pedigreed cat," but retrieval still surfaced the correct chunk.

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "How many hours a day do cats sleep?"

**What the system returned:** "Cats typically sleep for 12 to 16 hours, 13-16 hours, or
16 to 18, or 16-20 hours a day." — a muddled answer that strings together four different ranges instead of giving one clear figure.

**Root cause (tied to a specific pipeline stage):** This is a *retrieval + chunking*
problem, not a generation one. The fact "how long cats sleep" appears in many of our
sources, but each source states a slightly different range (12–16, 13–16, 16–18, 16–20).
Because every chunk is one self-contained fact, the top-5 retrieval pulled several of
these near-duplicate-but-conflicting chunks (top scores all ~0.78–0.87, so none were
filtered by the 0.6 threshold). The model faithfully grounded its answer in *all* of
them and, having no way to choose between equally-supported numbers, enumerated them
all. The grounding worked exactly as designed — the corpus itself is inconsistent.

**What you would change to fix it:** Add a de-duplication / conflict-resolution step
between retrieval and generation — e.g., cluster near-identical chunks and keep only the
highest-scoring representative, or instruct the model in the prompt to give a single
consolidated range and note when sources disagree. Preferring the most authoritative
source (the veterinary pages over general blogs) when figures conflict would also help.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The AI Tool Plan in `planning.md` broke the pipeline into milestones with exact function
signatures (`load_document`, `chunk_document`, `embedding`, `retrieve`,
`prompt_generation`, `response_generation`). Because those signatures and return shapes
were decided up front, each stage was implemented in its own file and the next stage
could be wired in without rework — e.g. `retrieve()` was specified to return dicts with
`text`, `score`, and `source`, which is exactly what both `prompt_generation()` and the
Gradio accordion later consumed. Having the chunking rule ("paragraph if blank-line
separated, otherwise per line") written down also removed guesswork while coding.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* The Milestone 6 — Interface bullet from `planning.md` (build a
  Gradio frontend with chat history, input, submit button, and a click-to-reveal
  accordion of retrieved contexts with scores; smaller grey
  context list; Gradio syntax only) plus the existing `retrieval.py` and `generation.py` interfaces.
- *What it produced:* `app.py` — a `gr.Blocks` app wiring retrieval → generation, a
  startup ingestion guard, and a `Chatbot.select` handler that opens an accordion with
  the contexts behind a clicked answer.
- *What I changed or overrode:* It initially used `gr.Chatbot(type="messages")` and the
  default HTML sanitizer; on Gradio 6.16 the `type` argument was removed and the inline
  font-size spans were being stripped, so I dropped `type` and set `sanitize_html=False`.
  I then directed a follow-up change so clicking the same response a second time
  collapses the accordion (a toggle via an `open_index` state).

**Instance 2**

- *What I gave the AI:* The observation that many LLM replies began with "according to the context," and the existing `PROMPT_TEMPLATE` in `generation.py`.
- *What it produced:* An updated prompt template adding an instruction to answer the question directly and avoid referring to the context, then a verification run over the evaluation questions confirming the phrasing was gone.
- *What I changed or overrode:* I kept a lighter wording of the instruction ("answer the question directly") rather than a long list of banned phrases, since the shorter version already removed the unwanted prefix while keeping answers accurate against the expected answers.
