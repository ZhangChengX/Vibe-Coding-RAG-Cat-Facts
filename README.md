# Vibe-Coding-RAG-Cat-Facts

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
An chatbot of Cat facts knowledge for cat lovers

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | dataset |  | https://huggingface.co/ngxson/demo_simple_rag_py/resolve/main/cat-facts.txt |
| 2 | webpage |  | https://cvillecatcare.com/veterinary-topics/101-amazing-cat-facts-fun-trivia-about-your-feline-friend/ |
| 3 | webpage |  | https://www.discoverwildlife.com/animal-facts/mammals/cat-facts |
| 4 | webpage |  | https://www.bjsrawpetfood.com/blogs/all/fascinating-cat-facts-you-didn-t-know |
| 5 | webpage |  | https://www.mygavet.com/services/cats/blog/50-cat-facts-you-probably-didnt-know |
| 6 | webpage |  | https://www.animalfriends.co.uk/cat/cat-blog/cat-facts/ |
| 7 | webpage |  | https://www.goodhousekeeping.com/life/pets/g69020271/shocking-facts-about-cats-you-never-knew/ |
| 8 | webpage |  | https://petventuresbook.com/blogs/blog/20-interesting-cat-facts |
| 9 | webpage |  | https://www.nekocatcafe.com/blog/62-facts-about-cats |
| 10 | webpage |  | https://www.aaha.org/resources/lets-get-purr-sonal-interesting-facts-about-cats/ |

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

**Final chunk count:**

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
You are a helpful assistant for answering questions based on context about cat facts. 
Use only the following retrieved context to answer the question. 
If the answer isn't in the context, say you don't know instead of making something up.
context: [context]
question: [query]

**How source attribution is surfaced in the response:**
After every generated answer we include a short "Sources" block listing the top retrieved documents used to produce the reply.
If the answer cannot be supported by retrieved context the assistant replies "I don't know" and does not fabricate sources.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

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

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
