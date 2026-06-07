"""Milestone 5 — Generation.

Builds a grounded prompt from a query and the retrieved context, then sends it
to the Groq LLM and returns the generated answer.
"""

import os
from typing import List, Union

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Groq-hosted model used for generation. Override with the GROQ_MODEL env var.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Retrieved results below this similarity score are treated as irrelevant and
# dropped from the context.
SCORE_THRESHOLD = 0.6

PROMPT_TEMPLATE = """You are a helpful assistant for answering questions based on context about cat facts.
Use only the following retrieved context to answer the question.
If the answer isn't in the context, say you don't know instead of making something up.
context: {context}
question: {query}"""

_client = None


def _get_client() -> Groq:
    """Create (once) and return the Groq client."""
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def prompt_generation(query: str, context: List[Union[dict, str]]) -> str:
    """Combine the retrieved context and the query into a single prompt.

    Results whose similarity score is below SCORE_THRESHOLD are ignored so that
    weakly-related chunks don't mislead the model.

    Args:
        query: The user's question.
        context: The retrieved results. Each item may be a dict (as returned by
            retrieve(), with "text", "score", and "source" keys) or a plain
            string.

    Returns:
        The fully formatted prompt string.
    """
    lines = []
    for item in context:
        if isinstance(item, dict):
            if item.get("score", 1.0) < SCORE_THRESHOLD:
                continue
            text = item.get("text", "")
            lines.append(text)
        else:
            lines.append(item)
    
    if len(lines) > 0:
        context_block = "\n".join(lines)
    else:
        # context_block = "No relevant context retrieved. Answer based on your general knowledge."
        context_block = "No relevant context retrieved. Answer: I don't know."
        print("# Warning: no retrieved context passed the score threshold.")

    return PROMPT_TEMPLATE.format(context=context_block, query=query)


def response_generation(prompt: str) -> str:
    """Send the prompt to the Groq LLM and return the response text.

    Args:
        prompt: The fully formatted prompt produced by prompt_generation().

    Returns:
        The model's generated answer.
    """
    response = _get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # End-to-end smoke test: retrieve context, build a prompt, generate answers.
    from retrieval import retrieve

    eval_questions = [
        "Can cats taste sweets?",
        "How long does a cat pregnant?",
        "How many muscles does cats have to control the outer ear?",
        "What is the smallest pedigreed cat?",
        "What is the biggest wildcat?",
        "Can cats develop an AI chatbot using Python and Groq LLMs?",
    ]
    for question in eval_questions:
        context = retrieve(question, 5)
        print("Question: ", question)
        print("Context:\n", context)
        prompt = prompt_generation(question, context)
        print("Prompt:\n", prompt)
        answer = response_generation(prompt)
        print(f"Q: {question}")
        print(f"A: {answer}\n")
