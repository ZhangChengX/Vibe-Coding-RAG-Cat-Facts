"""Milestone 6 — Interface.

A Gradio web frontend over the cat-facts RAG pipeline. On startup it makes sure
the vector store is populated (Ingestion -> Chunking -> Embedding -> Vector
Store), and every question runs the full workflow (Retrieval -> Generation).

The chat history shows each answer. Clicking an answer opens an accordion that
lists the retrieved contexts — with their similarity scores — that produced it.
"""

from typing import Dict, List, Tuple

import gradio as gr

from chunking import DOCUMENTS_DIR, chunk_document, load_document
from generation import prompt_generation, response_generation
from retrieval import _collection, embedding, retrieve

# How many chunks to retrieve per query (matches the planning Top-k).
TOP_K = 5


def ensure_corpus_ingested() -> None:
    """Populate the vector store from documents/ if it is still empty.

    Covers the Ingestion -> Chunking -> Embedding -> Vector Store stages so the
    app is self-contained: a fresh checkout can launch and answer questions
    without running retrieval.py first.
    """
    if _collection.count() > 0:
        print(f"Vector store ready with {_collection.count()} chunks.")
        return

    print("Vector store empty — ingesting documents/ ...")
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        chunks = chunk_document(load_document(path.name))
        embedding(path.name, chunks)
        print(f"  embedded {len(chunks)} chunks from {path.name}")
    print(f"Vector store now holds {_collection.count()} chunks.")


def answer_query(query: str) -> Tuple[str, List[Dict]]:
    """Run the full Retrieval -> Generation workflow for a single question.

    Args:
        query: The user's question.

    Returns:
        A tuple of (answer, contexts) where contexts is the list of retrieved
        results (each a dict with "text", "score", "source").
    """
    contexts = retrieve(query, TOP_K)
    prompt = prompt_generation(query, contexts)
    answer = response_generation(prompt)
    return answer, contexts


def format_contexts(contexts: List[Dict]) -> str:
    """Render the retrieved contexts as a smaller, grey markdown list."""
    if not contexts:
        return "<span style='font-size:0.85em;color:#888'>No context retrieved.</span>"

    items = []
    for ctx in contexts:
        items.append(
            f"- <span style='font-size:0.85em;color:#888'>"
            f"<b>[{ctx['score']:.3f}]</b> ({ctx['source']}) {ctx['text']}"
            f"</span>"
        )
    return "\n".join(items)


def respond(
    message: str,
    history: List[Dict],
    contexts_by_index: Dict[int, List[Dict]],
):
    """Handle a submitted message: run the workflow and update the chat.

    Args:
        message: The submitted text.
        history: The current chat history (list of role/content dicts).
        contexts_by_index: Maps an assistant message's position in history to
            the contexts that produced it.

    Returns:
        Updated (chatbot, input box, contexts state, accordion) values.
    """
    if not message or not message.strip():
        return history, "", contexts_by_index, gr.update(), None

    answer, contexts = answer_query(message)

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": answer},
    ]
    # The assistant message we just appended is the last item in history.
    contexts_by_index[len(history) - 1] = contexts

    # Collapse the accordion (and clear the open index) until the user clicks a
    # response to inspect it.
    return history, "", contexts_by_index, gr.update(open=False), None


def show_context(
    contexts_by_index: Dict[int, List[Dict]],
    open_index,
    evt: gr.SelectData,
):
    """Toggle the contexts behind a clicked chat message.

    Clicking a response opens the accordion on its contexts; clicking the same
    response again collapses it.

    Args:
        contexts_by_index: Maps message index -> retrieved contexts.
        open_index: The message index currently shown in the accordion, or None
            if the accordion is collapsed.
        evt: The Chatbot select event carrying the clicked message index.

    Returns:
        Updated (accordion, context markdown, open-index state) values.
    """
    # The Chatbot select event reports the clicked message's flat position.
    # Normalize to an int in case a future Gradio sends a tuple/list.
    index = evt.index
    if isinstance(index, (list, tuple)):
        index = index[0]

    contexts = contexts_by_index.get(index)
    if contexts is None:
        # A user message (or one with no stored context) was clicked; leave the
        # accordion as it is.
        return gr.update(), gr.update(), open_index

    if index == open_index:
        # The currently-shown response was clicked again — collapse it.
        return gr.update(open=False), gr.update(), None

    return gr.update(open=True), format_contexts(contexts), index


with gr.Blocks(title="Cat Facts — The Unofficial Guide") as app:
    gr.Markdown("# 🐱 Cat Facts — The Unofficial Guide")
    gr.Markdown("Ask anything about cats. Click an answer to see the sources behind it.")

    # State: which retrieved contexts produced each assistant message.
    contexts_state = gr.State({})
    # State: the message index currently shown in the accordion (None if closed).
    open_index_state = gr.State(None)

    # sanitize_html=False so the inline font-size spans on answers render.
    chatbot = gr.Chatbot(label="Chat history", height=420, sanitize_html=False)

    with gr.Accordion("Retrieved context (click a response above)", open=False) as accordion:
        context_md = gr.Markdown()

    with gr.Row():
        msg = gr.Textbox(
            placeholder="e.g. Can cats taste sweets?",
            show_label=False,
            scale=8,
            autofocus=True,
        )
        send = gr.Button("Send", variant="primary", scale=1)

    # Submit via button click or pressing Enter in the textbox.
    submit_args = dict(
        fn=respond,
        inputs=[msg, chatbot, contexts_state],
        outputs=[chatbot, msg, contexts_state, accordion, open_index_state],
    )
    send.click(**submit_args)
    msg.submit(**submit_args)

    # Clicking a chat message toggles the contexts that produced it.
    chatbot.select(
        fn=show_context,
        inputs=[contexts_state, open_index_state],
        outputs=[accordion, context_md, open_index_state],
    )


if __name__ == "__main__":
    ensure_corpus_ingested()
    app.launch()
