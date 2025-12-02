# ===== Importing external modules ===========
from pathlib import Path
from datetime import datetime

# ===== User and Task Classes ===========
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return f"{self.username},{self.password}"

class Admin(User):
    def register_user(self):
        reg_user()

    def view_completed_tasks(self):
        view_completed()

    def delete_task(self):
        delete_task()

    def generate_reports(self):
        generate_reports()

class Task:
    def __init__(self, asignee, title, description, due_date, date_now, complete):
        self.asignee = asignee
        self.title = title
        self.description = description
        self.due_date = due_date
        self.date_now = date_now
        self.complete = complete

    def __str__(self):
        return (
            f"-------------------------\n"
            f"Task:\t\t\t{self.title}\n"
            f"Assigned to:\t\t{self.asignee}\n"
            f"Date assigned:\t\t{self.date_now}\n"
            f"Due date:\t\t{self.due_date}\n"
            f"Task Complete?\t\t{self.complete}\n"
            f"Task description:\n  {self.description}\n"
            f"-------------------------\n"
        )

# ===== File Paths ===========
user_path = Path("user.txt")
task_path = Path("tasks.txt")
task_report_path = Path("task_overview.txt")
user_report_path = Path("user_overview.txt")
users = []

# ===== Helper Functions ===========
def read_users():
    users.clear()
    with open(user_path, "r") as file:
        for line in file:
            username, password = [x.strip() for x in line.strip().split(",")]
            users.append(User(username, password))
    return users

def read_tasks():
    tasks = []
    with open(task_path, "r") as file:
        for line in file:
            parts = [p.strip() for p in line.strip().split(",")]
            if len(parts) == 6:
                tasks.append(Task(*parts))
    return tasks

def write_tasks(tasks):
    with open(task_path, "w") as file:
        for t in tasks:
            file.write(f"{t.asignee},{t.title}, {t.description}, {t.due_date}, {t.date_now}, {t.complete}\n")

# ===== Core Functionalities ===========
def reg_user():
    """Register a new user (admin only)"""
    read_users()
    while True:
        new_username = input("Enter new username: ").strip()
        if any(u.username == new_username for u in users):
            print("Error: Username already exists. Try again.")
            continue
        new_password = input("Enter password: ").strip()
        confirm_password = input("Confirm password: ").strip()
        if new_password != confirm_password:
            print("Passwords do not match. Try again.")
            continue
        with open(user_path, "a") as file:
            file.write(f"\n{new_username},{new_password}")
        print(f"User '{new_username}' registered successfully.")
        break

def add_task():
    asignee = input("Task assigned to: ").strip()
    title = input("Task title: ").strip()
    description = input("Task description: ").strip()
    due_date_input = input("Due date (YYYY-MM-DD): ").strip()
    due_date = datetime.strptime(due_date_input, "%Y-%m-%d").strftime("%d %b %Y")
    date_now = datetime.now().strftime("%d %b %Y")
    complete = "No"
    with open(task_path, "a") as file:
        file.write(f"{asignee},{title}, {description}, {due_date}, {date_now}, {complete}\n")
    print("Task added successfully.")

def view_all():
    tasks = read_tasks()
    for t in tasks:
        print(t)

def get_valid_task_number(max_num):
    """Recursive function to get a valid task number or -1"""
    choice = input(f"Enter task number (1-{max_num}) or -1 to return: ").strip()
    if choice == "-1":
        return -1
    if choice.isdigit() and 1 <= int(choice) <= max_num:
        return int(choice) - 1
    print("Invalid input. Try again.")
    return get_valid_task_number(max_num)  # recursion

def view_mine(username):
    tasks = read_tasks()
    my_tasks = [t for t in tasks if t.asignee == username]
    if not my_tasks:
        print("No tasks assigned to you.")
        return
    while True:
        print("\nYour tasks:")
        for idx, t in enumerate(my_tasks, 1):
            print(f"{idx}. {t.title} (Complete: {t.complete})")
        task_idx = get_valid_task_number(len(my_tasks))
        if task_idx == -1:
            break
        t = my_tasks[task_idx]
        if t.complete.lower() == "yes":
            print("Task already completed. Cannot edit.")
            continue
        action = input("Enter 'c' to mark complete, 'e' to edit: ").strip().lower()
        if action == "c":
            t.complete = "Yes"
            print("Task marked complete.")
        elif action == "e":
            new_asignee = input(f"New assignee (leave blank to keep '{t.asignee}'): ").strip()
            if new_asignee:
                t.asignee = new_asignee
            new_due = input(f"New due date YYYY-MM-DD (leave blank to keep '{t.due_date}'): ").strip()
            if new_due:
                t.due_date = datetime.strptime(new_due, "%Y-%m-%d").strftime("%d %b %Y")
            print("Task updated.")
        write_tasks(tasks)
        my_tasks = [t for t in tasks if t.asignee == username]  # refresh list

def view_completed():
    tasks = read_tasks()
    for t in tasks:
        if t.complete.lower() == "yes":
            print(t)

def delete_task():
    tasks = read_tasks()
    for i, t in enumerate(tasks, 1):
        print(f"{i}. {t.title} assigned to {t.asignee}")
    choice = input("Enter task number to delete: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(tasks):
        tasks.pop(int(choice) - 1)
        write_tasks(tasks)
        print("Task deleted successfully.")
    else:
        print("Invalid selection.")

# ===== Report Generation ===========
def generate_reports():
    tasks = read_tasks()
    users_list = read_users()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.complete.lower() == "yes")
    incomplete_tasks = total_tasks - completed_tasks
    overdue_tasks = sum(1 for t in tasks if t.complete.lower() == "no" and datetime.strptime(t.due_date, "%d %b %Y") < datetime.now())
    incomplete_percent = (incomplete_tasks / total_tasks * 100) if total_tasks else 0
    overdue_percent = (overdue_tasks / total_tasks * 100) if total_tasks else 0

    # Task overview
    with open(task_report_path, "w") as f:
        f.write(f"Total tasks: {total_tasks}\n")
        f.write(f"Completed tasks: {completed_tasks}\n")
        f.write(f"Incomplete tasks: {incomplete_tasks}\n")
        f.write(f"Overdue tasks: {overdue_tasks}\n")
        f.write(f"Percentage incomplete: {incomplete_percent:.2f}%\n")
        f.write(f"Percentage overdue: {overdue_percent:.2f}%\n")

    # User overview
    with open(user_report_path, "w") as f:
        f.write(f"Total users: {len(users_list)}\n")
        f.write(f"Total tasks: {total_tasks}\n")
        for u in users_list:
            user_tasks = [t for t in tasks if t.asignee == u.username]
            num_user_tasks = len(user_tasks)
            percent_of_total = (num_user_tasks / total_tasks * 100) if total_tasks else 0
            completed_user = sum(1 for t in user_tasks if t.complete.lower() == "yes")
            incomplete_user = num_user_tasks - completed_user
            overdue_user = sum(1 for t in user_tasks if t.complete.lower() == "no" and datetime.strptime(t.due_date, "%d %b %Y") < datetime.now())
            completed_percent = (completed_user / num_user_tasks * 100) if num_user_tasks else 0
            incomplete_percent_user = (incomplete_user / num_user_tasks * 100) if num_user_tasks else 0
            overdue_percent_user = (overdue_user / num_user_tasks * 100) if num_user_tasks else 0
            f.write(f"\nUser: {u.username}\n")
            f.write(f"  Total tasks: {num_user_tasks}\n")
            f.write(f"  % of total tasks: {percent_of_total:.2f}%\n")
            f.write(f"  % completed: {completed_percent:.2f}%\n")
            f.write(f"  % incomplete: {incomplete_percent_user:.2f}%\n")
            f.write(f"  % overdue: {overdue_percent_user:.2f}%\n")
    print("Reports generated successfully.")

def display_statistics():
    """Displays stats from the report files; generates if they don't exist"""
    if not task_report_path.exists() or not user_report_path.exists():
        generate_reports()
    print("\n--- Task Overview ---")
    with open(task_report_path, "r") as f:
        print(f.read())
    print("\n--- User Overview ---")
    with open(user_report_path, "r") as f:
        print(f.read())

# ===== Login ===========
def login():
    read_users()
    while True:
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        for u in users:
            if u.username == username and u.password == password:
                print("Login successful!")
                if username == "admin":
                    return Admin(username, password)
                else:
                    return User(username, password)
        print("Invalid username or password.")

# ===== Main Program ===========
current_user = login()

while True:
    if isinstance(current_user, Admin):
        menu = input(
            "\nSelect an option:\n"
            "r - register user\n"
            "a - add task\n"
            "va - view all tasks\n"
            "vm - view my tasks\n"
            "vc - view completed tasks\n"
            "del - delete a task\n"
            "gr - generate reports\n"
            "ds - display statistics\n"
            "e - exit\n: ").lower()
    else:
        menu = input(
            "\nSelect an option:\n"
            "a - add task\n"
            "va - view all tasks\n"
            "vm - view my tasks\n"
            "e - exit\n: ").lower()

    if menu == "r" and isinstance(current_user, Admin):
        current_user.register_user()
    elif menu == "a":
        add_task()
    elif menu == "va":
        view_all()
    elif menu == "vm":
        view_mine(current_user.username)
    elif menu == "vc" and isinstance(current_user, Admin):
        current_user.view_completed_tasks()
    elif menu == "del" and isinstance(current_user, Admin):
        current_user.delete_task()
    elif menu == "gr" and isinstance(current_user, Admin):
        current_user.generate_reports()
    elif menu == "ds" and isinstance(current_user, Admin):
        display_statistics()
    elif menu == "e":
        print("Goodbye!")
        break
    else:
        print("Invalid input. Try again.")
