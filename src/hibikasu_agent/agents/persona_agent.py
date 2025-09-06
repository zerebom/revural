"""Persona Agent implementation using Google ADK."""

from typing import Any, cast
from uuid import uuid4

from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.adk.runners import InMemoryRunner
from google.genai import types

from hibikasu_agent.agents.prompts import (
    create_initial_prompt,
    create_persona_prompt,
)
from hibikasu_agent.schemas import Persona, Utterance
from hibikasu_agent.utils.logging_config import get_logger

logger = get_logger(__name__)


class PersonaAgent:
    """AI Persona Agent that participates in discussions."""

    def __init__(
        self,
        persona: Persona,
        model: str = "gemini-2.5-flash-lite",
    ):
        """Initialize a Persona Agent.

        Args:
            persona: The persona configuration.
            model: The LLM model to use.
        """
        self.persona = persona
        self.model = model

        # Create the underlying LLM agent
        self.agent = LlmAgent(
            name=f"persona_{persona.name.replace(' ', '_')}",
            model=model,
            description=f"AI persona: {persona.name} - {persona.occupation}",
            instruction=(f"You are {persona.name}, a {persona.age}-year-old " f"{persona.occupation}."),
        )

        # Create runner once and reuse it
        app_name = f"persona_app_{self.persona.name.replace(' ', '_')}"
        self.runner = InMemoryRunner(agent=self.agent, app_name=app_name)

        logger.info(
            "PersonaAgent initialized",
            persona_name=persona.name,
            model=model,
        )

    async def generate_initial_utterance(self, topic: str) -> str:
        """Generate the first utterance for starting a discussion.

        Args:
            topic: The discussion topic.

        Returns:
            The generated utterance content.
        """
        logger.debug(
            "Generating initial utterance",
            persona_name=self.persona.name,
            topic=topic,
        )

        prompt = create_initial_prompt(self.persona, topic)

        # Use the shared runner instance
        session_id = str(uuid4())
        user_id = "user"
        await self.runner.session_service.create_session(
            app_name=self.runner.app_name, user_id=user_id, session_id=session_id
        )

        message = types.Content(parts=[types.Part(text=prompt)], role="user")

        # Collect all events from the async generator
        events = []
        async for event in self.runner.run_async(
            session_id=session_id,
            user_id=user_id,
            new_message=message,
        ):
            events.append(event)

        # Extract text from the final response event
        utterance_content = self._extract_text_from_events(events)

        logger.debug(
            "Initial utterance generated",
            persona_name=self.persona.name,
            utterance_length=len(utterance_content),
        )

        return utterance_content

    async def generate_utterance(
        self,
        topic: str,
        discussion_history: list[Utterance],
        moderator_input: str | None = None,
    ) -> str:
        """Generate an utterance in response to the discussion.

        Args:
            topic: The discussion topic.
            discussion_history: List of past utterances.
            moderator_input: Optional moderator intervention.

        Returns:
            The generated utterance content.
        """
        logger.debug(
            "Generating utterance",
            persona_name=self.persona.name,
            history_length=len(discussion_history),
            has_moderator_input=bool(moderator_input),
        )

        prompt = create_persona_prompt(self.persona, topic, discussion_history, moderator_input)

        # Use the shared runner instance
        session_id = str(uuid4())
        user_id = "user"
        await self.runner.session_service.create_session(
            app_name=self.runner.app_name, user_id=user_id, session_id=session_id
        )

        message = types.Content(parts=[types.Part(text=prompt)], role="user")

        # Collect all events from the async generator
        events = []
        async for event in self.runner.run_async(
            session_id=session_id,
            user_id=user_id,
            new_message=message,
        ):
            events.append(event)

        # Extract text from the final response event
        utterance_content = self._extract_text_from_events(events)

        logger.debug(
            "Utterance generated",
            persona_name=self.persona.name,
            utterance_length=len(utterance_content),
        )

        return utterance_content

    def _extract_text_from_events(self, events: list[Event]) -> str:
        """Extract text content from run events.

        Args:
            events: List of events from runner.run_async()

        Returns:
            The extracted text content.
        """
        # Look for the last response content in events
        for event in reversed(events):
            if hasattr(event, "content") and event.content is not None:
                content = event.content
                if hasattr(content, "parts") and content.parts:
                    # Extract text from the first part
                    first_part = content.parts[0]
                    if hasattr(first_part, "text") and first_part.text is not None:
                        return cast(str, first_part.text)

        # If no proper content found, return string representation
        return str(events[-1] if events else "No response")

    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text content from agent response.

        Args:
            response: The agent response object.

        Returns:
            The extracted text content.
        """
        # ADK runner returns a RunResult object
        if hasattr(response, "content"):
            content = response.content
            if hasattr(content, "parts") and content.parts:
                # Extract text from the first part
                first_part = content.parts[0]
                if hasattr(first_part, "text") and isinstance(first_part.text, str):
                    return first_part.text

        # Fallback to other structures
        if hasattr(response, "text") and isinstance(response.text, str):
            return response.text
        elif isinstance(response, str):
            return response

        # If all else fails, convert to string
        return str(response)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"PersonaAgent(name='{self.persona.name}', "
            f"age={self.persona.age}, "
            f"occupation='{self.persona.occupation}')"
        )
