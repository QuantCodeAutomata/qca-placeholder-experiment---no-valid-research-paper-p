"""
Tests for placeholder_experiment.experiment
=============================================
Verifies that the placeholder experiment correctly identifies invalid
submissions, produces well-formed reports, and enforces all structural
invariants described in the experiment specification.
"""

from __future__ import annotations

import datetime
import pytest

from placeholder_experiment.experiment import (
    ExperimentStatus,
    PlaceholderExperiment,
    ValidationResult,
    ExperimentMetadata,
    generate_placeholder_report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def default_experiment() -> PlaceholderExperiment:
    """Return a PlaceholderExperiment with default parameters."""
    return PlaceholderExperiment(
        exp_id="exp_1",
        submitted_document_name="DataCamp Scikit-Learn Cheat Sheet",
    )


@pytest.fixture
def custom_experiment() -> PlaceholderExperiment:
    """Return a PlaceholderExperiment with custom parameters."""
    return PlaceholderExperiment(
        exp_id="exp_custom",
        submitted_document_name="Some Random Tutorial Document",
    )


# ---------------------------------------------------------------------------
# Construction & validation tests
# ---------------------------------------------------------------------------


def test_placeholder_experiment_instantiation(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that PlaceholderExperiment instantiates with correct attributes."""
    assert default_experiment.exp_id == "exp_1"
    assert default_experiment.submitted_document_name == "DataCamp Scikit-Learn Cheat Sheet"


def test_placeholder_experiment_repr(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that __repr__ returns a meaningful string."""
    repr_str = repr(default_experiment)
    assert "PlaceholderExperiment" in repr_str
    assert "exp_1" in repr_str
    assert "DataCamp Scikit-Learn Cheat Sheet" in repr_str


def test_invalid_exp_id_raises_value_error() -> None:
    """Test that an empty exp_id raises ValueError."""
    with pytest.raises(ValueError, match="exp_id"):
        PlaceholderExperiment(exp_id="", submitted_document_name="Some Doc")


def test_invalid_document_name_raises_value_error() -> None:
    """Test that an empty submitted_document_name raises ValueError."""
    with pytest.raises(ValueError, match="submitted_document_name"):
        PlaceholderExperiment(exp_id="exp_1", submitted_document_name="")


def test_non_string_exp_id_raises_value_error() -> None:
    """Test that a non-string exp_id raises ValueError."""
    with pytest.raises((ValueError, TypeError)):
        PlaceholderExperiment(exp_id=None, submitted_document_name="Some Doc")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Document validation tests
# ---------------------------------------------------------------------------


def test_validate_submitted_document_returns_validation_result(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that validate_submitted_document returns a ValidationResult."""
    result = default_experiment.validate_submitted_document()
    assert isinstance(result, ValidationResult)


def test_cheat_sheet_is_invalid(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that the DataCamp cheat sheet is correctly identified as invalid."""
    result = default_experiment.validate_submitted_document()
    assert result.is_valid is False


def test_cheat_sheet_document_type_detected(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that the document type is detected for the cheat sheet."""
    result = default_experiment.validate_submitted_document()
    assert result.document_type != "unknown document"
    assert "reference" in result.document_type.lower() or "guide" in result.document_type.lower()


def test_all_required_components_missing(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that all required paper components are listed as missing."""
    result = default_experiment.validate_submitted_document()
    expected_missing = PlaceholderExperiment.REQUIRED_PAPER_COMPONENTS
    for component in expected_missing:
        assert component in result.missing_components, (
            f"Expected '{component}' to be in missing_components"
        )


def test_missing_components_count(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that the number of missing components equals the required count."""
    result = default_experiment.validate_submitted_document()
    assert len(result.missing_components) == len(
        PlaceholderExperiment.REQUIRED_PAPER_COMPONENTS
    )


def test_recommendations_are_non_empty(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that recommendations list is non-empty."""
    result = default_experiment.validate_submitted_document()
    assert len(result.recommendations) > 0


def test_recommendations_mention_resubmission(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that at least one recommendation mentions resubmission."""
    result = default_experiment.validate_submitted_document()
    combined = " ".join(result.recommendations).lower()
    assert "resubmit" in combined or "submit" in combined


def test_tutorial_document_also_invalid(
    custom_experiment: PlaceholderExperiment,
) -> None:
    """Test that a tutorial document is also identified as invalid."""
    result = custom_experiment.validate_submitted_document()
    assert result.is_valid is False


# ---------------------------------------------------------------------------
# Metadata tests
# ---------------------------------------------------------------------------


def test_build_metadata_returns_experiment_metadata(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that build_metadata returns an ExperimentMetadata instance."""
    metadata = default_experiment.build_metadata()
    assert isinstance(metadata, ExperimentMetadata)


def test_metadata_status_is_invalid_input(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that metadata status is INVALID_INPUT for a placeholder."""
    metadata = default_experiment.build_metadata()
    assert metadata.status == ExperimentStatus.INVALID_INPUT


def test_metadata_exp_id_matches(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that metadata exp_id matches the experiment's exp_id."""
    metadata = default_experiment.build_metadata()
    assert metadata.exp_id == default_experiment.exp_id


def test_metadata_title_is_non_empty(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that metadata title is a non-empty string."""
    metadata = default_experiment.build_metadata()
    assert isinstance(metadata.title, str)
    assert len(metadata.title) > 0


def test_metadata_research_objectives_non_empty(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that research objectives list is non-empty."""
    metadata = default_experiment.build_metadata()
    assert len(metadata.research_objectives) > 0


def test_metadata_created_at_is_datetime(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that created_at is a datetime object."""
    metadata = default_experiment.build_metadata()
    assert isinstance(metadata.created_at, datetime.datetime)


# ---------------------------------------------------------------------------
# Report generation tests
# ---------------------------------------------------------------------------


def test_generate_report_returns_dict(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that generate_report returns a dictionary."""
    report = default_experiment.generate_report()
    assert isinstance(report, dict)


def test_report_contains_required_keys(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that the report contains all required top-level keys."""
    report = default_experiment.generate_report()
    required_keys = [
        "experiment_id",
        "title",
        "status",
        "submitted_document",
        "validation",
        "metadata",
        "timestamp",
    ]
    for key in required_keys:
        assert key in report, f"Expected key '{key}' in report"


def test_report_experiment_id_matches(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that report experiment_id matches the experiment's exp_id."""
    report = default_experiment.generate_report()
    assert report["experiment_id"] == "exp_1"


def test_report_status_is_invalid_input(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that report status is 'invalid_input'."""
    report = default_experiment.generate_report()
    assert report["status"] == ExperimentStatus.INVALID_INPUT.value


def test_report_validation_is_not_valid(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that report validation.is_valid is False."""
    report = default_experiment.generate_report()
    assert report["validation"]["is_valid"] is False


def test_report_validation_missing_components_non_empty(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that report validation.missing_components is non-empty."""
    report = default_experiment.generate_report()
    assert len(report["validation"]["missing_components"]) > 0


def test_report_metadata_research_objectives_non_empty(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that report metadata.research_objectives is non-empty."""
    report = default_experiment.generate_report()
    assert len(report["metadata"]["research_objectives"]) > 0


def test_report_timestamp_is_iso_format(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that report timestamp is a valid ISO 8601 string."""
    report = default_experiment.generate_report()
    timestamp = report["timestamp"]
    assert isinstance(timestamp, str)
    # Should parse without error
    parsed = datetime.datetime.fromisoformat(timestamp)
    assert isinstance(parsed, datetime.datetime)


def test_report_submitted_document_matches(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that report submitted_document matches the input."""
    report = default_experiment.generate_report()
    assert report["submitted_document"] == "DataCamp Scikit-Learn Cheat Sheet"


def test_report_is_idempotent(
    default_experiment: PlaceholderExperiment,
) -> None:
    """Test that calling generate_report twice returns consistent results."""
    report1 = default_experiment.generate_report()
    report2 = default_experiment.generate_report()
    # Core fields should be identical (timestamps may differ slightly)
    assert report1["experiment_id"] == report2["experiment_id"]
    assert report1["status"] == report2["status"]
    assert report1["validation"] == report2["validation"]


# ---------------------------------------------------------------------------
# Module-level convenience function tests
# ---------------------------------------------------------------------------


def test_generate_placeholder_report_returns_dict() -> None:
    """Test that generate_placeholder_report returns a dictionary."""
    report = generate_placeholder_report()
    assert isinstance(report, dict)


def test_generate_placeholder_report_default_exp_id() -> None:
    """Test that generate_placeholder_report uses 'exp_1' as default exp_id."""
    report = generate_placeholder_report()
    assert report["experiment_id"] == "exp_1"


def test_generate_placeholder_report_custom_params() -> None:
    """Test that generate_placeholder_report accepts custom parameters."""
    report = generate_placeholder_report(
        exp_id="exp_custom",
        submitted_document_name="Some Tutorial",
    )
    assert report["experiment_id"] == "exp_custom"
    assert report["submitted_document"] == "Some Tutorial"


def test_generate_placeholder_report_status_invalid() -> None:
    """Test that generate_placeholder_report always returns invalid status."""
    report = generate_placeholder_report()
    assert report["status"] == "invalid_input"


# ---------------------------------------------------------------------------
# ExperimentStatus enum tests
# ---------------------------------------------------------------------------


def test_experiment_status_values() -> None:
    """Test that ExperimentStatus enum has expected values."""
    assert ExperimentStatus.PENDING.value == "pending"
    assert ExperimentStatus.INVALID_INPUT.value == "invalid_input"
    assert ExperimentStatus.READY.value == "ready"
    assert ExperimentStatus.COMPLETED.value == "completed"


def test_experiment_status_invalid_input_is_not_completed() -> None:
    """Test that INVALID_INPUT is distinct from COMPLETED."""
    assert ExperimentStatus.INVALID_INPUT != ExperimentStatus.COMPLETED


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


def test_single_character_exp_id() -> None:
    """Test that a single-character exp_id is accepted."""
    exp = PlaceholderExperiment(exp_id="x", submitted_document_name="Doc")
    assert exp.exp_id == "x"


def test_very_long_document_name() -> None:
    """Test that a very long document name is handled gracefully."""
    long_name = "A" * 1000
    exp = PlaceholderExperiment(exp_id="exp_long", submitted_document_name=long_name)
    report = exp.generate_report()
    assert report["submitted_document"] == long_name


def test_document_name_with_special_characters() -> None:
    """Test that document names with special characters are handled."""
    special_name = "Paper: α-β Analysis (2024) — Vol. 1"
    exp = PlaceholderExperiment(
        exp_id="exp_special", submitted_document_name=special_name
    )
    report = exp.generate_report()
    assert report["submitted_document"] == special_name


def test_multiple_experiments_are_independent() -> None:
    """Test that multiple PlaceholderExperiment instances are independent."""
    exp_a = PlaceholderExperiment(exp_id="exp_a", submitted_document_name="Doc A")
    exp_b = PlaceholderExperiment(exp_id="exp_b", submitted_document_name="Doc B")

    report_a = exp_a.generate_report()
    report_b = exp_b.generate_report()

    assert report_a["experiment_id"] == "exp_a"
    assert report_b["experiment_id"] == "exp_b"
    assert report_a["submitted_document"] == "Doc A"
    assert report_b["submitted_document"] == "Doc B"


def test_required_paper_components_is_non_empty() -> None:
    """Test that REQUIRED_PAPER_COMPONENTS class attribute is non-empty."""
    assert len(PlaceholderExperiment.REQUIRED_PAPER_COMPONENTS) > 0


def test_invalid_document_signatures_is_non_empty() -> None:
    """Test that INVALID_DOCUMENT_SIGNATURES class attribute is non-empty."""
    assert len(PlaceholderExperiment.INVALID_DOCUMENT_SIGNATURES) > 0


def test_cheat_sheet_signature_in_invalid_signatures() -> None:
    """Test that 'cheat sheet' is in INVALID_DOCUMENT_SIGNATURES."""
    signatures = {k.lower() for k in PlaceholderExperiment.INVALID_DOCUMENT_SIGNATURES}
    assert any("cheat sheet" in sig for sig in signatures)
