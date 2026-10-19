import pytest

from streamlit_app import _fire_tv_arguments, _simulated_agent_result


def test_fire_tv_arguments_reads_bedrock_tool_result():
    result = {
        "tool": "trigger_fire_tv",
        "arguments": {
            "action": "play_calming_content",
            "protocol": "alexa",
        },
    }

    assert _fire_tv_arguments(result) == {
        "action": "play_calming_content",
        "protocol": "alexa",
    }


def test_fire_tv_arguments_ignores_non_fire_tv_results():
    assert _fire_tv_arguments("No intervention needed") is None
    assert _fire_tv_arguments({"tool": "other_tool", "arguments": {}}) is None


def test_fire_tv_arguments_rejects_malformed_tool_requests():
    with pytest.raises(ValueError, match="arguments object"):
        _fire_tv_arguments({"tool": "trigger_fire_tv"})


@pytest.mark.parametrize(
    ("biometric_state", "context_state", "should_intervene"),
    [
        ("critical", "sedentary", True),
        ("elevated", "sedentary", True),
        ("critical", "active", False),
        ("calm", "sedentary", False),
    ],
)
def test_simulated_agent_result_preserves_intervention_rule(
    biometric_state, context_state, should_intervene
):
    result = _simulated_agent_result(biometric_state, context_state)

    assert (_fire_tv_arguments(result) is not None) is should_intervene
