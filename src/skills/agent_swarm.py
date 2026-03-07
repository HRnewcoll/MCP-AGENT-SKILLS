"""Agent Swarm (Company) skill – spin up a virtual AI company from a single prompt.

Given a goal (e.g. "build a website"), this skill automatically assembles a
company-like structure of AI agent *profiles* with appropriate roles, seniority
levels and tasks.  All state is stored locally as JSON – no external API is
required.

Supported actions
-----------------
create_company  goal=<str>
    Bootstrap a company tailored to *goal*.  Clears any existing company.
list_agents
    Return a formatted list of every agent and their current task.
get_agent       agent_id=<int>
    Show full profile for the agent with the given numeric ID.
add_agents      role=<str>  [count=<int>]  [level=<str>]
    Add *count* (default 1) new agents with *role* and optional *level*
    (junior / mid / senior / lead).  Useful for growing the company later.
assign_task     agent_id=<int>  task=<str>
    Assign a new task description to the specified agent.
complete_task   agent_id=<int>
    Mark the agent's current task as completed.
status
    Show a high-level summary of the company's progress.
clear
    Remove all agents and reset the company.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

# ---------------------------------------------------------------------------
# Role templates used when auto-generating a company
# ---------------------------------------------------------------------------

# Maps a keyword (found in the goal) → list of (role, level) tuples to include.
_ROLE_KEYWORD_MAP: dict[str, list[tuple[str, str]]] = {
    "website": [
        ("CEO", "lead"),
        ("Project Manager", "senior"),
        ("Frontend Developer", "senior"),
        ("Frontend Developer", "junior"),
        ("Backend Developer", "senior"),
        ("Backend Developer", "junior"),
        ("UI/UX Designer", "senior"),
        ("QA Tester", "mid"),
        ("DevOps Engineer", "mid"),
    ],
    "app": [
        ("CEO", "lead"),
        ("Project Manager", "senior"),
        ("Mobile Developer", "senior"),
        ("Mobile Developer", "junior"),
        ("Backend Developer", "senior"),
        ("QA Tester", "mid"),
        ("UI/UX Designer", "mid"),
    ],
    "market": [
        ("CMO", "lead"),
        ("Marketing Strategist", "senior"),
        ("Copywriter", "mid"),
        ("SEO Specialist", "mid"),
        ("Social Media Manager", "junior"),
        ("Data Analyst", "mid"),
    ],
    "security": [
        ("CISO", "lead"),
        ("Penetration Tester", "senior"),
        ("Penetration Tester", "junior"),
        ("Security Analyst", "senior"),
        ("DevSecOps Engineer", "mid"),
    ],
    "data": [
        ("Chief Data Officer", "lead"),
        ("Data Scientist", "senior"),
        ("Data Engineer", "senior"),
        ("Data Analyst", "mid"),
        ("ML Engineer", "mid"),
    ],
    "game": [
        ("Game Director", "lead"),
        ("Game Developer", "senior"),
        ("Game Developer", "junior"),
        ("Level Designer", "mid"),
        ("QA Tester", "mid"),
        ("Sound Designer", "junior"),
    ],
}

# Default company structure when no keyword matches.
_DEFAULT_ROLES: list[tuple[str, str]] = [
    ("CEO", "lead"),
    ("Project Manager", "senior"),
    ("Senior Developer", "senior"),
    ("Developer", "mid"),
    ("Junior Developer", "junior"),
    ("QA Tester", "mid"),
    ("Technical Writer", "junior"),
]

# First names used when auto-generating agent names.
_FIRST_NAMES = [
    "Alex", "Sam", "Jordan", "Taylor", "Morgan",
    "Casey", "Riley", "Drew", "Quinn", "Avery",
    "Blake", "Reese", "Sage", "Hayden", "Finley",
    "Dakota", "Cameron", "Emery", "Logan", "Peyton",
]


def _generate_name(index: int) -> str:
    return _FIRST_NAMES[index % len(_FIRST_NAMES)]


# ---------------------------------------------------------------------------
# TypedDicts
# ---------------------------------------------------------------------------

class _AgentProfile(TypedDict):
    id: int
    name: str
    role: str
    level: str          # junior | mid | senior | lead
    status: str         # idle | busy | completed
    current_task: str
    tasks_completed: int
    joined_at: str


class _Company(TypedDict):
    goal: str
    created_at: str
    agents: list[_AgentProfile]


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------

class AgentSwarmSkill:
    """Spawn and manage a virtual AI company (agent swarm) for any goal."""

    name = "agent_swarm"
    description = (
        "Manage a virtual AI company (agent swarm). "
        "Supported actions: 'create_company' (goal=<str>) – auto-build a team; "
        "'list_agents' – show all agents; 'get_agent' (agent_id=<int>) – profile; "
        "'add_agents' (role=<str>, count=<int>, level=<str>) – grow the team; "
        "'assign_task' (agent_id=<int>, task=<str>) – give an agent a task; "
        "'complete_task' (agent_id=<int>) – mark task done; "
        "'status' – company overview; 'clear' – reset company."
    )

    def __init__(self, store_path: str | os.PathLike = ".agent_swarm.json") -> None:
        self._path = Path(store_path)
        self._company: _Company = self._load()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        action: str,
        goal: str = "",
        agent_id: int = 0,
        role: str = "",
        level: str = "mid",
        count: int = 1,
        task: str = "",
    ) -> str:
        """
        Perform an agent swarm operation.

        Parameters
        ----------
        action:
            One of ``"create_company"``, ``"list_agents"``, ``"get_agent"``,
            ``"add_agents"``, ``"assign_task"``, ``"complete_task"``,
            ``"status"``, ``"clear"``.
        goal:
            Goal / task description (required for *create_company*).
        agent_id:
            Numeric agent ID (required for *get_agent*, *assign_task*,
            *complete_task*).
        role:
            Agent role string (required for *add_agents*).
        level:
            Seniority level – ``"junior"``, ``"mid"``, ``"senior"``, or
            ``"lead"`` (optional for *add_agents*; defaults to ``"mid"``).
        count:
            Number of agents to add (optional for *add_agents*; defaults
            to ``1``).
        task:
            Task description (required for *assign_task*).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()
        if action == "create_company":
            return self._create_company(goal)
        if action == "list_agents":
            return self._list_agents()
        if action == "get_agent":
            return self._get_agent(agent_id)
        if action == "add_agents":
            return self._add_agents(role, level, count)
        if action == "assign_task":
            return self._assign_task(agent_id, task)
        if action == "complete_task":
            return self._complete_task(agent_id)
        if action == "status":
            return self._status()
        if action == "clear":
            return self._clear()
        return (
            f"Error: unknown action {action!r}. "
            "Use create_company, list_agents, get_agent, add_agents, "
            "assign_task, complete_task, status, or clear."
        )

    # ------------------------------------------------------------------
    # Action implementations
    # ------------------------------------------------------------------

    def _create_company(self, goal: str) -> str:
        if not goal:
            return "Error: goal is required for create_company"
        roles = self._pick_roles(goal)
        now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        agents: list[_AgentProfile] = []
        for idx, (role, lv) in enumerate(roles):
            agents.append({
                "id": idx + 1,
                "name": _generate_name(idx),
                "role": role,
                "level": lv,
                "status": "idle",
                "current_task": "",
                "tasks_completed": 0,
                "joined_at": now,
            })
        self._company = {"goal": goal, "created_at": now, "agents": agents}
        self._save()
        lines = [
            f"Company created for goal: {goal!r}",
            f"Team size: {len(agents)} agents",
            "",
        ]
        for a in agents:
            lines.append(f"  #{a['id']} {a['name']} – {a['level'].capitalize()} {a['role']}")
        return "\n".join(lines)

    def _list_agents(self) -> str:
        agents = self._company.get("agents", [])
        if not agents:
            return "(no agents – use create_company first)"
        lines = [f"Company goal: {self._company.get('goal', '(none)')}"]
        lines.append(f"{'ID':<4} {'Name':<10} {'Role':<25} {'Level':<8} {'Status':<10} Task")
        lines.append("-" * 80)
        for a in agents:
            task = a["current_task"] if a["current_task"] else "(idle)"
            lines.append(
                f"#{a['id']:<3} {a['name']:<10} {a['role']:<25} {a['level']:<8} "
                f"{a['status']:<10} {task}"
            )
        return "\n".join(lines)

    def _get_agent(self, agent_id: int) -> str:
        agent = self._find(agent_id)
        if agent is None:
            return f"Error: agent #{agent_id} not found"
        lines = [
            f"Agent #{agent['id']}",
            f"  Name            : {agent['name']}",
            f"  Role            : {agent['role']}",
            f"  Level           : {agent['level']}",
            f"  Status          : {agent['status']}",
            f"  Current task    : {agent['current_task'] or '(none)'}",
            f"  Tasks completed : {agent['tasks_completed']}",
            f"  Joined          : {agent['joined_at']}",
        ]
        return "\n".join(lines)

    def _add_agents(self, role: str, level: str, count: int) -> str:
        if not role:
            return "Error: role is required for add_agents"
        if count < 1:
            return "Error: count must be at least 1"
        valid_levels = {"junior", "mid", "senior", "lead"}
        if level not in valid_levels:
            level = "mid"
        agents = self._company.setdefault("agents", [])
        if "goal" not in self._company:
            self._company["goal"] = ""
        if "created_at" not in self._company:
            self._company["created_at"] = datetime.now(tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        start_id = max((a["id"] for a in agents), default=0) + 1
        now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        added = []
        for i in range(count):
            agent: _AgentProfile = {
                "id": start_id + i,
                "name": _generate_name(start_id + i - 1),
                "role": role,
                "level": level,
                "status": "idle",
                "current_task": "",
                "tasks_completed": 0,
                "joined_at": now,
            }
            agents.append(agent)
            added.append(agent)
        self._save()
        summary = ", ".join(f"#{a['id']} {a['name']}" for a in added)
        return f"Added {count} {level} {role}(s): {summary}"

    def _assign_task(self, agent_id: int, task: str) -> str:
        if not agent_id:
            return "Error: agent_id is required"
        if not task:
            return "Error: task is required"
        agent = self._find(agent_id)
        if agent is None:
            return f"Error: agent #{agent_id} not found"
        agent["current_task"] = task
        agent["status"] = "busy"
        self._save()
        return f"Assigned to #{agent_id} {agent['name']}: {task!r}"

    def _complete_task(self, agent_id: int) -> str:
        if not agent_id:
            return "Error: agent_id is required"
        agent = self._find(agent_id)
        if agent is None:
            return f"Error: agent #{agent_id} not found"
        if not agent["current_task"]:
            return f"Error: agent #{agent_id} has no active task"
        completed = agent["current_task"]
        agent["current_task"] = ""
        agent["status"] = "idle"
        agent["tasks_completed"] += 1
        self._save()
        return (
            f"Agent #{agent_id} {agent['name']} completed task: {completed!r} "
            f"(total: {agent['tasks_completed']})"
        )

    def _status(self) -> str:
        agents = self._company.get("agents", [])
        goal = self._company.get("goal", "(none)")
        total = len(agents)
        busy = sum(1 for a in agents if a["status"] == "busy")
        idle = sum(1 for a in agents if a["status"] == "idle")
        done_tasks = sum(a["tasks_completed"] for a in agents)
        lines = [
            f"Company status",
            f"  Goal            : {goal}",
            f"  Total agents    : {total}",
            f"  Busy            : {busy}",
            f"  Idle            : {idle}",
            f"  Tasks completed : {done_tasks}",
        ]
        return "\n".join(lines)

    def _clear(self) -> str:
        count = len(self._company.get("agents", []))
        self._company = {"goal": "", "created_at": "", "agents": []}
        self._save()
        return f"Company cleared ({count} agents removed)"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pick_roles(goal: str) -> list[tuple[str, str]]:
        goal_lower = goal.lower()
        for keyword, roles in _ROLE_KEYWORD_MAP.items():
            if keyword in goal_lower:
                return roles
        return _DEFAULT_ROLES

    def _find(self, agent_id: int) -> _AgentProfile | None:
        for a in self._company.get("agents", []):
            if a["id"] == agent_id:
                return a
        return None

    def _load(self) -> _Company:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data  # type: ignore[return-value]
            except (json.JSONDecodeError, OSError):
                pass
        return {"goal": "", "created_at": "", "agents": []}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._company, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
