import json
from collections.abc import Iterator
from typing import Any, Protocol, TypeGuard

from beeai_framework.agents.requirement.events import (
    RequirementAgentFinalAnswerEvent,
    RequirementAgentStartEvent,
)
from beeai_framework.backend.events import ChatModelStartEvent, ChatModelSuccessEvent
from beeai_framework.backend.types import ChatModelOutput
from beeai_framework.errors import FrameworkError
from beeai_framework.tools.events import ToolStartEvent, ToolSuccessEvent

from document_summarizer.utilities import is_plain_file_name


class GuardrailViolation(Exception):
    """Raised when a guardrail blocks an agent action."""


class _FileNameInput(Protocol):
    file_name: str


async def before_agent_guardrail(event: RequirementAgentStartEvent, _meta: Any) -> None:
    """Reject requests about forbidden files."""
    blocked_file = "top-secret.txt"
    request_text = event.state.input.text

    if not request_text:
        return

    request_text = request_text.lower()

    if blocked_file in request_text:
        raise GuardrailViolation(f"Requests about {blocked_file!r} are not permitted.")


async def after_agent_guardrail(
    event: RequirementAgentFinalAnswerEvent, _meta: Any
) -> None:
    """Reject final answers containing disallowed text."""
    blocked_word = "kitten"
    final_answer = event.output

    if not final_answer:
        return

    if blocked_word in final_answer.lower():
        raise GuardrailViolation(
            f"Refusing to print final response because it contains {blocked_word!r}."
        )


async def before_model_guardrail(event: ChatModelStartEvent, _meta: Any) -> None:
    """Reject model calls containing disallowed text."""
    blocked_word = "devil"

    for message in event.input.messages:
        message_text = message.text
        if not message_text:
            continue

        message_text = message_text.lower()
        if blocked_word in message_text:
            raise GuardrailViolation(
                f"Refusing to send the word {blocked_word!r} to the language model."
            )


async def after_model_guardrail(event: ChatModelSuccessEvent, _meta: Any) -> None:
    """Reject model responses containing disallowed text."""
    if not isinstance(event, ChatModelSuccessEvent):
        return

    blocked_word = "ghost"

    text = get_model_response_text(event.value)

    if not text:
        return

    text = text.lower()
    if blocked_word in text:
        raise GuardrailViolation(
            "Refusing to continue because the model "
            f"response contains {blocked_word!r}."
        )


async def before_tool_guardrail(
    event: ToolStartEvent,
    _meta: Any,
) -> None:
    """Reject calls with path-like file names."""
    tool_input = event.input.model_dump()
    file_name = tool_input.get("file_name")

    if not isinstance(file_name, str):
        raise GuardrailViolation("File name must be a string.")

    if not is_plain_file_name(file_name):
        raise GuardrailViolation(
            "File name cannot be a fully-qualified path or relative path."
        )


async def before_tool_modification(event: ToolStartEvent, _meta: Any) -> None:
    event_input = event.input

    if not _has_file_name(event_input):
        return

    file_name = event_input.file_name.strip()

    if file_name.lower() == "jekyll.md":
        event_input.file_name = "hyde.md"
    else:
        event_input.file_name = file_name


async def after_tool_guardrail(
    event: ToolSuccessEvent,
    _meta: Any,
) -> None:
    """Reject document content containing sensitive information"""
    content = event.output.get_text_content()

    if not content:
        return

    content = content.lower()

    # Clearly this is an overly simplistic way of detecting sensitive information.
    # However, the focus of this project is hooking up guardrails, not trying to
    # create real guardrails.
    for word in ["database_", "admin_"]:
        if word in content:
            raise GuardrailViolation(
                "`get_file_contents` returned document content containing "
                "sensitive information."
            )


def get_model_response_text(output: ChatModelOutput) -> str:
    """Return text the model is trying to present to the user."""
    text_parts = [output.get_text_content()]

    for tool_call in output.get_tool_calls():
        if tool_call.tool_name != "final_answer":
            continue

        try:
            tool_args = json.loads(tool_call.args)
        except json.JSONDecodeError:
            text_parts.append(tool_call.args)
            continue

        response = tool_args.get("response")
        if isinstance(response, str):
            text_parts.append(response)

    return "\n".join(part for part in text_parts if part)


def find_guardrail_violation(error: BaseException) -> GuardrailViolation | None:
    """Return the original guardrail violation if one exists in the error tree."""
    for nested_error in walk_exception_tree(error):
        if isinstance(nested_error, GuardrailViolation):
            return nested_error

    return None


def walk_exception_tree(error: BaseException) -> Iterator[BaseException]:
    """Yield an exception and all nested causes, contexts, and group children."""
    seen: set[int] = set()
    stack: list[BaseException] = [error]

    while stack:
        current = stack.pop()

        if id(current) in seen:
            continue

        seen.add(id(current))
        yield current

        if isinstance(current, BaseExceptionGroup):
            stack.extend(current.exceptions)

        if current.__cause__ is not None:
            stack.append(current.__cause__)

        if current.__context__ is not None:
            stack.append(current.__context__)

        if isinstance(current, FrameworkError) and current.predecessor is not None:
            stack.append(current.predecessor)


def _has_file_name(input_value: object) -> TypeGuard[_FileNameInput]:
    file_name = getattr(input_value, "file_name", None)
    return isinstance(file_name, str)
