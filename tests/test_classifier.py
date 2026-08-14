"""Unit tests for the classifier feature.

The LLM call is mocked here — these tests verify prompt construction and
output validation, NOT model quality. Model quality against real inputs is
what Phase 2's golden dataset + Phase 3's eval engine measure. Don't confuse
these two layers of testing.
"""
import pytest
from unittest.mock import patch

from src.classifier import classify_email
from src.models import EmailClassificationOutput
from src.prompt_loader import load_prompt_config, list_prompt_versions


def test_prompt_config_loads():
    config = load_prompt_config("v1")
    assert config.version_id == "v1"
    assert len(config.few_shot_examples) == 2


def test_list_prompt_versions_finds_v1():
    assert "v1" in list_prompt_versions()


@patch("src.classifier.call_llm_json")
def test_classify_email_returns_valid_output(mock_call):
    mock_call.return_value = {
        "category": "billing",
        "summary": "Customer was double-charged and wants a refund.",
    }
    config = load_prompt_config("v1")
    result = classify_email("I was billed twice this month, please fix it.", config)

    assert isinstance(result, EmailClassificationOutput)
    assert result.category == "billing"
    mock_call.assert_called_once()


@patch("src.classifier.call_llm_json")
def test_classify_email_rejects_invalid_category(mock_call):
    mock_call.return_value = {"category": "not_a_real_category", "summary": "test"}
    config = load_prompt_config("v1")

    with pytest.raises(Exception):
        classify_email("some email", config)


@patch("src.classifier.call_llm_json")
def test_classify_email_rejects_missing_summary(mock_call):
    mock_call.return_value = {"category": "billing"}
    config = load_prompt_config("v1")

    with pytest.raises(Exception):
        classify_email("some email", config)
