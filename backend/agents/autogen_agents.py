"""AutoGen multi-agent setup used by Agentic RAG: Planner, Retriever, Critic, Writer.

Falls back to a plain sequential simulation of the same roles (no `pyautogen` dependency
required) so the Agentic RAG demo works even without the package installed/configured.
"""
from __future__ import annotations

from dataclasses import dataclass

from backend.llm_client import claude_client
from backend.rag.base import RetrievedChunk


@dataclass
class AgentStep:
    agent: str
    output: str


def _try_build_autogen_agents():
    try:
        import autogen  # noqa: F401

        return True
    except Exception:
        return False


AUTOGEN_AVAILABLE = _try_build_autogen_agents()


def run_agent_pipeline(query: str, chunks: list[RetrievedChunk]) -> list[AgentStep]:
    """Simulates a 4-agent AutoGen-style conversation: Planner -> Retriever-critic -> Writer -> Critic.

    When `pyautogen` + real Claude credentials are configured, this could be swapped for an
    actual `autogen.GroupChat` with each agent backed by a Claude-powered `ConversableAgent`.
    The role decomposition and prompt structure below mirrors that real AutoGen topology.
    """
    context = "\n".join(f"- [{c.document.title}] {c.document.text}" for c in chunks)
    steps: list[AgentStep] = []

    planner_prompt = (
        f"You are the Planner agent. Question: {query}\n"
        "Break this into 2-3 sub-questions needed to answer it fully."
    )
    plan = claude_client.generate(planner_prompt, max_tokens=200)
    steps.append(AgentStep(agent="Planner", output=plan))

    retriever_critic_prompt = (
        f"You are the Retriever-Critic agent. Sub-questions:\n{plan}\n\n"
        f"Available evidence:\n{context}\n\n"
        "Judge whether the evidence is sufficient to answer each sub-question; flag any gaps."
    )
    critique = claude_client.generate(retriever_critic_prompt, max_tokens=200)
    steps.append(AgentStep(agent="Retriever-Critic", output=critique))

    writer_prompt = (
        f"You are the Writer agent. Question: {query}\nPlan:\n{plan}\n"
        f"Evidence sufficiency notes:\n{critique}\nEvidence:\n{context}\n\n"
        "Write the best possible grounded answer given all of the above."
    )
    draft_answer = claude_client.generate(writer_prompt, max_tokens=400)
    steps.append(AgentStep(agent="Writer", output=draft_answer))

    final_critic_prompt = (
        f"You are the final Critic agent. Review this draft answer for accuracy and "
        f"whether it is fully grounded in the evidence. Draft:\n{draft_answer}\n\n"
        "If it's good, restate it as the final answer. If not, correct it."
    )
    final_answer = claude_client.generate(final_critic_prompt, max_tokens=400)
    steps.append(AgentStep(agent="Critic (final)", output=final_answer))

    return steps
