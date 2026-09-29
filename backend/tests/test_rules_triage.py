import pytest

from app.providers.triage.rules import RuleBasedTriage
from app.schemas import Category, Priority


@pytest.mark.parametrize(
    ("text", "category"),
    [
        ("Pani pipe is leaking outside our house.", Category.water),
        ("Bijli transformer is sparking near the market.", Category.electricity),
        ("Kooda has not been collected from this lane.", Category.sanitation),
        ("A pothole has damaged the road outside school.", Category.roads),
        ("The street light is off and the lane is dark.", Category.streetlights),
        ("Stray animals are creating a problem in the park.", Category.other),
    ],
)
def test_rules_classifies_municipal_categories(text, category):
    result = RuleBasedTriage().triage(text, "Block A")

    assert result.category is category


@pytest.mark.parametrize(
    ("text", "priority"),
    [
        ("A burst pipe is flooding the road.", Priority.high),
        ("Please repair this minor pothole when possible.", Priority.low),
        ("The public tap has been leaking since morning.", Priority.normal),
    ],
)
def test_rules_assigns_predictable_priorities(text, priority):
    result = RuleBasedTriage().triage(text, "Block A")

    assert result.priority is priority


def test_rules_normalizes_and_limits_its_summary_without_changing_classification():
    text = "Water pipe leak " + "near the school " * 20

    result = RuleBasedTriage().triage(text, "Block A")

    assert result.category is Category.water
    assert len(result.summary) == 140
    assert "  " not in result.summary
