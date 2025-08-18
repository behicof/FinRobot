from finrobot.agents.workflow import FinRobot, SingleAssistant
from autogen.agentchat.conversable_agent import ConversableAgent


def _dummy_validate(self, llm_config):
    return llm_config or {}


def _dummy_create_client(self, llm_config):
    return None


ConversableAgent._validate_llm_config = _dummy_validate
ConversableAgent._create_client = _dummy_create_client


def make_config(name: str):
    return {"name": name, "description": "desc"}


def test_instances_do_not_share_state():
    robot_a = FinRobot(make_config("A"))
    robot_b = FinRobot(make_config("B"))

    robot_a.toolkits.append("demo_tool")
    assert robot_b.toolkits == []

    assistant_a = SingleAssistant(make_config("C"))
    assistant_b = SingleAssistant(make_config("D"))

    assistant_a.assistant.llm_config["foo"] = "bar"
    assert "foo" not in assistant_b.assistant.llm_config

    assistant_a.user_proxy._code_execution_config["work_dir"] = "other"
    assert assistant_b.user_proxy._code_execution_config["work_dir"] == "coding"
