"""
A simple quiz program that presents a series of questions to the user.
The user is asked to answer each question and receives immediate feedback
on whether their answer is correct or incorrect. At the end, the program
displays the user's score as a percentage of correct answers.
"""

# Create a list of questions and their correct answers.
questions = [
    ["What color is the daytime sky on a clear day? ", "blue"],
    ["What is the answer to life, the universe and everything? ", "42"],
    ["What is a three-letter word for mouse trap? ", "cat"],
]

# Check if there are any questions in the questions list.
# If the list is empty, print a message and terminate the program.
if len(questions) == 0:
    print("No questions were given.")

# Initialize index for iterating through the questions.
# Initialize right to count the number of correct answers.
index = 0
right = 0

# Loop through each question in the list.
while index < len(questions):
    # Extract the question and correct answer from the current question set.
    question = questions[index][0]
    answer = questions[index][1]

    # Prompt the user with the question and store their answer.
    given_answer = input(question)

    # Check if the user's answer matches the correct answer.
    if answer == given_answer:
        print("Correct")  # Inform the user they answered correctly.
        right = right + 1  # Increment the count of correct answers.
    else:
        # Inform the user of the correct answer.
        print("Incorrect, correct was:", answer)

    # Move to the next question.
    index = index + 1

# Calculate the user's score as a percentage the result using f-strings.
# Round the score to 2 decimal places for clarity.
score = round(right * 100 / len(questions), 2)
print(f"You got {score}% right out of {len(questions)}")
