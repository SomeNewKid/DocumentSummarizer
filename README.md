# Document Summarizer

Document Summarizer is a small Python command-line sample for exploring
guardrails in the BeeAI framework. It accepts a prompt asking for a document
summary, lets a BeeAI `RequirementAgent` call a local file-reading tool, and
prints a short summary.

> [!WARNING]
> This is an experimental project and should not be considered production-ready.

The project was created to learn where guardrails can be added around a
BeeAI-based agent. The document summarization task is intentionally small so
the guardrail behavior stays visible.

## What It Does

The CLI accepts a prompt such as:

```powershell
.\.venv\Scripts\python.exe -m document_summarizer "Please summarize the example.txt file."
```

The agent then:

- checks the user's request before the agent run continues
- checks each model call before messages are sent to the LLM
- calls the `get_file_contents` tool for documents under `documents`
- checks the tool input before the tool executes
- checks the tool output before the agent uses it
- checks model responses before the agent continues
- checks the final answer before printing it

Guardrails can either allow execution to continue or block the run and print a
short refusal message.

## Requirements

- Python 3.11.
- PowerShell on Windows.
- Ollama installed and running.
- The local Ollama model used by `src/document_summarizer/agent.py`:

```powershell
ollama pull granite3.3:8b
```

## Setup

Create the virtual environment and install the project with development
dependencies:

```powershell
.\scripts\setup-dev.ps1
```

The setup script expects Python 3.11 at the path configured in
`scripts\setup-dev.ps1`.

## Running

Run the agent from the repository root:

```powershell
.\.venv\Scripts\python.exe -m document_summarizer "Please summarize the example.txt file."
```

The command reads sample files from the `documents` directory. Try different
file names to observe which guardrails allow the run to continue and which ones
block execution.

Example blocked request:

```powershell
.\.venv\Scripts\python.exe -m document_summarizer "Please summarize the top-secret.txt file."
```

## Development Checks

Run formatting, linting, type checking, and tests:

```powershell
.\scripts\check.ps1
```

This runs:

- `ruff format .`
- `ruff check .`
- `pyright`
- `pytest`

## Project Structure

```text
src/document_summarizer/
  __main__.py     Package entry point for python -m document_summarizer
  agent.py        BeeAI RequirementAgent setup and command-line entry point
  guardrails.py   Agent, model, and tool guardrails
  tools.py        Local document-reading tool
  utilities.py    Path and filename helpers

documents/
  alice.md
  credentials.txt
  desknet.pdf
  devil.txt
  example.txt
  ghost.txt
  kitten.txt
  lumora.jpg
  top-secret.txt

tests/
  test_smoke.py
  test_utilities.py

scripts/
  setup-dev.ps1
  check.ps1
```

## Notes

This project is a guardrail learning exercise, not a general-purpose document
summarizer. The file-reading tool is deliberately narrow: it reads only named
`.md` and `.txt` files from the local `documents` directory.

The sample guardrails are intentionally simple. They block specific file names,
path-like tool arguments, selected words in model or tool content, and selected
words in the final answer. They are meant to make the BeeAI lifecycle visible,
not to provide real data-loss prevention.

Agent behavior and final wording can vary between runs because tool selection
and final response generation are model-driven. Local Ollama model behavior can
also vary by model version and runtime configuration.

## Third-Party Notices

This project has a direct runtime dependency on the `beeai-framework` Python
package. See the package's PyPI license metadata for full license and notice
terms.

## License

GNU General Public License v3.0. See the `LICENSE` file for details.
