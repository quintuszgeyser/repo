import random
jokes = [
    "Why don’t scientists trust atoms? Because they make up everything!",
    "Why did the math book look sad? Because it had too many problems.",
    "What do you call fake spaghetti? An impasta!",
    "Why did the scarecrow win an award? Because he was outstanding in his field.",
    "Why don’t skeletons fight each other? They don’t have the guts.",
    "What do you call cheese that isn’t yours? Nacho cheese!",
    "Why did the computer go to therapy? It had a hard drive.",
    "What do you get if you cross a snowman and a vampire? Frostbite!",
    "Why can’t your nose be 12 inches long? Because then it would be a foot.",
    "What did one ocean say to the other ocean? Nothing, they just waved.",
    "Why did the coffee file a police report? It got mugged.",
    "What’s a computer’s favorite snack? Microchips.",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "Why did the bicycle fall over? It was two-tired.",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one!"
]



random_number =  random.randrange(0,len(jokes))

print(jokes[random_number])