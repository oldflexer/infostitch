"""Unit tests for Template value object."""
from __future__ import annotations

import pytest

from domain.value_objects.template import Template, get_template, get_all_templates, get_template_ids


class TestTemplate:
    """Tests for Template value object."""

    def test_create_template(self):
        """Test creating a template with valid data."""
        template = Template(
            id="test_template",
            name="Test Template",
            prompt="Write a post about {title}. Summary: {summary}",
            description="Test template",
            variables=["title", "summary"],
            min_length=100,
            max_length=200,
        )
        
        assert template.id == "test_template"
        assert template.name == "Test Template"
        assert template.prompt == "Write a post about {title}. Summary: {summary}"
        assert template.description == "Test template"
        assert template.variables == ["title", "summary"]
        assert template.min_length == 100
        assert template.max_length == 200

    def test_format_prompt(self):
        """Test formatting prompt with variables."""
        template = Template(
            id="test",
            name="Test",
            prompt="Title: {title}\nSummary: {summary}\nContent: {content}",
            variables=["title", "summary", "content"],
        )
        
        result = template.format_prompt(
            title="Test Title",
            summary="Test Summary",
            content="Test Content",
        )
        
        assert "Title: Test Title" in result
        assert "Summary: Test Summary" in result
        assert "Content: Test Content" in result

    def test_format_prompt_missing_variable_raises(self):
        """Test that missing variable raises ValueError."""
        template = Template(
            id="test",
            name="Test",
            prompt="Title: {title}\nSummary: {summary}",
            variables=["title", "summary"],
        )
        
        with pytest.raises(ValueError, match="Missing template variable"):
            template.format_prompt(title="Test Title")

    def test_validate_variables(self):
        """Test validating provided variables."""
        template = Template(
            id="test",
            name="Test",
            prompt="Title: {title}\nSummary: {summary}\nContent: {content}",
            variables=["title", "summary", "content"],
        )
        
        # All provided
        missing = template.validate_variables({"title": "T", "summary": "S", "content": "C"})
        assert missing == []
        
        # Some missing
        missing = template.validate_variables({"title": "T"})
        assert "summary" in missing
        assert "content" in missing
        assert len(missing) == 2

    def test_validation_empty_id_raises(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Template ID cannot be empty"):
            Template(
                id="",
                name="Test",
                prompt="Test {title}",
                variables=["title"],
            )

    def test_validation_empty_name_raises(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Template name cannot be empty"):
            Template(
                id="test",
                name="",
                prompt="Test {title}",
                variables=["title"],
            )

    def test_validation_empty_prompt_raises(self):
        """Test that empty prompt raises ValueError."""
        with pytest.raises(ValueError, match="Template prompt cannot be empty"):
            Template(
                id="test",
                name="Test",
                prompt="",
                variables=["title"],
            )


class TestTemplateRegistry:
    """Tests for template registry functions."""

    def test_get_template_exists(self):
        """Test getting existing template."""
        template = get_template("news_brief")
        
        assert template is not None
        assert template.id == "news_brief"
        assert template.name == "News Brief"

    def test_get_template_not_exists(self):
        """Test getting non-existing template returns None."""
        template = get_template("non_existent")
        assert template is None

    def test_get_all_templates(self):
        """Test getting all templates."""
        templates = get_all_templates()
        
        assert len(templates) == 10
        assert all(isinstance(t, Template) for t in templates)

    def test_get_template_ids(self):
        """Test getting all template IDs."""
        ids = get_template_ids()
        
        assert len(ids) == 10
        assert "news_brief" in ids
        assert "deep_dive" in ids
        assert "quick_take" in ids