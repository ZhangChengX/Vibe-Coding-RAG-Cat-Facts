# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
An chatbot of Cat facts knowledge for cat lovers

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** dynamic chunk size by each sentence or paragraph

**Overlap:** no overlap

**Reasoning:** on the webpages, each paragraph or sentence is a fact. in cat-facts.txt each sentence is a fact.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 5

**Production tradeoff reflection:** all-MiniLM-L6-v2 is a good fit for this small cat-facts corpus because it is fast, low-cost, and accurate enough for short factual text.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Can cats taste sweets? | No, Cats can’t taste sweets. |
| 2 | How long does a cat pregnant? | A cat is pregnant for about 58-65 days. |
| 3 | How many muscles does cats have to control the outer ear? | Cats have 32 muscles control the outer ear. |
| 4 | What is the smallest pedigreed cat? | Singapura |
| 5 | What is the biggest wildcat? | Siberian Tiger |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. When extracting cat fact content from webpages, do not extract other text such as the header, footer, navigation menu, sidebar, etc.

2. Some webpages contain a single fact in every sentence, while others may contain an entire paragraph that is a single fact. Be careful to distinguish between them.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

flowchart LR
    A["Document Ingestion"] --> B["Chunking"]
    B --> C["Embedding"]
    C --> D["Vector Store (ChromaDB)"]
    D --> E["Retrieval"]
    E --> F["Embedding Model (all-MiniLM-L6-v2)"]
    F --> G["Generation (LLM API)"]

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 2 — Collect dataset:**
- Create collection.py
- Create a function collect(url: str) that crawls the text from the URL, keeping only the main content of the web page and removing other content like the header, footer, navigation menu, and sidebar. Return the collected text.
- Create a function generate_dataset(urls: List) that collects the URLs provided in the Documents section. Use the collect() function to get the text from each URL and store each text as a .txt file in the documents folder. the txt file name can be the title of webpage. Ignore the first URL, since its text already exists in the folder as cat-facts.txt.

**Milestone 3 — Ingestion and chunking:**
- Create chunking.py
- Create a function load_document(file_name:str) that loads txt file in documents folder and returns the text content.
- Create a function chunk_document(document:str) that splits the document by line or paragraph into a list of chunk. If the document contains multiple paragraphs separated by a blank line, then each paragraph is a chunk, otherwise, each line is a chunk. Ignore the chunk if it only contains blank line or space.

**Milestone 4 — Embedding and retrieval:**
- Create retrieval.py
- Create helper variables _client and _collection to hold ChromaDB client and collection used by internal functions, Store the ChromaDB file in ./chroma_db folder .
- Create a function embedding(file_name:str, chunks:List) that embeds the list of chunks and stores the list of the raw chunk with corresponding embedding and source(file_name) into the ChromaDB vector database.
- Create a function retrieve(query:str, n_results:int) that searchs the top n_results relevent results and returns the list of result ranked by similarity score, each item in the list need to contain text, score, and source.

**Milestone 5 — Generation:**
- Create generation.py
- Create a function prompt_generation(query:str, context:List) that retrieves 5 relevent results as context using retrieve(), ignores the result if the score less than 0.6, combines and returns the remain context and query with the following prompt template: 
"You are a helpful assistant for answering questions based on cat facts.
Use only the following retrieved context to answer the question directly.
If the answer isn't in the context, say you don't know instead of making something up.
context: [context]
question: [query]"
- Create a function response_generation(prompt:str) that sends the prompt to LLM and returns the response.

**Milestone 6 — Interface:**
- Create app.py 
- Create a simple Gradio (gradio>=6.9.0) web page as a frontend that contains at least the following UI elements: chat history, chat input, and a button to submit the input. Display chat response inside chat history area. When clicking the response, an Accordion is displayed to show a list of what retrieved contexts generated the response, with the score of each context. Add a toggle state so clicking the same response again closes the accordion. The list in accordion used smaller and grey font style. Do not generate html and css file, use Gradio syntax only.
- Create a backend server to handle the entire workflow described in the Architecture section.
