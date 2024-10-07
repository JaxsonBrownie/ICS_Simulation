import random
import time


while True:
    # List of numbers from 1 to 8
    numbers = list(range(1, 9))
    time.sleep(3)

    # Continue selecting numbers until the list is empty
    while numbers:
        # Choose a random number
        chosen_number = random.choice(numbers)
        print(f'Selected: {chosen_number}')
        
        # Remove the chosen number from the list
        numbers.remove(chosen_number)

    print("All numbers have been selected.")
