from pawpal_system import Owner, Pet, Scheduler, Task


def build_sample_schedule() -> None:
	owner = Owner(
		name="Jordan",
		pets=[
			Pet(name="Mochi", species="dog", age_years=4),
			Pet(name="Biscuit", species="cat", age_years=2),
		],
		available_minutes=90,
		preferred_start_time="08:00",
	)

	owner.add_task(
		Task(
			title="Breakfast",
			duration_minutes=10,
			priority="high",
			category="feeding",
			pet_name="Mochi",
			scheduled_time="08:00",
		)
	)
	owner.add_task(
		Task(
			title="Morning walk",
			duration_minutes=30,
			priority="high",
			category="walking",
			pet_name="Mochi",
			scheduled_time="09:00",
		)
	)
	owner.add_task(
		Task(
			title="Give medication",
			duration_minutes=5,
			priority="medium",
			category="medication",
			pet_name="Biscuit",
			scheduled_time="11:30",
		)
	)

	plan = Scheduler(owner).build_plan()
	scheduled_tasks = sorted(
		plan.tasks_to_complete,
		key=lambda task: task.scheduled_time or "99:99",
	)

	print("Today's schedule:")
	print(f"Owner: {owner.name}")
	print("Pets: " + ", ".join(pet.name for pet in owner.get_pets()))
	print("-" * 30)

	for task in scheduled_tasks:
		print(
			f"{task.scheduled_time} - {task.pet_name}: {task.title} "
			f"({task.duration_minutes} min, {task.priority} priority)"
		)

	print("-" * 30)
	print(f"Total planned time: {plan.total_duration_minutes} minutes")


if __name__ == "__main__":
	build_sample_schedule()

