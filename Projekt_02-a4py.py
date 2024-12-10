import json
import time
from datetime import datetime, timedelta


class FileManager:
    """
    Správa souborů - kontrola existence a inicializace souborů.
    """
    @staticmethod
    def ensure_file(file_path, default_data):
        """
        Zkontroluje existenci JSON souboru a vytvoří jej, pokud neexistuje.
        """
        try:
            with open(file_path, "r") as f:
                pass
        except FileNotFoundError:
            with open(file_path, "w") as f:
                json.dump(default_data, f, indent=4)


class UserManager:
    """
    Správa uživatelů - registrace, přihlášení, validace.
    """
    def __init__(self, user_file="users.json"):
        self.user_file = user_file
        FileManager.ensure_file(self.user_file, {})
        self.users = self.load_users()

    def load_users(self):
        """Načte data uživatelů ze souboru."""
        with open(self.user_file, "r") as f:
            return json.load(f)

    def save_users(self):
        """Uloží data uživatelů do souboru."""
        with open(self.user_file, "w") as f:
            json.dump(self.users, f, indent=4)

    def validate_username(self, username):
        """Validuje délku uživatelského jména."""
        return len(username) >= 6

    def validate_password(self, password):
        """Validuje délku a strukturu hesla."""
        return len(password) >= 6 and any(char.isdigit() for char in password)

    def sign_up(self, username, password):
        """
        Registrace nového uživatele.
        """
        if username in self.users:
            print("Username already exists.")
            return False
        if not self.validate_username(username):
            print("Username must be at least 6 characters long.")
            return False
        if not self.validate_password(password):
            print("Password must be at least 6 characters long and include a number.")
            return False
        self.users[username] = {"password": password, "games": []}
        self.save_users()
        print("Registration successful.")
        return True

    def log_in(self, username, password):
        """
        Přihlášení uživatele.
        """
        if username in self.users and self.users[username]["password"] == password:
            print("Login successful.")
            return True
        print("Invalid username or password.")
        return False


class GameStats:
    """
    Správa statistik - ukládání a načítání herních výsledků.
    """
    def __init__(self, stats_file="stats.json"):
        self.stats_file = stats_file
        FileManager.ensure_file(self.stats_file, {})
        self.stats = self.load_stats()

    def load_stats(self):
        """Načte statistiky ze souboru."""
        with open(self.stats_file, "r") as f:
            return json.load(f)

    def save_stats(self):
        """Uloží statistiky do souboru."""
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=4)

    def add_game_result(self, username, attempts, duration):
        """Přidá herní výsledek uživatele."""
        now = datetime.now().isoformat()
        if username not in self.stats:
            self.stats[username] = []
        self.stats[username].append({"attempts": attempts, "duration": duration, "timestamp": now})
        self.save_stats()

    def get_recent_stats(self, username, days=0):
        """
        Načte statistiky za poslední dny.
        Pokud days = 0, načte všechny statistiky.
        """
        if username not in self.stats:
            return []
        stats = self.stats[username]
        if days > 0:
            cutoff = datetime.now() - timedelta(days=days)
            return [game for game in stats if datetime.fromisoformat(game["timestamp"]) > cutoff]
        return stats


class BullsAndCowsGame:
    """
    Hlavní logika hry Bulls and Cows.
    """
    @staticmethod
    def generate_secret_number(num_digits):
        """
        Generuje náhodné tajné číslo s unikátními číslicemi.
        """
        from random import sample
        while True:
            number = sample(range(10), num_digits)
            if number[0] != 0:
                return ''.join(map(str, number))

    @staticmethod
    def is_valid_guess(guess, num_digits):
        """Validuje hráčův tip."""
        return guess.isdigit() and len(guess) == num_digits and len(set(guess)) == len(guess)

    @staticmethod
    def evaluate_guess(secret, guess):
        """Vyhodnocuje hráčův tip a počítá bulls a cows."""
        bulls = sum(s == g for s, g in zip(secret, guess))
        cows = sum(g in secret for g in guess) - bulls
        return bulls, cows

    def play(self, num_digits):
        """
        Hlavní smyčka hry Bulls and Cows.
        """
        secret = self.generate_secret_number(num_digits)
        attempts = 0
        start_time = time.time()
        print(f"\n{'=' * 40}")
        print(f"A {num_digits}-digit secret number has been generated!")
        print(f"{'=' * 40}\n")

        while True:
            guess = input("Enter your guess (or 'q' to quit): ").strip()
            if guess.lower() == "q":
                print("Thanks for playing!")
                return None, None

            if not self.is_valid_guess(guess, num_digits):
                print("Invalid guess. Try again.")
                continue

            attempts += 1
            bulls, cows = self.evaluate_guess(secret, guess)
            print(f"\n{'_' * 40}")
            print(f"{bulls} Bulls, {cows} Cows")
            print(f"{'_' * 40}\n")

            if bulls == num_digits:
                duration = time.time() - start_time
                print(f"\n{'=' * 40}")
                print(f"Congratulations! You guessed the number in {attempts} attempts and {duration:.2f} seconds.")
                print(f"{'=' * 40}\n")
                return attempts, duration


class GameManager:
    """
    Hlavní správa hry a interakce s uživatelem.
    """
    def __init__(self):
        self.user_manager = UserManager()
        self.game_stats = GameStats()
        self.game = BullsAndCowsGame()
        self.difficulty = 4  # Výchozí obtížnost (medium)

    def set_difficulty(self):
        """Nastavení obtížnosti hry."""
        print("\n" + "=" * 40)
        print("Select difficulty:")
        print("1. Easy (3 digits)")
        print("2. Medium (4 digits)")
        print("3. Hard (5 digits)")
        print("=" * 40)
        choice = input("Enter your choice (or 'q' to quit): ").strip()

        if choice.lower() == "q":
            print("Returning to the main menu.")
            return False

        if choice == "1":
            self.difficulty = 3
            print("Difficulty set to Easy (3 digits).")
        elif choice == "2":
            self.difficulty = 4
            print("Difficulty set to Medium (4 digits).")
        elif choice == "3":
            self.difficulty = 5
            print("Difficulty set to Hard (5 digits).")
        else:
            print("Invalid choice. Keeping current difficulty.")
        return True

    def start(self):
        """Spouští hlavní menu hry."""
        print("\n" + "=" * 40)
        print("Welcome to Bulls and Cows!")
        print("=" * 40)
        while True:
            print("\n1. Log in\n2. Sign up\n3. Play as guest\n4. Quit")
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                username = input("Enter username (or 'q' to quit): ").strip()
                if username.lower() == "q":
                    continue
                password = input("Enter password: ").strip()
                if self.user_manager.log_in(username, password):
                    self.main_menu(username)
            elif choice == "2":
                username = input("Enter username (or 'q' to quit): ").strip()
                if username.lower() == "q":
                    continue
                password = input("Enter password: ").strip()
                self.user_manager.sign_up(username, password)
            elif choice == "3":
                self.main_menu("guest")
            elif choice == "4":
                print("Goodbye!")
                break

    def main_menu(self, username):
        """Hlavní menu přihlášeného hráče."""
        while True:
            print(f"\n{'=' * 40}")
            print(f"Welcome, {username}!")
            print("1. Play game\n2. View statistics (not available for guests)\n3. Log out")
            print(f"{'=' * 40}")
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                if not self.set_difficulty():
                    continue
                attempts, duration = self.game.play(self.difficulty)
                if username != "guest" and attempts is not None:
                    self.game_stats.add_game_result(username, attempts, duration)
            elif choice == "2":
                if username == "guest":
                    print("Statistics are not available for guests.")
                elif len(self.game_stats.get_recent_stats(username)) == 0:
                    print("No statistics available. Play a game first!")
                else:
                    stats = self.game_stats.get_recent_stats(username, days=30)
                    print(f"Statistics for the last 30 days ({len(stats)} games):")
                    for game in stats:
                        print(f"- {game['attempts']} attempts, {game['duration']:.2f} seconds")
            elif choice == "3":
                print("Logging out...")
                break
            else:
                print("Invalid choice. Try again.")


if __name__ == "__main__":
    manager = GameManager()
    manager.start()
