import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
    - Build a daily checklist based on priority and time constraints
    - Show tasks users need to complete with checkboxes
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")

st.markdown("**Pet 1** (required)")
col_p1a, col_p1b = st.columns(2)
with col_p1a:
    pet_name = st.text_input("Pet 1 name", value="Mochi")
with col_p1b:
    species = st.selectbox("Pet 1 species", ["dog", "cat", "other"])

st.markdown("**Pet 2** (optional)")
add_second_pet = st.checkbox("Add a second pet")
pet2_name, pet2_species = "", "dog"
if add_second_pet:
    col_p2a, col_p2b = st.columns(2)
    with col_p2a:
        pet2_name = st.text_input("Pet 2 name", value="Biscuit")
    with col_p2b:
        pet2_species = st.selectbox("Pet 2 species", ["dog", "cat", "other"])

available_minutes = st.number_input(
    "Available time today (minutes)",
    min_value=10,
    max_value=600,
    value=120,
)

st.markdown("### Tasks")
st.caption("Add tasks, then generate a checklist plan.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "current_plan" not in st.session_state:
    st.session_state.current_plan = None
if "pets" not in st.session_state:
    st.session_state.pets = []
if "owner" not in st.session_state:
    st.session_state.owner = None
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False


def build_pets() -> list[Pet]:
    pets = [Pet(name=pet_name, species=species)]
    if add_second_pet and pet2_name:
        pets.append(Pet(name=pet2_name, species=pet2_species))
    return pets


def get_or_create_owner() -> Owner:
    pets = build_pets()
    st.session_state.pets = pets
    owner = st.session_state.owner

    if not isinstance(owner, Owner):
        owner = Owner(
            name=owner_name,
            pets=pets,
            available_minutes=int(available_minutes),
        )
        st.session_state.owner = owner
    else:
        owner.name = owner_name
        owner.pets = pets
        owner.available_minutes = int(available_minutes)

    return owner


owner = get_or_create_owner()

debug_mode = st.checkbox("Debug mode", key="debug_mode")
if debug_mode:
    with st.expander("Session debug (owner/pets)", expanded=True):
        st.write("owner in session:", isinstance(st.session_state.owner, Owner))
        if isinstance(st.session_state.owner, Owner):
            st.write(
                {
                    "name": st.session_state.owner.name,
                    "available_minutes": st.session_state.owner.available_minutes,
                    "pet_count": len(st.session_state.owner.pets),
                }
            )
        st.write(
            "pets in session:",
            [{"name": pet.name, "species": pet.species} for pet in st.session_state.pets],
        )

pet_name_options = [pet.name for pet in owner.get_pets() if pet.name]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    selected_pet_name = st.selectbox(
        "Pet",
        pet_name_options if pet_name_options else [""],
        index=0,
    )
with col5:
    scheduled_time_value = st.time_input("Time", value="08:00")

task_category = st.selectbox(
    "Category",
    ["feeding", "walking", "medication", "grooming", "other"],
    index=1,
)

if st.button("Add task"):
    st.session_state.tasks.append(
        {
            "title": task_title,
            "duration_minutes": int(duration),
            "priority": priority,
            "category": task_category,
            "pet_name": selected_pet_name,
            "scheduled_time": scheduled_time_value.strftime("%H:%M"),
        }
    )
    st.session_state.current_plan = None

if st.session_state.tasks:
    st.write("Current tasks:")
    remove_index = None
    for index, task in enumerate(st.session_state.tasks):
        task_col, remove_col = st.columns([5, 1])
        with task_col:
            st.write(
                f"- {task['scheduled_time']} | {task['pet_name']} | {task['title']} "
                f"({task['duration_minutes']} min, {task['priority']} priority, {task['category']})"
            )
        with remove_col:
            if st.button("Remove", key=f"remove_task_{index}"):
                remove_index = index

    if remove_index is not None:
        st.session_state.tasks.pop(remove_index)
        st.session_state.current_plan = None
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

owner.clear_tasks()
for task_data in st.session_state.tasks:
    owner.add_task(
        Task(
            title=task_data["title"],
            duration_minutes=task_data["duration_minutes"],
            priority=task_data["priority"],
            category=task_data["category"],
            pet_name=task_data.get("pet_name", ""),
            scheduled_time=task_data.get("scheduled_time", ""),
        )
    )

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a checklist of tasks to complete today.")

category_filter = st.selectbox(
    "Filter by category",
    ["all", "feeding", "walking", "medication", "grooming", "other"],
    index=0,
)

pet_filter = "all"
if len(owner.get_pets()) == 2:
    pet_filter = st.selectbox("Filter by pet", ["all"] + pet_name_options, index=0)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.build_plan(category_filter=category_filter, pet_filter=pet_filter)
    conflicts = scheduler.detect_task_conflicts()

    st.session_state.current_plan = {
        "category_filter": category_filter,
        "pet_filter": pet_filter,
        "tasks_to_complete": [
            {
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "category": task.category,
                "pet_name": task.pet_name,
                "scheduled_time": task.scheduled_time,
            }
            for task in plan.tasks_to_complete
        ],
        "skipped_tasks": [
            {
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "category": task.category,
                "pet_name": task.pet_name,
                "scheduled_time": task.scheduled_time,
            }
            for task in plan.skipped_tasks
        ],
        "total_duration_minutes": plan.total_duration_minutes,
        "conflicts": [
            {
                "tasks for mochi": f"{first_task.scheduled_time} | {first_task.pet_name} | {first_task.title}",
                "tasks for biscuit": f"{second_task.scheduled_time} | {second_task.pet_name} | {second_task.title}",
            }
            for first_task, second_task in conflicts
        ],
    }

if st.session_state.current_plan is not None:
    plan_data = st.session_state.current_plan

    st.markdown("### Today's Checklist")
    st.caption(f"Current category filter: {plan_data.get('category_filter', 'all')}")
    if len(owner.get_pets()) == 2:
        st.caption(f"Current pet filter: {plan_data.get('pet_filter', 'all')}")

    if plan_data.get("conflicts"):
        st.error("⚠️ Schedule conflict detected between pets. Please adjust time slots.")
        st.table(plan_data["conflicts"])

    if plan_data["tasks_to_complete"]:
        for index, task in enumerate(plan_data["tasks_to_complete"]):
            checkbox_label = (
                f"{task.get('scheduled_time', '')} | {task.get('pet_name', '')} | {task['title']} "
                f"({task['duration_minutes']} min, {task['priority']} priority, {task['category']})"
            )
            checkbox_key = (
                f"task_check_{index}_{task.get('scheduled_time', '')}_{task.get('pet_name', '')}_{task['title']}"
            )
            st.checkbox(checkbox_label, key=checkbox_key)
    else:
        st.info("No tasks fit in today's available time.")

    st.caption(f"Planned time: {plan_data['total_duration_minutes']} minutes")

    if plan_data["skipped_tasks"]:
        st.markdown("### Skipped (over time budget)")
        st.table(plan_data["skipped_tasks"])
