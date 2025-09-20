#!/usr/bin/env python
"""Mini-facilitator script for testing Persona Agent discussions."""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path - not needed with proper hatch config
# project_root = Path(__file__).parent.parent.parent
# sys.path.insert(0, str(project_root / "src"))
from hibikasu_agent.agents.persona_agent import PersonaAgent
from hibikasu_agent.schemas import (
    DiscussionLog,
    Persona,
    ProjectSettings,
    Utterance,
)
from hibikasu_agent.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


class MiniFacilitator:
    """Minimal facilitator for testing Persona Agent discussions."""

    def __init__(
        self,
        project_settings: ProjectSettings,
        max_turns: int = 10,
        model: str = "gemini-2.5-flash-lite",
    ):
        """Initialize the mini-facilitator.

        Args:
            project_settings: Project configuration including personas and topic.
            max_turns: Maximum number of discussion turns.
            model: LLM model to use for agents.
        """
        self.project_settings = project_settings
        self.max_turns = max_turns
        self.model = model
        self.discussion_log: list[Utterance] = []
        self.persona_agents: list[PersonaAgent] = []

        logger.info(
            "MiniFacilitator initialized",
            project_name=project_settings.project_name,
            num_personas=len(project_settings.personas),
            max_turns=max_turns,
        )

    def setup_agents(self):
        """Initialize Persona Agents."""
        logger.info("Setting up Persona Agents")

        for persona in self.project_settings.personas:
            agent = PersonaAgent(persona, model=self.model)
            self.persona_agents.append(agent)
            logger.debug(f"Created agent for {persona.name}")

    async def run_discussion(self) -> DiscussionLog:
        """Run the discussion simulation.

        Returns:
            The complete discussion log.
        """
        logger.info(
            "Starting discussion",
            topic=self.project_settings.topic,
        )

        # Setup agents
        self.setup_agents()

        # Start discussion
        print(f"\n{'=' * 60}")
        print(f"議題: {self.project_settings.topic}")
        print(f"{'=' * 60}\n")

        # First round: each persona gives initial opinion
        print("【初回発言ラウンド】\n")
        for _i, agent in enumerate(self.persona_agents):
            logger.debug(f"Getting initial utterance from {agent.persona.name}")

            utterance_content = await agent.generate_initial_utterance(self.project_settings.topic)

            utterance = Utterance(
                persona_name=agent.persona.name,
                content=utterance_content,
                timestamp=datetime.now().isoformat(),
            )

            self.discussion_log.append(utterance)
            self._print_utterance(utterance)

            # Small delay to avoid rate limiting
            await asyncio.sleep(1)

        # Main discussion rounds
        print("\n【議論フェーズ】\n")
        for turn in range(1, self.max_turns + 1):
            logger.info(f"Discussion turn {turn}/{self.max_turns}")

            for agent in self.persona_agents:
                # Skip if this persona just spoke
                if self.discussion_log and self.discussion_log[-1].persona_name == agent.persona.name:
                    continue

                logger.debug(f"Getting response from {agent.persona.name}")

                utterance_content = await agent.generate_utterance(
                    topic=self.project_settings.topic,
                    discussion_history=self.discussion_log,
                )

                utterance = Utterance(
                    persona_name=agent.persona.name,
                    content=utterance_content,
                    timestamp=datetime.now().isoformat(),
                )

                self.discussion_log.append(utterance)
                self._print_utterance(utterance)

                # Small delay
                await asyncio.sleep(1)

        print(f"\n{'=' * 60}")
        print("議論終了")
        print(f"{'=' * 60}\n")

        discussion = DiscussionLog(
            log=self.discussion_log,
            project_id=self.project_settings.project_id,
        )

        logger.info(
            "Discussion completed",
            total_utterances=len(self.discussion_log),
        )

        return discussion

    def _print_utterance(self, utterance: Utterance):
        """Print an utterance to console."""
        print(f"【{utterance.persona_name}】")
        print(f"{utterance.content}")
        print()

    def save_log(self, log: DiscussionLog, output_path: Path):
        """Save discussion log to file.

        Args:
            log: The discussion log to save.
            output_path: Path to save the log.
        """
        output_data = {
            "project_settings": self.project_settings.model_dump(),
            "discussion_log": log.model_dump(),
            "metadata": {
                "model": self.model,
                "max_turns": self.max_turns,
                "timestamp": datetime.now().isoformat(),
            },
        }

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Discussion log saved to {output_path}")


def create_sample_personas() -> list[Persona]:
    """Create sample personas for testing."""
    return [
        Persona(
            name="佐藤 拓也",
            age=28,
            occupation="IT企業のソフトウェアエンジニア",
            personality="新しい技術やガジェットに興味があり、効率性を重視する。健康にも関心があるが、仕事が忙しくて運動不足気味。",
        ),
        Persona(
            name="田中 美咲",
            age=35,
            occupation="マーケティング会社のプランナー",
            personality="トレンドに敏感で、SNSでの情報発信も積極的。美容と健康に関心が高く、オーガニック製品を好む。",
        ),
        Persona(
            name="山田 健太",
            age=42,
            occupation="中小企業の営業部長",
            personality="コストパフォーマンスを重視する現実主義者。家族との時間を大切にし、子供の教育にも熱心。",
        ),
    ]


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run a test discussion with Persona Agents")
    parser.add_argument(
        "--topic",
        type=str,
        default="新しいエナジードリンクのコンセプトについてどう思いますか？健康志向でオーガニック素材を使用し、カフェインは控えめです。",
        help="Discussion topic",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for discussion log",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=5,
        help="Maximum number of discussion turns",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash-lite",
        help="LLM model to use",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(level=log_level)

    # Create project settings
    project_settings = ProjectSettings(
        project_name="テスト議論",
        topic=args.topic,
        personas=create_sample_personas(),
        project_overview="Persona Agent の議論品質テスト",
    )

    # Create and run facilitator
    facilitator = MiniFacilitator(
        project_settings=project_settings,
        max_turns=args.max_turns,
        model=args.model,
    )

    # Run discussion
    discussion_log = await facilitator.run_discussion()

    # Save log if output path specified
    if args.output:
        output_path = Path(args.output)
        facilitator.save_log(discussion_log, output_path)
    else:
        # Default output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"discussion_log_{timestamp}.json")
        facilitator.save_log(discussion_log, output_path)
        print(f"\nログを {output_path} に保存しました。")


if __name__ == "__main__":
    asyncio.run(main())
