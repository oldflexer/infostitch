"""Template Value Object.

Represents a post template with its prompt and metadata.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True, slots=True)
class Template:
    """Immutable value object representing a post template."""

    id: str
    name: str
    prompt: str
    description: str = ""
    variables: List[str] = field(default_factory=list)
    max_length: int = 730
    min_length: int = 700

    def __post_init__(self) -> None:
        """Validate template after initialization."""
        if not self.id:
            raise ValueError("Template ID cannot be empty")
        if not self.name:
            raise ValueError("Template name cannot be empty")
        if not self.prompt:
            raise ValueError("Template prompt cannot be empty")

    def format_prompt(self, **kwargs: str) -> str:
        """Format prompt with provided variables."""
        try:
            return self.prompt.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def validate_variables(self, provided: Dict[str, str]) -> List[str]:
        """Check which required variables are missing."""
        missing = []
        for var in self.variables:
            if var not in provided:
                missing.append(var)
        return missing


# Predefined templates (matching the 10 templates from DB.md)
TEMPLATES = {
    "news_brief": Template(
        id="news_brief",
        name="News Brief",
        description="Concise news summary with key facts",
        prompt=(
            "Write a concise news post about the following article.\n"
            "Requirements:\n"
            "- Only facts from the article, no speculation\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji somewhere in the text\n"
            "- One HTML <b> tag for emphasis\n"
            "- No markdown, no links, no channel signature\n"
            "- Russian language\n\n"
            "Article title: {title}\n"
            "Article summary: {summary}\n"
            "Full text: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "deep_dive": Template(
        id="deep_dive",
        name="Deep Dive",
        description="Detailed analysis with context",
        prompt=(
            "Write an in-depth analysis post about the following article.\n"
            "Requirements:\n"
            "- Only facts from the article, no speculation\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji somewhere in the text\n"
            "- One HTML <b> tag for emphasis\n"
            "- No markdown, no links, no channel signature\n"
            "- Russian language\n\n"
            "Article title: {title}\n"
            "Article summary: {summary}\n"
            "Full text: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "quick_take": Template(
        id="quick_take",
        name="Quick Take",
        description="Short punchy take on the news",
        prompt=(
            "Write a quick, punchy take on this news.\n"
            "Requirements:\n"
            "- Only facts from the article\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji\n"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "expert_opinion": Template(
        id="expert_opinion",
        name="Expert Opinion",
        description="Expert commentary style",
        prompt=(
            "Write an expert commentary on this AI/tech news.\n"
            "Requirements:\n"
            "- Only facts from the article\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji\n"
            "- One HTML <b> tag\n"
            "- No markdown, no links, no signature\n"
            "- Russian language\n\n"
            "Title: {title}\n"
            "Summary: {summary}\n"
            "Content: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "case_study": Template(
        id="case_study",
        name="Case Study",
        description="Case study format for practical examples",
        prompt=(
            "Write a case study style post about this news.\n"
            "Requirements:\n"
            "- Only facts from the article\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji\n"
            "- One HTML <b> tag\n"
            "- No markdown, no links, no signature\n"
            "- Russian language\n\n"
            "Title: {title}\n"
            "Summary: {summary}\n"
            "Content: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "trend_analysis": Template(
        id="trend_analysis",
        name="Trend Analysis",
        description="Trend analysis perspective",
        prompt=(
            "Write a trend analysis post about this development.\n"
            "Requirements:\n"
            "- Only facts from the article\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji\n"
            "- One HTML <b> tag\n"
            "- No markdown, no links, no signature\n"
            "- Russian language\n\n"
            "Title: {title}\n"
            "Summary: {summary}\n"
            "Content: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "tool_review": Template(
        id="tool_review",
        name="Tool Review",
        description="Tool/product review style",
        prompt=(
            "Write a tool review style post about this announcement.\n"
            "Requirements:\n"
            "- Only facts from the article\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji\n"
            "- One HTML <b> tag\n"
            "- No markdown, no links, no signature\n"
            "- Russian language\n\n"
            "Title: {title}\n"
            "Summary: {summary}\n"
            "Content: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "research_summary": Template(
        id="research_summary",
        name="Research Summary",
        description="Academic research summary style",
        prompt=(
            "Write a research summary post about this paper/study.\n"
            "Requirements:\n"
            "- Only facts from the article\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji\n"
            "- One HTML <b> tag\n"
            "- No markdown, no links, no signature\n"
            "- Russian language\n\n"
            "Title: {title}\n"
            "Summary: {summary}\n"
            "Content: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "industry_news": Template(
        id="industry_news",
        name="Industry News",
        description="Industry news reporting style",
        prompt=(
            "Write an industry news report about this development.\n"
            "Requirements:\n"
            "- Only facts from the article\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji\n"
            "- One HTML <b> tag\n"
            "- No markdown, no links, no signature\n"
            "- Russian language\n\n"
            "Title: {title}\n"
            "Summary: {summary}\n"
            "Content: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
    "tutorial_style": Template(
        id="tutorial_style",
        name="Tutorial Style",
        description="Educational tutorial style",
        prompt=(
            "Write an educational post explaining this concept/tool.\n"
            "Requirements:\n"
            "- Only facts from the article\n"
            "- Length: {min_length}-{max_length} characters\n"
            "- One emoji\n"
            "- One HTML <b> tag\n"
            "- No markdown, no links, no signature\n"
            "- Russian language\n\n"
            "Title: {title}\n"
            "Summary: {summary}\n"
            "Content: {content}"
        ),
        variables=["title", "summary", "content", "min_length", "max_length"],
    ),
}


def get_template(template_id: str) -> Optional[Template]:
    """Get template by ID."""
    return TEMPLATES.get(template_id)


def get_all_templates() -> List[Template]:
    """Get all available templates."""
    return list(TEMPLATES.values())


def get_template_ids() -> List[str]:
    """Get all template IDs."""
    return list(TEMPLATES.keys())