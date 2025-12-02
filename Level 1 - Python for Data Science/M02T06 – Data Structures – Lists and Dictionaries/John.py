
upper = 0
wrong_guesses = []

while upper != 'John'.upper():
    user_input = input("Guess a name: ")
    upper = user_input.upper()
    if upper != 'John'.upper():
        wrong_guesses.append(user_input)
        
    else:
        print(wrong_guesses)
    
