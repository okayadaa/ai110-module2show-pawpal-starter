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
    - pets: list[Pet]            # 1 or 2 pets
    - available_minutes: int
    - preferred_start_time: str  # e.g. "08:00"
    + add_pet(pet: Pet) -> None
    + get_pets() -> list[Pet]
    + add_task(task: Task) -> None
    + remove_task(title: str) -> bool
    + get_tasks() -> list[Task]

DailyPlan
    - tasks_to_complete: list[Task]
    - checkbox_state: dict[str, bool]
    - skipped_tasks: list[Task]
    - total_duration_minutes: int
    + get_checklist_items() -> list[tuple[Task, bool]]

Scheduler
    - owner: Owner
    + build_plan() -> DailyPlan
    + _filter_feasible(tasks, budget) -> tuple[list[Task], list[Task]]
    + _sort_by_priority(tasks) -> list[Task]
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = {"feeding", "walking", "medication", "grooming", "other"}
_CATEGORY_ALIASES = {
    "walk": "walking",
    "walks": "walking",
    "meds": "medication",
    "medicine": "medication",
    "enrichment": "other",
}


def normalize_category(category: str | None) -> str:
    """Map a raw category value into the supported category set."""
    normalized = (category or "").strip().lower()
    normalized = _CATEGORY_ALIASES.get(normalized, normalized)
    return normalized if normalized in ALLOWED_CATEGORIES else "other"

@dataclass
class Task:
    """A single pet care task."""
    title: str
    duration_minutes: int
    priority: str = "medium"       # "low" | "medium" | "high"
    category: str = "other"        # "feeding" | "walking" | "medication" | "grooming" | "other"
    notes: str = ""
    pet_name: str = ""
    scheduled_time: str = ""


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
    """A pet owner who has 1–2 pets and a list of care tasks to schedule."""

    MAX_PETS = 2

    def __init__(
        self,
        name: str,
        pets: list[Pet],
        available_minutes: int = 120,
        preferred_start_time: str = "08:00",
    ) -> None:
        if not pets or len(pets) > self.MAX_PETS:
            raise ValueError(f"Owner must have 1 or {self.MAX_PETS} pets.")
        self.name = name
        self.pets = list(pets)
        self.available_minutes = available_minutes
        self.preferred_start_time = preferred_start_time
        self._tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a second pet. Raises ValueError if owner already has the maximum."""
        if len(self.pets) >= self.MAX_PETS:
            raise ValueError(f"An owner can have at most {self.MAX_PETS} pets.")
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return the owner's pets."""
        return list(self.pets)

    def add_task(self, task: Task) -> None:
        """Add a care task to the owner's task list."""
        self._tasks.append(task)

    def clear_tasks(self) -> None:
        """Remove all tasks from the owner's task list."""
        self._tasks.clear()

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Returns True if found and removed."""
        for index, task in enumerate(self._tasks):
            if task.title == title:
                del self._tasks[index]
                return True
        return False

    def get_tasks(self) -> list[Task]:
        """Return a copy of the current task list."""
        return list(self._tasks)

    def get_tasks_by_category(self, category: str) -> list[Task]:
        """Return tasks that match a category (supports alias values)."""
        normalized_category = normalize_category(category)
        return [
            task
            for task in self._tasks
            if normalize_category(task.category) == normalized_category
        ]


class DailyPlan:
    """A checklist-style daily plan containing tasks the user should complete."""

    def __init__(
        self,
        tasks_to_complete: list[Task],
        checkbox_state: dict[str, bool],
        skipped_tasks: list[Task],
        total_duration_minutes: int,
    ) -> None:
        self.tasks_to_complete = tasks_to_complete
        self.checkbox_state = checkbox_state
        self.skipped_tasks = skipped_tasks
        self.total_duration_minutes = total_duration_minutes

    def get_checklist_items(self) -> list[tuple[Task, bool]]:
        """Return tasks paired with checkbox state for UI display."""
        return [
            (task, self.checkbox_state.get(task.title, False))
            for task in self.tasks_to_complete
        ]


class Scheduler:
    """Sorts and filters owner tasks, then returns a DailyPlan."""

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def build_plan(self, category_filter: str = "all", pet_filter: str = "all") -> DailyPlan:
        """Main entry point: sort and filter tasks, then return a DailyPlan."""
        owner_tasks = self.owner.get_tasks()
        if category_filter != "all":
            normalized_filter = normalize_category(category_filter)
            owner_tasks = [
                task
                for task in owner_tasks
                if normalize_category(task.category) == normalized_filter
            ]
        if pet_filter != "all":
            owner_tasks = [
                task
                for task in owner_tasks
                if task.pet_name.strip().lower() == pet_filter.strip().lower()
            ]
        sorted_tasks = self._sort_by_priority(owner_tasks)
        tasks_to_complete, skipped_tasks = self._filter_feasible(
            sorted_tasks,
            self.owner.available_minutes,
        )
        total_duration = sum(task.duration_minutes for task in tasks_to_complete)
        checkbox_state = {task.title: False for task in tasks_to_complete}
        return DailyPlan(
            tasks_to_complete=tasks_to_complete,
            checkbox_state=checkbox_state,
            skipped_tasks=skipped_tasks,
            total_duration_minutes=total_duration,
        )

    def detect_task_conflicts(self) -> list[tuple[Task, Task]]:
        """
        Return overlapping task pairs for different pets.

        A task is considered in conflict when:
        - both tasks have valid HH:MM scheduled_time values
        - both tasks have pet_name values
        - the pets are different
        - time windows overlap
        """
        tasks_with_time = [
            task
            for task in self.owner.get_tasks()
            if task.scheduled_time and task.pet_name and self._parse_time(task.scheduled_time) is not None
        ]

        conflicts: list[tuple[Task, Task]] = []
        for index, first_task in enumerate(tasks_with_time):
            first_start = self._parse_time(first_task.scheduled_time)
            if first_start is None:
                continue
            first_end = first_start + timedelta(minutes=first_task.duration_minutes)

            for second_task in tasks_with_time[index + 1 :]:
                if first_task.pet_name == second_task.pet_name:
                    continue

                second_start = self._parse_time(second_task.scheduled_time)
                if second_start is None:
                    continue
                second_end = second_start + timedelta(minutes=second_task.duration_minutes)

                if first_start < second_end and second_start < first_end:
                    conflicts.append((first_task, second_task))

        return conflicts

    def _filter_feasible(self, tasks: list[Task], budget: int) -> tuple[list[Task], list[Task]]:
        """
        Return (feasible, skipped) where feasible tasks fit within the time budget.
        High-priority tasks are never skipped unless they alone exceed the budget.
        """
        used_minutes = 0
        selected: list[Task] = []
        skipped: list[Task] = []

        for task in tasks:
            if used_minutes + task.duration_minutes <= budget:
                selected.append(task)
                used_minutes += task.duration_minutes
            else:
                skipped.append(task)

        return selected, skipped

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by valid scheduled time, else by priority and duration."""
        return sorted(
            tasks,
            key=lambda task: (
                self._parse_time(task.scheduled_time) is None,
                self._parse_time(task.scheduled_time) or datetime.max,
                self.PRIORITY_ORDER.get(task.priority, 3),
                task.duration_minutes,
            ),
        )

    def _parse_time(self, time_str: str) -> datetime | None:
        """Parse HH:MM time string. Returns None for invalid input."""
        try:
            return datetime.strptime(time_str, "%H:%M")
        except ValueError:
            return None
