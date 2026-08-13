import random

def play_game():
    secret = random.randint(1, 100)
    attempts = 0
    low, high = 1, 100

    print("\n🎯 Number Guessing Game")
    print("I've picked a number between 1 and 100. Can you guess it?\n")

    while True:
        try:
            guess = int(input(f"  Your guess [{low}–{high}]: "))
        except ValueError:
            print("  Please enter a valid number.\n")
            continue

        if guess < 1 or guess > 100:
            print("  Please enter a number between 1 and 100.\n")
            continue

        attempts += 1

        if guess == secret:
            print(f"\n  ✅ Correct! The number was {secret}.")
            print(f"  You got it in {attempts} attempt{'s' if attempts > 1 else ''}!\n")
            break
        elif guess < secret:
            low = max(low, guess + 1)
            print(f"  ↑  Too low! Try higher.\n")
        else:
            high = min(high, guess - 1)
            print(f"  ↓  Too high! Try lower.\n")

best = None
while True:
    play_game()
    if best is None:
        best = int(input("  Play again? (y/n): ").strip().lower() == 'y' or 0)
    again = input("  Play again? (y/n): ").strip().lower()
    if again != 'y':
        print("\nThanks for playing! Goodbye. 👋\n")
        break