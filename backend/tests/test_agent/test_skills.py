"""Unit tests for QA, Ship30, and Artifact skill behavior."""

from app.agent.skills.artifact_skill import ArtifactSkill
from app.agent.skills.qa_skill import QASkill
from app.agent.skills.ship30_skill import Ship30Skill


def test_qa_skill_formatting():
    skill = QASkill()
    assert skill.name == "qa_skill"
    assert skill.retrieval_top_k == 5
    
    chunks = [
        {"source_file": "ep1.md", "episode_title": "Finding PMF", "speaker": "Rahul Vohra", "content": "Ask users..."}
    ]
    formatted = skill._format_chunks(chunks)
    assert "Rahul Vohra" in formatted
    assert "Finding PMF" in formatted


def test_ship30_intent_detection():
    skill = Ship30Skill()
    assert skill.detect_intent("Write a Ship 30 essay about retention") == 0.9
    assert skill.detect_intent("Create an atomic essay") == 0.9
    assert skill.detect_intent("General question about PMF") == 0.0


def test_artifact_skill_intent():
    skill = ArtifactSkill()
    assert skill.detect_intent("Create an HTML artifact") == 0.85
    assert skill.detect_intent("Generate markdown code") == 0.85
    assert skill.detect_intent("What is growth?") == 0.0
