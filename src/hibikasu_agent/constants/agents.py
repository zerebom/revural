"""Agent-related constant definitions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SpecialistDefinition:
    """Static configuration describing a specialist agent.

    Single Source of Truth for all agent information including UI metadata.
    """

    # Core agent configuration
    role: str
    agent_key: str
    state_key: str
    display_name: str
    review_description: str

    # UI enhancement fields (for rich profile display)
    role_label: str | None = None
    bio: str | None = None
    tags: list[str] | None = None
    avatar_url: str | None = None


ENGINEER_AGENT_KEY: Final[str] = "engineer_specialist"
UX_AGENT_KEY: Final[str] = "ux_designer_specialist"
QA_AGENT_KEY: Final[str] = "qa_tester_specialist"
PM_AGENT_KEY: Final[str] = "pm_specialist"

ENGINEER_ISSUES_STATE_KEY: Final[str] = "engineer_issues"
UX_ISSUES_STATE_KEY: Final[str] = "ux_designer_issues"
QA_ISSUES_STATE_KEY: Final[str] = "qa_tester_issues"
PM_ISSUES_STATE_KEY: Final[str] = "pm_issues"

SPECIALIST_DEFINITIONS: tuple[SpecialistDefinition, ...] = (
    SpecialistDefinition(
        role="engineer",
        agent_key=ENGINEER_AGENT_KEY,
        state_key=ENGINEER_ISSUES_STATE_KEY,
        display_name="Engineer Specialist",
        review_description="バックエンドエンジニアの専門的観点からPRDをレビュー",
        role_label="エンジニアAI",
        bio="バックエンド設計とAPIの専門家として、スケーラブルなシステム構築を支援します。",
        tags=["#API設計", "#スケーラビリティ", "#パフォーマンス"],
        avatar_url="/avatars/engineer.png",
    ),
    SpecialistDefinition(
        role="ux_designer",
        agent_key=UX_AGENT_KEY,
        state_key=UX_ISSUES_STATE_KEY,
        display_name="UX Designer Specialist",
        review_description="UXデザイナーの専門的観点からPRDをレビュー",
        role_label="UXデザイナーAI",
        bio="ユーザー中心設計の観点から、直感的で使いやすいインターフェースを提案します。",
        tags=["#UX設計", "#ユーザビリティ", "#アクセシビリティ"],
        avatar_url="/avatars/ux_designer.png",
    ),
    SpecialistDefinition(
        role="qa_tester",
        agent_key=QA_AGENT_KEY,
        state_key=QA_ISSUES_STATE_KEY,
        display_name="QA Tester Specialist",
        review_description="QAテスターの専門的観点からPRDをレビュー",
        role_label="QAテスターAI",
        bio="品質保証の専門家として、バグ予防とテスト戦略の観点から課題を発見します。",
        tags=["#品質管理", "#テスト戦略", "#バグ予防"],
        avatar_url="/avatars/qa_tester.png",
    ),
    SpecialistDefinition(
        role="pm",
        agent_key=PM_AGENT_KEY,
        state_key=PM_ISSUES_STATE_KEY,
        display_name="PM Specialist",
        review_description="プロダクトマネージャーの専門的観点からPRDをレビュー",
        role_label="プロダクトマネージャーAI",
        bio="ビジネス価値とユーザー価値のバランスを重視し、戦略的な製品判断を支援します。",
        tags=["#プロダクト戦略", "#要件定義", "#ビジネス価値"],
        avatar_url="/avatars/pm.png",
    ),
)

AGENT_STATE_KEYS: Mapping[str, str] = {
    definition.agent_key: definition.state_key for definition in SPECIALIST_DEFINITIONS
}

AGENT_DISPLAY_NAMES: Mapping[str, str] = {
    definition.agent_key: definition.display_name for definition in SPECIALIST_DEFINITIONS
}

STATE_KEY_TO_AGENT_KEY: Mapping[str, str] = {
    definition.state_key: definition.agent_key for definition in SPECIALIST_DEFINITIONS
}

ROLE_TO_DEFINITION: Mapping[str, SpecialistDefinition] = {
    definition.role: definition for definition in SPECIALIST_DEFINITIONS
}

SPECIALIST_AGENT_KEYS: tuple[str, ...] = tuple(definition.agent_key for definition in SPECIALIST_DEFINITIONS)
