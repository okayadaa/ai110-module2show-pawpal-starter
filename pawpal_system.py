"""
pawpal_system.py
Core domain classes and scheduling logic for PawPal+.

UML summary
-----------
<<dataclass>> Task
    - title: str
    - duration_minutes: int
    - priority: str          # "low" | "medium" | "high"
    - category: str          # "feeding" | "walk" | "meds" | "grooming" | "enrichment" | "other"
    - notes: str

<<dataclass>> Pet
    - name: str
    - species: str           # "dog" | "cat" | "other"
    - age_years: float
    - special_needs: list[str]

Owner
    - name: str
    - pet: Pet
    - available_minutes: int
    - preferred_start_time: str  # e.g. "08:00"
    + add_task(task: Task) -> None
    + remove_task(title: str) -> bool
    + get_tasks() -> list[Task]

ScheduledTask
    - task: Task
    - start_time: str
    - end_time: str
    - reason: str

DailyPlan
    - scheduled_tasks: list[ScheduledTask]
    - skipped_tasks: list[Task]
    - total_duration_minutes: int
    + summary() -> str
    + explain() -> str

Scheduler
    - owner: Owner
    + build_plan() -> DailyPlan
    + _filter_feasible(tasks, budget) -> list[Task]
    + _sort_by_priority(tasks) -> list[Task]
    + _assign_times(tasks, start) -> list[ScheduledTask]
    + _build_reason(task) -> str
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care task."""
    title: str
    duration_minutes: int
    priority: str = "medium"       # "low" | "medium" | "high"
    category: str = "other"        # "feeding" | "walk" | "meds" | "grooming" | "enrichment" | "other"
    notes: str = ""


@dataclass
class Pet:
    """Represents a pet."""
    name: str
    species: str                              # "dog" | "cat" | "other"
    age_years: float = 0.0
    special_needs: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Regular classes
# ---------------------------------------------------------------------------

class Owner:
    """A pet owner who has a pet and a list of care tasks to schedule."""

    def __init__(
        self,
        name: str,
        pet: Pet,
        available_minutes: int = 120,
        preferred_start_time: str = "08:00",
    ) -> None:
        self.name = name
        self.pet = pet
        self.available_minutes = available_minutes
        self.preferred_start_time = preferred_start_time
        self._tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a care task to the owner's task list."""
        pass

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Returns True if found and removed."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return a copy of the current task list."""
        pass


class ScheduledTask:
    """A Task that has been placed onto the day's timeline."""

    def __init__(self, task: Task, start_time: str, end_time: str, reason: str) -> None:
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason

    def __repr__(self) -> str:
        pass


class DailyPlan:
    """The output of the Scheduler: an ordered list of scheduled tasks."""

    def __init__(
        self,
        scheduled_tasks: list[ScheduledTask],
        skipped_tasks: list[Task],
        total_duration_minutes: int,
    ) -> None:
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_duration_minutes = total_duration_minutes

    def summary(self) -> str:
        """Return a short human-readable summary of the plan."""
        pass

    def explain(self) -> str:
        """Return a detailed explanation of why each task was chosen or skipped."""
        pass


class Scheduler:
    """Builds a DailyPlan for an Owner based on available time and task priorities."""

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def build_plan(self) -> DailyPlan:
        """Main entry point: sort, filter, assign times, return a DailyPlan."""
        pass

    def _filter_feasible(self, tasks: list[Task], budget: int) -> tuple[list[Task], list[Task]]:
        """
        Return (feasible, skipped) where feasible tasks fit within the time budget.
        High-priority tasks are never skipped unless they alone exceed the budget.
        """
        pass

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted high → medium → low, with duration as a tiebreaker."""
        pass

    def _assign_times(self, tasks: list[Task], start_time: str) -> list[ScheduledTask]:
        """Walk through sorted tasks and assign HH:MM start/end times."""
        pass

    def _build_reason(self, task: Task) -> str:
        """Generate a plain-English explanation for why a task was included."""
        pass
