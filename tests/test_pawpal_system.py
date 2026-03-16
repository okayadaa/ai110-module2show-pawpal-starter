from pawpal_system import normalize_category, Pet, Owner, Task, Scheduler


def test_normalize_category_aliases():
    assert normalize_category("walk") == "walking"
    assert normalize_category("meds") == "medication"
    assert normalize_category("unknown") == "other"


def test_build_plan_priority_order():
    pet = Pet(name="Bella", species="dog")
    owner = Owner(name="Ada", pets=[pet], available_minutes=120)

    owner.add_task(Task(title="Medium task", duration_minutes=20, priority="medium"))
    owner.add_task(Task(title="High short", duration_minutes=10, priority="high"))
    owner.add_task(Task(title="High long", duration_minutes=30, priority="high"))

    plan = Scheduler(owner).build_plan()
    assert [t.title for t in plan.tasks_to_complete] == ["High short", "High long", "Medium task"]


def test_build_task_duration_order():
    pet = Pet(name="Bella", species="dog")
    owner = Owner(name="Ada", pets=[pet], available_minutes=180)

    owner.add_task(
        Task(
            title="Late walk",
            duration_minutes=20,
            priority="high",
            pet_name="Bella",
            scheduled_time="10:00",
        )
    )
    owner.add_task(
        Task(
            title="Morning meds",
            duration_minutes=20,
            priority="high",
            pet_name="Bella",
            scheduled_time="08:00",
        )
    )
    owner.add_task(
        Task(
            title="Mid-morning feed",
            duration_minutes=20,
            priority="high",
            pet_name="Bella",
            scheduled_time="09:00",
        )
    )

    plan = Scheduler(owner).build_plan()

    assert [task.scheduled_time for task in plan.tasks_to_complete] == ["08:00", "09:00", "10:00"]


def test_detect_task_conflicts():
    dog = Pet(name="Mochi", species="dog")
    cat = Pet(name="Biscuit", species="cat")
    owner = Owner(name="Ada", pets=[dog, cat], available_minutes=120)

    owner.add_task(
        Task(
            title="Mochi morning walk",
            duration_minutes=30,
            priority="high",
            pet_name="Mochi",
            scheduled_time="09:00",
        )
    )
    owner.add_task(
        Task(
            title="Biscuit medication",
            duration_minutes=20,
            priority="medium",
            pet_name="Biscuit",
            scheduled_time="09:10",
        )
    )

    conflicts = Scheduler(owner).detect_task_conflicts()

    assert len(conflicts) == 1
    first_task, second_task = conflicts[0]
    assert {first_task.pet_name, second_task.pet_name} == {"Mochi", "Biscuit"}
    assert {first_task.title, second_task.title} == {"Mochi morning walk", "Biscuit medication"}


def test_build_plan_pet_filter_tasks():
    dog = Pet(name="Mochi", species="dog")
    cat = Pet(name="Biscuit", species="cat")
    owner = Owner(name="Ada", pets=[dog, cat], available_minutes=120)

    owner.add_task(
        Task(
            title="Mochi breakfast",
            duration_minutes=10,
            priority="high",
            pet_name="Mochi",
        )
    )
    owner.add_task(
        Task(
            title="Biscuit grooming",
            duration_minutes=15,
            priority="medium",
            pet_name="Biscuit",
        )
    )

    plan = Scheduler(owner).build_plan(pet_filter="Mochi")

    assert len(plan.tasks_to_complete) == 1
    assert plan.tasks_to_complete[0].title == "Mochi breakfast"
    assert plan.tasks_to_complete[0].pet_name == "Mochi"