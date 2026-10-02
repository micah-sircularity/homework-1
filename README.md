# Book search and course assistant

A small Python project for searching a collection of programming books and asking questions about them. It extracts text from PDFs, prepares and chunks the text, searches it with `minsearch`, and uses Fireworks AI to answer questions from retrieved passages.

## Setup

Requires Python 3.13 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

The repository includes book PDFs, extracted text, and prepared documents, so search works without a preparation step. The book source URLs are listed in `data/books.csv`.

## Search the books

```bash
uv run python helpers/index_docs.py
uv run ./helpers/search "recursion" --num-results 5
```

The first command prints the number of indexed documents. The second prints matching passages with their source book and starting position.

## Ask the assistant

Set a Fireworks API key in your environment or in a local `.env` file:

```text
FIREWORKS_API_KEY=your-key-here
```

Then start a question and answer session:

```bash
uv run ./helpers/rag "What is recursion?"
```

Enter more questions at the prompt, or submit a blank line to exit. Responses include an answer, confidence information, suggested follow-up questions, token usage, and an estimated cost. `.env` is ignored by Git.

## Prepare documents

To recreate the prepared data from the included PDFs:

```bash
uv run python -c 'from pathlib import Path; from helpers.extract import write_pdf_directory; write_pdf_directory(Path("data"), Path("books_text"))'
uv run python helpers/prepare.py
uv run ./helpers/chunk count books_text/think-python-2e.md
```

The extraction step writes Markdown files to `books_text/`. The preparation step writes document JSON to `prepared_docs/`. The chunk command replaces the selected book's JSON with overlapping chunks; `--size` and `--step` set the window size and stride in non-empty lines. Search and the assistant read JSON from `prepared_docs/`.
