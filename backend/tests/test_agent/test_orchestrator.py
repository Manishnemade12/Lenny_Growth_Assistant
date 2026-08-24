"""Unit tests for Agent Orchestrator intent classification."""

from app.agent.orchestrator import AgentOrchestrator


def test_intent_classification_qa_default():
    orchestrator = AgentOrchestrator()
    skill = orchestrator.classify_intent("What does Lenny say about PMF?")
    assert skill.name == "qa_skill"


def test_intent_classification_ship30():
    orchestrator = AgentOrchestrator()
    skill = orchestrator.classify_intent("Write a Ship 30 for 30 essay on growth loops")
    assert skill.name == "ship30_skill"


def test_intent_classification_artifact():
    orchestrator = AgentOrchestrator()
    skill = orchestrator.classify_intent("Create an HTML artifact summarizing frameworks")
    assert skill.name == "artifact_skill"
