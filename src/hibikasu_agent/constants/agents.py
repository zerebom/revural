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
    personal_name: str | None = None


ENGINEER_AGENT_KEY: Final[str] = "engineer_specialist"
UX_AGENT_KEY: Final[str] = "ux_designer_specialist"
QA_AGENT_KEY: Final[str] = "qa_tester_specialist"
PM_AGENT_KEY: Final[str] = "pm_specialist"
DATA_SCIENTIST_AGENT_KEY: Final[str] = "data_scientist_specialist"
UX_WRITER_AGENT_KEY: Final[str] = "ux_writer_specialist"
SECURITY_SPECIALIST_AGENT_KEY: Final[str] = "security_specialist_specialist"
MARKETING_STRATEGIST_AGENT_KEY: Final[str] = "marketing_strategist_specialist"
LEGAL_ADVISOR_AGENT_KEY: Final[str] = "legal_advisor_specialist"

ENGINEER_ISSUES_STATE_KEY: Final[str] = "engineer_issues"
UX_ISSUES_STATE_KEY: Final[str] = "ux_designer_issues"
QA_ISSUES_STATE_KEY: Final[str] = "qa_tester_issues"
PM_ISSUES_STATE_KEY: Final[str] = "pm_issues"
DATA_SCIENTIST_ISSUES_STATE_KEY: Final[str] = "data_scientist_issues"
UX_WRITER_ISSUES_STATE_KEY: Final[str] = "ux_writer_issues"
SECURITY_SPECIALIST_ISSUES_STATE_KEY: Final[str] = "security_specialist_issues"
MARKETING_STRATEGIST_ISSUES_STATE_KEY: Final[str] = "marketing_strategist_issues"
LEGAL_ADVISOR_ISSUES_STATE_KEY: Final[str] = "legal_advisor_issues"

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
        personal_name="佐藤 彰",
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
        personal_name="鈴木 美緒",
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
        personal_name="リアム・オコナー",
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
        personal_name="マリア・ガルシア",
    ),
    SpecialistDefinition(
        role="data_scientist",
        agent_key=DATA_SCIENTIST_AGENT_KEY,
        state_key=DATA_SCIENTIST_ISSUES_STATE_KEY,
        display_name="Data Scientist Specialist",
        review_description="データサイエンティストの専門的観点からPRDをレビュー",
        role_label="データサイエンティストAI",
        bio="その仕様で本当に成果を測定できるかを検証します。ログ設計、KPIの計測可能性、A/Bテストの妥当性をレビューします。",
        tags=["#データ分析", "#効果測定", "#A/Bテスト"],
        avatar_url="/avatars/data_scientist.png",
        personal_name="高橋 健太",
    ),
    SpecialistDefinition(
        role="ux_writer",
        agent_key=UX_WRITER_AGENT_KEY,
        state_key=UX_WRITER_ISSUES_STATE_KEY,
        display_name="UX Writer Specialist",
        review_description="UXライターの専門的観点からPRDをレビュー",
        role_label="UXライターAI",
        bio="ブランドボイスを保ちながら、心に響く言葉を提案します。UIコピー、エラーメッセージ、行動を促すフレーズの改善を支援します。",
        tags=["#UXライティング", "#マイクロコピー", "#ブランドボイス"],
        avatar_url="/avatars/ux_writer.png",
        personal_name="田中 結衣",
    ),
    SpecialistDefinition(
        role="security_specialist",
        agent_key=SECURITY_SPECIALIST_AGENT_KEY,
        state_key=SECURITY_SPECIALIST_ISSUES_STATE_KEY,
        display_name="Security Specialist",
        review_description="セキュリティスペシャリストの専門的観点からPRDをレビュー",
        role_label="セキュリティAI",
        bio="想定される脅威からサービスとユーザーデータを守ります。脆弱性、認証認可、個人情報保護の観点からリスクを指摘します。",
        tags=["#セキュリティ", "#脆弱性診断", "#個人情報保護"],
        avatar_url="/avatars/security_specialist.png",
        personal_name="イヴァン・ペトロフ",
    ),
    SpecialistDefinition(
        role="marketing_strategist",
        agent_key=MARKETING_STRATEGIST_AGENT_KEY,
        state_key=MARKETING_STRATEGIST_ISSUES_STATE_KEY,
        display_name="Marketing Strategist",
        review_description="マーケティングストラテジストの専門的観点からPRDをレビュー",
        role_label="マーケティングAI",
        bio="プロダクトの価値が市場と顧客に正しく伝わるかを確認します。競合優位性、ターゲット顧客、市場投入戦略をレビューします。",
        tags=["#マーケティング戦略", "#GTM", "#競合分析"],
        avatar_url="/avatars/marketing_strategist.png",
        personal_name="クロエ・デュポン",
    ),
    SpecialistDefinition(
        role="legal_advisor",
        agent_key=LEGAL_ADVISOR_AGENT_KEY,
        state_key=LEGAL_ADVISOR_ISSUES_STATE_KEY,
        display_name="Legal Advisor",
        review_description="リーガルアドバイザーの専門的観点からPRDをレビュー",
        role_label="リーガルAI",
        bio="法務・コンプライアンス上のリスクを特定し、あなたの事業を守ります。利用規約、プライバシーポリシー、関連法規への準拠を確認します。",
        tags=["#法務", "#コンプライアンス", "#利用規約"],
        avatar_url="/avatars/legal_advisor.png",
        personal_name="サミュエル・ジョーンズ",
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
