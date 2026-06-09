"""
Multi-Agent Coordinator implementation
"""

import logging
from typing import List, Union, Generator

from crewai import Task, Crew

from src.agents.modes import CoordinationMode
from src.agents.configurable_agent import ConfigurableAgent

logger = logging.getLogger(__name__)


class MultiAgentCoordinator:
    """Coordinates multiple agents in different collaboration modes"""

    def __init__(self, agents: List[ConfigurableAgent]):
        self.agents = agents
        if len(agents) < 2:
            raise ValueError("Multi-agent coordination requires at least 2 agents")

    def coordinate(
        self, mode: CoordinationMode, query: str, stream: bool = False, **kwargs
    ) -> Union[str, Generator[str, None, None]]:
        """Coordinate agents based on the specified mode"""
        if mode == CoordinationMode.PIPELINE:
            return self._pipeline_mode(query, stream)
        elif mode == CoordinationMode.ENSEMBLE:
            return self._ensemble_mode(query, stream)
        elif mode == CoordinationMode.DEBATE:
            rebuttal_limit = kwargs.get('rebuttal_limit', 3)
            return self._debate_mode(query, stream, rebuttal_limit)
        elif mode == CoordinationMode.SWARM:
            return self._swarm_mode(query, stream)
        elif mode == CoordinationMode.HIERARCHICAL:
            return self._hierarchical_mode(query, stream)
        else:
            raise ValueError(f"Unknown coordination mode: {mode}")

    def coordinate_with_history(
        self, mode: CoordinationMode, query: str, **kwargs
    ) -> dict:
        """Coordinate agents and return full conversation history"""
        if mode == CoordinationMode.PIPELINE:
            return self._pipeline_mode_with_history(query)
        elif mode == CoordinationMode.ENSEMBLE:
            return self._ensemble_mode_with_history(query)
        elif mode == CoordinationMode.DEBATE:
            rebuttal_limit = kwargs.get('rebuttal_limit', 3)
            return self._debate_mode_with_history(query, rebuttal_limit)
        elif mode == CoordinationMode.SWARM:
            return self._swarm_mode_with_history(query)
        elif mode == CoordinationMode.HIERARCHICAL:
            return self._hierarchical_mode_with_history(query)
        else:
            raise ValueError(f"Unknown coordination mode: {mode}")

    def _pipeline_mode(
        self, query: str, stream: bool
    ) -> Union[str, Generator[str, None, None]]:
        """Sequential processing through agents"""
        current_input = query
        for i, agent in enumerate(self.agents):
            logger.info(f"Pipeline step {i + 1}: {agent.role}")
            result = agent.process_request(current_input, stream=False, agent_id=agent.role)
            current_input = result if isinstance(result, str) else str(result)
        return current_input

    def _pipeline_mode_with_history(self, query: str) -> dict:
        """Sequential processing with full history"""
        conversation = []
        current_input = query
        for i, agent in enumerate(self.agents):
            logger.info(f"Pipeline step {i + 1}: {agent.role}")
            result = agent.process_request(current_input, stream=False, agent_id=agent.role)
            conversation.append({
                "agent": agent.role,
                "step": i + 1,
                "input": current_input,
                "response": result if isinstance(result, str) else str(result)
            })
            current_input = result if isinstance(result, str) else str(result)
        return {
            "conversation": conversation,
            "final_response": current_input
        }

    def _ensemble_mode(
        self, query: str, stream: bool
    ) -> Union[str, Generator[str, None, None]]:
        """Parallel processing with synthesis"""
        # Run all agents in parallel (simulated)
        responses = []
        for agent in self.agents:
            response = agent.process_request(query, stream=False, agent_id=agent.role)
            responses.append(f"{agent.role}: {response}")

        # Create synthesis prompt
        synthesis_prompt = f"""Synthesize the following responses into a coherent answer:

{chr(10).join(responses)}

Provide a unified response that combines the best insights from all perspectives."""

        # Use the first agent as synthesizer
        return self.agents[0].process_request(synthesis_prompt, stream=stream, agent_id=f"{self.agents[0].role} (Synthesizer)")

    def _ensemble_mode_with_history(self, query: str) -> dict:
        """Parallel processing with full history"""
        conversation = []
        responses = []
        
        for agent in self.agents:
            response = agent.process_request(query, stream=False, agent_id=agent.role)
            conversation.append({
                "agent": agent.role,
                "phase": "individual_response",
                "response": response
            })
            responses.append(f"{agent.role}: {response}")

        # Create synthesis prompt
        synthesis_prompt = f"""Synthesize the following responses into a coherent answer:

{chr(10).join(responses)}

Provide a unified response that combines the best insights from all perspectives."""

        synthesis = self.agents[0].process_request(synthesis_prompt, stream=False, agent_id=f"{self.agents[0].role} (Synthesizer)")
        conversation.append({
            "agent": self.agents[0].role,
            "phase": "synthesis",
            "response": synthesis
        })
        
        return {
            "conversation": conversation,
            "final_response": synthesis
        }

    def _debate_mode(
        self, query: str, stream: bool, rebuttal_limit: int = 3
    ) -> Union[str, Generator[str, None, None]]:
        """Agents debate the topic with back-and-forth"""
        debate_history = [f"Topic: {query}"]
        rounds = rebuttal_limit  # Number of debate rounds

        for round_num in range(rounds):
            for i, agent in enumerate(self.agents):
                opponent_views = [
                    f"Agent {j + 1}: {debate_history[-1]}"
                    for j in range(len(self.agents))
                    if j != i
                ]
                debate_prompt = f"""You are {agent.role}. The debate topic is: {query}

Previous arguments:
{chr(10).join(debate_history[-len(self.agents) :])}

Provide your counter-argument or rebuttal."""

                response = agent.process_request(debate_prompt, stream=False, agent_id=agent.role)
                debate_history.append(f"{agent.role}: {response}")

        # Final synthesis
        final_prompt = f"""Debate summary:
{chr(10).join(debate_history)}

Provide a final conclusion based on this debate."""
        return self.agents[0].process_request(final_prompt, stream=stream, agent_id=f"{self.agents[0].role} (Conclusion)")

    def _debate_mode_with_history(self, query: str, rebuttal_limit: int = 3) -> dict:
        """Debate mode with full history"""
        conversation = []
        debate_history = [f"Topic: {query}"]
        rounds = rebuttal_limit

        for round_num in range(rounds):
            for i, agent in enumerate(self.agents):
                debate_prompt = f"""You are {agent.role}. The debate topic is: {query}

Previous arguments:
{chr(10).join(debate_history[-len(self.agents) :])}

Provide your counter-argument or rebuttal."""

                response = agent.process_request(debate_prompt, stream=False, agent_id=agent.role)
                debate_history.append(f"{agent.role}: {response}")
                conversation.append({
                    "agent": agent.role,
                    "round": round_num + 1,
                    "phase": "debate",
                    "response": response
                })

        # Final synthesis
        final_prompt = f"""Debate summary:
{chr(10).join(debate_history)}

Provide a final conclusion based on this debate."""
        synthesis = self.agents[0].process_request(final_prompt, stream=False, agent_id=f"{self.agents[0].role} (Conclusion)")
        conversation.append({
            "agent": self.agents[0].role,
            "phase": "conclusion",
            "response": synthesis
        })
        
        return {
            "conversation": conversation,
            "final_response": synthesis
        }

    def _swarm_mode(
        self, query: str, stream: bool
    ) -> Union[str, Generator[str, None, None]]:
        """Swarm intelligence - all agents work together"""
        # Create a crew with all agents
        task = Task(
            description=query,
            expected_output="A collaborative response from the swarm.",
        )

        crew = Crew(
            agents=[agent.agent for agent in self.agents],
            tasks=[task],
            verbose=not stream,
        )

        result = crew.kickoff()
        response_text = getattr(result, "raw", getattr(result, "output", str(result)))  # type: ignore
        return response_text

    def _swarm_mode_with_history(self, query: str) -> dict:
        """Swarm mode with history"""
        task = Task(
            description=query,
            expected_output="A collaborative response from the swarm.",
        )

        crew = Crew(
            agents=[agent.agent for agent in self.agents],
            tasks=[task],
            verbose=True,
        )

        result = crew.kickoff()
        response_text = getattr(result, "raw", getattr(result, "output", str(result)))
        
        # Swarm mode doesn't have clear individual responses
        return {
            "conversation": [{
                "agent": "Swarm (Collaborative)",
                "phase": "collaborative",
                "response": response_text
            }],
            "final_response": response_text
        }

    def _hierarchical_mode(
        self, query: str, stream: bool
    ) -> Union[str, Generator[str, None, None]]:
        """Hierarchical coordination with manager and specialists"""
        manager = self.agents[0]  # First agent is manager
        specialists = self.agents[1:]

        # Manager delegates to specialists
        delegation_prompt = f"""As a manager, analyze this query and delegate to specialists: {query}

Available specialists:
{chr(10).join(f"- {agent.role}: {agent.goal}" for agent in specialists)}

Create subtasks for the specialists."""

        delegation = manager.process_request(delegation_prompt, stream=False, agent_id=f"{manager.role} (Manager)")

        # Specialists work on subtasks
        specialist_responses = []
        for specialist in specialists:
            specialist_prompt = f"""You are {specialist.role}. Your task: {delegation}

Original query: {query}

Provide your specialized analysis."""
            response = specialist.process_request(specialist_prompt, stream=False, agent_id=specialist.role)
            specialist_responses.append(f"{specialist.role}: {response}")

        # Manager synthesizes
        synthesis_prompt = f"""As manager, synthesize these specialist responses into a final answer:

{chr(10).join(specialist_responses)}

Original query: {query}"""

        return manager.process_request(synthesis_prompt, stream=stream, agent_id=f"{manager.role} (Manager)")

    def _hierarchical_mode_with_history(self, query: str) -> dict:
        """Hierarchical mode with full history"""
        conversation = []
        manager = self.agents[0]
        specialists = self.agents[1:]

        # Manager delegates
        delegation_prompt = f"""As a manager, analyze this query and delegate to specialists: {query}

Available specialists:
{chr(10).join(f"- {agent.role}: {agent.goal}" for agent in specialists)}

Create subtasks for the specialists."""

        delegation = manager.process_request(delegation_prompt, stream=False, agent_id=f"{manager.role} (Manager)")
        conversation.append({
            "agent": f"{manager.role} (Manager)",
            "phase": "delegation",
            "response": delegation
        })

        # Specialists work
        specialist_responses = []
        for specialist in specialists:
            specialist_prompt = f"""You are {specialist.role}. Your task: {delegation}

Original query: {query}

Provide your specialized analysis."""
            response = specialist.process_request(specialist_prompt, stream=False, agent_id=specialist.role)
            specialist_responses.append(f"{specialist.role}: {response}")
            conversation.append({
                "agent": specialist.role,
                "phase": "specialist_work",
                "response": response
            })

        # Manager synthesizes
        synthesis_prompt = f"""As manager, synthesize these specialist responses into a final answer:

{chr(10).join(specialist_responses)}

Original query: {query}"""

        synthesis = manager.process_request(synthesis_prompt, stream=False, agent_id=f"{manager.role} (Manager)")
        conversation.append({
            "agent": f"{manager.role} (Manager)",
            "phase": "synthesis",
            "response": synthesis
        })
        
        return {
            "conversation": conversation,
            "final_response": synthesis
        }
