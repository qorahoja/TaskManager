from aiogram.dispatcher.filters.state import State, StatesGroup

# Define states
class States(StatesGroup):
    name = State()
    password = State()
    try_1 = State()
    try_2 = State()
    try_3 = State()
    login_pass = State()
    reset_password = State()
    group_name_for_reset = State()
    old_name_for_reset = State()
    new_pass = State()
    try_group_1 = State()
    try_group_2 = State()
    try_group_3 = State()
    team_name = State()
    technical_task = State()
    task_subject = State()
    write_task_for_employe = State()
    deadline = State()
    tester = State()
    select_member = State()
    change_tester = State()
    decline = State()
    point = State()
