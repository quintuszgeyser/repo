from pathlib import Path

FILEPATH = Path("equations.txt")

def safe_number_input(prompt):
    """Safely gets a valid float number from the user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid number. Please enter a numeric value.")


def safe_operation_input():
    """Safely gets a valid mathematical operation."""
    while True:
        op = input("Enter operation (+, -, *, /): ").strip()
        if op in ["+", "-", "*", "/"]:
            return op
        print("Invalid operation. Try again.")


def perform_calculation():
    """Perform a calculation and record it in equations.txt."""
    num1 = safe_number_input("Enter first number: ")
    num2 = safe_number_input("Enter second number: ")
    op = safe_operation_input()

    try:
        if op == "+":
            result = num1 + num2
        elif op == "-":
            result = num1 - num2
        elif op == "*":
            result = num1 * num2
        elif op == "/":
            result = num1 / num2  

        equation = f"{num1} {op} {num2} = {result}"

        print("Result:", equation)

   
        with open(FILEPATH, "a") as file:
            file.write(equation + "\n")

    except ZeroDivisionError:
        print(" Error: Cannot divide by zero.")


def print_history():
    """Print all previous equations. Handles missing file."""
    if not FILEPATH.exists():
        print("No history found (equations.txt does not exist).")
        return

    print("\n--- Previous Calculations ---")
    with open(FILEPATH, "r") as file:
        content = file.read().strip()

        if content == "":
            print("No calculations recorded yet.")
        else:
            print(content)
    print("-----------------------------\n")


def main():
    print("=== Simple Calculator Application ===")

    while True:
        print("\nWhat would you like to do?")
        print("1 → Perform a calculation")
        print("2 → Print previous equations")
        print("3 → Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            perform_calculation()
        elif choice == "2":
            print_history()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
