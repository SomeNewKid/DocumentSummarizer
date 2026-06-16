"""Command-line interface for the application."""

from __future__ import annotations

import sys

from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.agents.requirement.requirements.conditional import (
    ConditionalRequirement,
)
from beeai_framework.backend import ChatModel
from beeai_framework.backend.events import ChatModelSuccessEvent
from beeai_framework.emitter import EmitterOptions, EventMeta
from beeai_framework.errors import FrameworkError
from beeai_framework.tools.think import ThinkTool

from document_summarizer.guardrails import (
    after_agent_guardrail,
    after_model_guardrail,
    after_tool_guardrail,
    before_agent_guardrail,
    before_model_guardrail,
    before_tool_guardrail,
    find_guardrail_violation,
)
from document_summarizer.tools import get_file_contents


async def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface."""
    prompt = _get_prompt(argv)
    if not prompt:
        example = "What does the acronym 'CSS' stand for?"
        raise SystemExit(f'Usage: python -m internal_acronym_explainer "{example}"')

    # model_name = "ollama:granite3.2:2b"
    model_name = "ollama:granite3.3:8b"

    agent = RequirementAgent(
        llm=ChatModel.from_name(model_name),
        tools=[ThinkTool(), get_file_contents],
        requirements=[ConditionalRequirement(ThinkTool, force_at_step=1)],
        role="Document Summarizer",
        instructions=(
            "Determine the name of the file whose content is to be summarized. "
            "Use the `get_file_contents` tool to read the named file. "
            "If the tool raises an error, you should summarize "
            "the error. "
            "Otherwise, generate a summary of the contents of the file, "
            "using fewer than 40 words. "
            "The summary should not include the name of the file."
        ),
    )

    try:
        expectation = "Short document summary."
        response = (
            await agent.run(prompt, expected_output=expectation)
            .on(
                "tool.custom.get_file_contents.start",
                before_tool_guardrail,
                EmitterOptions(is_blocking=True),
            )
            .on(
                "tool.custom.get_file_contents.success",
                after_tool_guardrail,
                EmitterOptions(is_blocking=True),
            )
            .on(
                "backend.ollama.chat.start",
                before_model_guardrail,
                EmitterOptions(is_blocking=True),
            )
            .on(
                is_chat_model_success_event,
                after_model_guardrail,
                EmitterOptions(is_blocking=True, match_nested=True),
            )
            .on(
                "agent.requirement.start",
                before_agent_guardrail,
                EmitterOptions(is_blocking=True),
            )
            .on(
                "agent.requirement.final_answer",
                after_agent_guardrail,
                EmitterOptions(is_blocking=True),
            )
        )
        print(response.last_message.text)
    except FrameworkError as err:
        guardrail_error = find_guardrail_violation(err)
        if guardrail_error:
            print(f"Guardrail blocked execution: {guardrail_error}")
        else:
            print(err.explain())
    return 0


def is_chat_model_success_event(meta: EventMeta) -> bool:
    return meta.data_type is ChatModelSuccessEvent


def _get_prompt(argv: list[str] | None = None) -> str:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        return ""

    return args[0]
