import pytest
import sys
import types


# Stub out agent_library to avoid heavy dependencies during import
agent_library_stub = types.ModuleType("finrobot.agents.agent_library")
agent_library_stub.library = {}
sys.modules["finrobot.agents.agent_library"] = agent_library_stub

# Stub out toolkits and rag modules to avoid optional dependencies
toolkits_stub = types.ModuleType("finrobot.toolkits")
toolkits_stub.register_toolkits = lambda *args, **kwargs: None
sys.modules["finrobot.toolkits"] = toolkits_stub

rag_stub = types.ModuleType("finrobot.functional.rag")
rag_stub.get_rag_function = lambda *args, **kwargs: (lambda *a, **k: None, object())
sys.modules["finrobot.functional.rag"] = rag_stub

# Relax LLM config validation for tests
from autogen.agentchat.conversable_agent import ConversableAgent

ConversableAgent._validate_llm_config = lambda self, llm_config: llm_config
ConversableAgent._create_client = classmethod(lambda cls, llm_config: None)

from finrobot.agents.workflow import (
    FinRobot,
    SingleAssistant,
    MultiAssistantBase,
)


class DummyMulti(MultiAssistantBase):
    def _get_representative(self):
        return self.user_proxy


def test_finrobot_toolkits_independent():
    r1 = FinRobot({"name": "AgentA"})
    r1.toolkits.append("tool")
    r2 = FinRobot({"name": "AgentB"})
    assert "tool" not in r2.toolkits


def test_singleassistant_configs_independent():
    s1 = SingleAssistant({"name": "AgentA"})
    s1.assistant.llm_config["foo"] = "bar"
    s1.user_proxy._code_execution_config["work_dir"] = "dir1"
    s2 = SingleAssistant({"name": "AgentB"})
    assert "foo" not in s2.assistant.llm_config
    assert s2.user_proxy._code_execution_config["work_dir"] == "coding"


def test_multiassistant_configs_independent():
    group_config1 = {"agents": [{"name": "Worker"}]}
    m1 = DummyMulti(group_config1)
    m1.llm_config["foo"] = "bar"
    m1.user_proxy._code_execution_config["work_dir"] = "dir1"
    m1.agent_configs.append({"name": "Extra"})

    group_config2 = {"agents": [{"name": "Worker"}]}
    m2 = DummyMulti(group_config2)
    assert "foo" not in m2.llm_config
    assert m2.user_proxy._code_execution_config["work_dir"] == "coding"
    assert len(m2.agent_configs) == 1
