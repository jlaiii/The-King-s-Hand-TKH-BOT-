import os
import sys
import subprocess
import time
import random
import pyautogui
import pydirectinput
from collections import deque

# --- Initial Setup and Dependency Check ---

def install_dependencies():
    """
    Checks if required libraries are installed and installs them if they are not.
    """
    required_packages = ['pyautogui', 'pydirectinput']
    
    print("Checking for required Python libraries...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"  - {package} is already installed.")
        except ImportError:
            print(f"  - {package} not found. Attempting to install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"  - Successfully installed {package}.")
            except subprocess.CalledProcessError:
                print(f"  - Failed to install {package}. Please install it manually with 'pip install {package}'.")
                sys.exit(1)

# Run the dependency check at the very beginning
install_dependencies()

# --- Configuration ---
pyautogui.PAUSE = 0.5
pydirectinput.FAILSAFE = False

# --- Global Functions ---

def log_event(message):
    """
    Logs a message to the console and to a log file without a timestamp.
    """
    log_message = f"[https://jlaiii.github.io/TKH/] {message}"
    print(log_message)
    
    with open("bot_log.txt", "a") as log_file:
        log_file.write(log_message + "\n")

def jitter_click(x, y, x_range=20, y_range=20):
    """Perform a click with a random offset (jitter)."""
    jitter_x = random.randint(-x_range, x_range)
    jitter_y = random.randint(-y_range, y_range)
    jittered_x = x + jitter_x
    jittered_y = y + jitter_y
    pydirectinput.click(jittered_x, jittered_y)

def find_image_on_screen(image_path, confidence=0.8, grayscale=False):
    """
    Tries to find an image on the screen and returns its center coordinates.
    Returns None if the image is not found.
    """
    try:
        location = pyautogui.locateCenterOnScreen(
            image_path,
            confidence=confidence,
            grayscale=grayscale
        )
        return location
    except pyautogui.ImageNotFoundException:
        return None
    except Exception as e:
        log_event(f"ERROR: An error occurred while finding image: {e}")
        return None

def click_with_retry(image_path, confidence, grayscale, offset_x=0, offset_y=0, attempts=5, delay_between_attempts=1.0):
    """
    Finds and clicks an image on the screen with multiple retries.
    Returns True if the click was successful, False otherwise.
    """
    for attempt in range(attempts):
        location = find_image_on_screen(image_path, confidence=confidence, grayscale=grayscale)
        if location:
            click_x = location[0] + offset_x
            click_y = location[1] + offset_y
            log_event(f"Attempt {attempt + 1}/{attempts}: Clicking button at {location}...")
            jitter_click(click_x, click_y)
            time.sleep(random.uniform(0.5, 1.0))
            # Wait a moment and re-check if the screen has changed
            time.sleep(delay_between_attempts)
            # A simple way to check if the click worked is to see if the button is still there.
            # This is not foolproof but can help in many cases.
            new_location = find_image_on_screen(image_path, confidence=confidence, grayscale=grayscale)
            if not new_location or (abs(new_location[0] - location[0]) > 50 or abs(new_location[1] - location[1]) > 50):
                log_event("Click appears to have been successful.")
                return True
        else:
            log_event(f"Attempt {attempt + 1}/{attempts}: Button not found. Retrying in {delay_between_attempts} seconds...")
            time.sleep(delay_between_attempts)
    
    log_event(f"Failed to click the button after {attempts} attempts. Moving on.")
    return False

def click_battle_button(image_paths, game_mode):
    """
    Finds and clicks the battle button once, including a second click for 2v2 mode.
    Returns True if the click was successful, False otherwise.
    """
    battle_button_location = find_image_on_screen(image_paths['battle_button_image'], confidence=0.6)
    if battle_button_location:
        log_event("Clicking the main Battle button.")
        jitter_click(battle_button_location[0] + 0, battle_button_location[1] - 200) # First click
        time.sleep(1) # Wait for the screen to transition
        
        # Special handling for 2v2 mode
        if game_mode == "2v2":
            log_event("Selecting 2v2 mode with an additional click.")
            # Use the saved location to perform the second click
            jitter_click(battle_button_location[0] + 150, battle_button_location[1] - 400)
            time.sleep(random.uniform(1.0, 2.0))
        
        # A simple check to see if the battle button is still there. If it's not, the click likely succeeded.
        if not find_image_on_screen(image_paths['battle_button_image'], confidence=0.6):
            log_event("Battle button click successful. Searching for game...")
            return True
        else:
            log_event("Battle button still visible after click.")
            return False
    else:
        log_event("Battle button not found when trying to click.")
        return False

def check_image_assets(image_paths):
    """
    Checks if all required image assets exist and provides a status report.
    Reports missing assets and returns True if all are found, False otherwise.
    """
    found_assets = []
    missing_assets = []
    for name, path in image_paths.items():
        if os.path.exists(path):
            found_assets.append(f"  - '{name}' image found successfully.")
        else:
            missing_assets.append(f"  - ERROR: '{name}' image NOT found at: {path}")

    return found_assets, missing_assets

def format_duration(seconds):
    """
    Formats a duration in seconds into a string of days, hours, minutes, and seconds.
    """
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    parts.append(f"{seconds} second{'s' if seconds > 1 or seconds == 0 else ''}")

    return ", ".join(parts)

# --- Main Script Logic ---

def monitor_game_status(game_mode, image_paths):
    """
    The main monitoring loop for the game bot.
    """
    log_event(f"The King's Hand v1.0 initialized and ready. Selected mode: {game_mode}")
    print("-" * 50)
    log_event("Please ensure the game window is in focus.")
    log_event("All events will be logged to bot_log.txt")

    game_state = "unknown"
    start_time_finding_game = time.time()
    start_time_in_battle = None
    start_time_total = time.time()
    last_log_time = time.time()
    last_stats_log_time = time.time()
    games_completed = 0
    total_cards_placed = 0
    game_find_times = []
    battle_durations = []
    unknown_state_start_time = None
    last_battle_button_click_time = 0  # Track when we last clicked the battle button
    last_in_battle_detection_time = 0  # Track when we last detected being in battle
    battle_detection_lost_time = None  # Track when we first lost battle detection
    
    # Deques to store recent game data for calculating rolling averages
    games_completed_last_week = deque(maxlen=7)
    games_completed_last_month = deque(maxlen=30)


    while True:
        current_time = time.time()
        
        # Log general bot runtime every 10 seconds
        if current_time - last_log_time >= 10:
            total_runtime = current_time - start_time_total
            formatted_runtime = format_duration(total_runtime)
            log_event(f"Bot has been running for: {formatted_runtime}.")
            last_log_time = current_time

        # Print stats every 60 seconds
        if current_time - last_stats_log_time >= 40:
            total_runtime_seconds = current_time - start_time_total
            avg_find_time = sum(game_find_times) / len(game_find_times) if game_find_times else 0
            avg_battle_time = sum(battle_durations) / len(battle_durations) if battle_durations else 0
            avg_cards_per_game = total_cards_placed / games_completed if games_completed > 0 else 0
            
            # Calculate average games per hour and per day
            avg_games_per_hour = (games_completed / total_runtime_seconds) * 3600 if total_runtime_seconds > 0 else 0
            avg_games_per_24_hours = (games_completed / total_runtime_seconds) * 86400 if total_runtime_seconds > 0 else 0
            
            # Calculate weekly and monthly averages
            avg_games_per_week = (games_completed / total_runtime_seconds) * (86400 * 7) if total_runtime_seconds > 0 else 0
            avg_games_per_month = (games_completed / total_runtime_seconds) * (86400 * 30) if total_runtime_seconds > 0 else 0
            
            log_event("-" * 50)
            log_event("Current Automation Stats")
            log_event("-" * 50)
            log_event(f"  - Games Completed: {games_completed}")
            log_event(f"  - Avg. Game Find Time: {avg_find_time:.2f} seconds")
            log_event(f"  - Avg. Battle Duration: {avg_battle_time:.2f} seconds")
            log_event(f"  - Avg. Cards per Game: {avg_cards_per_game:.2f}")
            log_event(f"  - Avg. Games per Hour: {avg_games_per_hour:.2f}")
            log_event(f"  - Avg. Games per 24 Hours: {avg_games_per_24_hours:.2f}")
            log_event(f"  - Avg. Games per Week: {avg_games_per_week:.2f}")
            log_event(f"  - Avg. Games per Month: {avg_games_per_month:.2f}")
            log_event("-" * 50)
            last_stats_log_time = current_time

        # Reset unknown state timer on state change
        if game_state != "unknown":
            unknown_state_start_time = None
        
        # Check for in-battle marker with stability system
        in_battle_location = find_image_on_screen(image_paths['in_battle_image'], confidence=0.9)
        if in_battle_location:
            # Update the last detection time
            last_in_battle_detection_time = current_time
            battle_detection_lost_time = None  # Reset the lost detection timer
            
            if game_state != "in_battle":
                elapsed_finding_game = time.time() - start_time_finding_game
                log_event(f"Status: Detected you are in a battle. Found a game in {elapsed_finding_game:.2f} seconds.")
                game_find_times.append(elapsed_finding_game)
                game_state = "in_battle"
                start_time_in_battle = time.time()
            
            # Perform clicks while in battle
            log_event("Selecting and placing cards...")
            click1_x = in_battle_location[0] + 300
            click1_y = in_battle_location[1] - 100
            jitter_click(click1_x, click1_y)
            total_cards_placed += 1
            time.sleep(2)
            
            click2_x = click1_x
            click2_y = click1_y - 300
            jitter_click(click2_x, click2_y)
            total_cards_placed += 1
            time.sleep(1)
        
        # Handle case where in-battle marker is not detected
        elif game_state == "in_battle":
            # We were in battle but don't detect it now - start the stability timer
            if battle_detection_lost_time is None:
                battle_detection_lost_time = current_time
                log_event("Temporarily lost in-battle detection. Waiting for stability...")
            elif (current_time - battle_detection_lost_time) >= 5:
                # We've lost detection for 5+ seconds, consider battle actually ended
                log_event("In-battle detection lost for 5+ seconds. Battle likely ended.")
                game_state = "battle_ended_waiting_for_results"
                battle_detection_lost_time = None
            # If less than 5 seconds, continue as if still in battle but don't perform actions

        # Check for 2v2 end button (battle complete for 2v2)
        elif game_mode == "2v2" and find_image_on_screen(image_paths['two_v_two_end_image'], confidence=0.8, grayscale=True):
            if game_state not in ["battle_complete_2v2", "battle_ended_waiting_for_results"]:
                elapsed_in_battle = time.time() - start_time_in_battle if start_time_in_battle else 0
                log_event(f"Status: Battle finished. The battle lasted {elapsed_in_battle:.2f} seconds.")
                battle_durations.append(elapsed_in_battle)
                games_completed += 1
                log_event(f"The bot has finished {games_completed} game(s) so far.")
                game_state = "battle_complete_2v2"
                
                log_event("Clicking 2v2 end button.")
                click_with_retry(image_paths['two_v_two_end_image'], confidence=0.8, grayscale=True)
                time.sleep(2)  # Give time for screen transition
                game_state = "returning_to_menu"  # Reset state to allow Battle button detection
                start_time_finding_game = time.time()

        # Check for play again button (1v1 Trophy Road)
        elif game_mode == "1v1_trophy_road" and find_image_on_screen(image_paths['play_again_image'], confidence=0.8, grayscale=False):
            if game_state not in ["battle_complete_1v1_trophy_road", "battle_ended_waiting_for_results"]:
                elapsed_in_battle = time.time() - start_time_in_battle if start_time_in_battle else 0
                log_event(f"Status: Battle finished. The battle lasted {elapsed_in_battle:.2f} seconds.")
                battle_durations.append(elapsed_in_battle)
                games_completed += 1
                log_event(f"The bot has finished {games_completed} game(s) so far.")
                game_state = "battle_complete_1v1_trophy_road"
            
            log_event("Clicking Play Again button.")
            click_with_retry(image_paths['play_again_image'], confidence=0.8, grayscale=False)
            time.sleep(2)  # Give time for screen transition
            game_state = "returning_to_menu"  # Reset state to allow Battle button detection
            start_time_finding_game = time.time()

        # Check for OK button (battle complete - prioritize this over Battle button detection)
        elif find_image_on_screen(image_paths['ok_button_image'], confidence=0.5, grayscale=True):
            if game_state not in ["battle_complete_1v1", "battle_complete_1v1_trophy_road", "battle_ended_waiting_for_results"]:
                elapsed_in_battle = time.time() - start_time_in_battle if start_time_in_battle else 0
                log_event(f"Status: Battle finished. The battle lasted {elapsed_in_battle:.2f} seconds.")
                battle_durations.append(elapsed_in_battle)
                games_completed += 1
                log_event(f"The bot has finished {games_completed} game(s) so far.")
                game_state = "battle_complete_1v1"
            
            log_event("Clicking OK button to return to main menu.")
            click_with_retry(image_paths['ok_button_image'], confidence=0.5, grayscale=True, offset_x=-30)
            time.sleep(2)  # Give time for screen transition
            game_state = "returning_to_menu"  # Reset state to allow Battle button detection
            start_time_finding_game = time.time()

        # Check for Battle button (main menu) - use higher confidence to avoid false positives
        elif find_image_on_screen(image_paths['battle_button_image'], confidence=0.7):
            # Only avoid clicking if we just completed a battle and haven't processed the post-battle screen yet
            if game_state in ["battle_complete_1v1", "battle_complete_2v2", "battle_complete_1v1_trophy_road"]:
                # We just completed a battle, wait for the proper post-battle screen
                log_event("Battle button detected but ignoring since we just completed a battle. Waiting for proper post-battle screen...")
                time.sleep(1)
            # Also avoid clicking if we recently clicked the battle button (within 5 seconds)
            elif (current_time - last_battle_button_click_time) < 5:
                # We recently clicked the battle button, probably in a loading/transition state
                pass  # Do nothing, don't log spam
            # Also avoid if we're in unknown state (likely a transition screen)
            elif game_state == "unknown" and unknown_state_start_time and (current_time - unknown_state_start_time) < 3:
                # We're in an unknown state recently, probably a transition screen showing false battle button
                pass  # Do nothing, don't log spam
            else:
                # Safe to click the battle button - ensure we're actually on main menu
                if game_state != "not_in_battle":
                    log_event("Status: Detected main menu. Initiating new game...")
                    game_state = "not_in_battle"
                    
                    # Use the new retry function for the battle button
                    if click_battle_button(image_paths, game_mode):
                        last_battle_button_click_time = current_time  # Record successful click time
                    else:
                        log_event("Failed to click battle button. Re-entering loop to try again.")
                    start_time_finding_game = time.time()

        # If none of the known states are found, check for a fallback
        else:
            if game_state != "unknown":
                log_event("Status: Unknown or loading screen.")
                game_state = "unknown"
                unknown_state_start_time = time.time()
            
            # Reset battle completion states after some time to allow normal menu detection
            elif game_state in ["battle_complete_1v1", "battle_complete_2v2", "battle_complete_1v1_trophy_road"] and unknown_state_start_time and (current_time - unknown_state_start_time) > 5:
                log_event("Resetting battle completion state to allow normal menu detection.")
                game_state = "unknown"

            # Fallback for 1v1 Trophy Road mode if "playagain.png" is not found
            if game_mode == "1v1_trophy_road" and unknown_state_start_time and (current_time - unknown_state_start_time) > 10:
                ok_location = find_image_on_screen(image_paths['ok_button_image'], confidence=0.5, grayscale=True)
                if ok_location:
                    log_event("Status: In unknown state for too long. Found OK button as a fallback.")
                    
                    elapsed_in_battle = time.time() - start_time_in_battle if start_time_in_battle else 0
                    log_event(f"Status: Battle finished. The battle lasted {elapsed_in_battle:.2f} seconds.")
                    battle_durations.append(elapsed_in_battle)
                    games_completed += 1
                    log_event(f"The bot has finished {games_completed} game(s) so far.")
                    game_state = "battle_complete_1v1"

                    log_event("Clicking OK button to return to main menu.")
                    click_with_retry(image_paths['ok_button_image'], confidence=0.5, grayscale=True, offset_x=-30)
                    time.sleep(2)  # Give time for screen transition
                    game_state = "returning_to_menu"  # Reset state to allow Battle button detection
                    start_time_finding_game = time.time()
                    unknown_state_start_time = None # Reset the timer

        time.sleep(0.1)

# --- Entry Point ---
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Updated image paths to point to the 'assets' folder
    image_paths = {
        'battle_button_image': os.path.join(script_dir, 'assets', 'battle_button.png'),
        'ok_button_image': os.path.join(script_dir, 'assets', 'ok.png'),
        'play_again_image': os.path.join(script_dir, 'assets', 'playagain.png'),
        'two_v_two_end_image': os.path.join(script_dir, 'assets', '2v2end.png'),
        'in_battle_image': os.path.join(script_dir, 'assets', 'inbattle.png')
    }

    os.system('cls' if os.name == 'nt' else 'clear')
    print("-" * 50)
    print("  THE KING'S HAND - v1.0")
    print("  Website: https://jlaiii.github.io/TKH/")
    print("-" * 50)
    print("Verifying Image Assets...")
    
    found_assets, missing_assets = check_image_assets(image_paths)
    
    if found_assets:
        print("\nAssets Found:")
        for asset in found_assets:
            print(asset)
    
    if missing_assets:
        print("\nAssets Missing:")
        for asset in missing_assets:
            print(asset)
        print("\n" + "=" * 50)
        print("ERROR: One or more critical image assets are missing. The script cannot function correctly.")
        print("Please download the missing files from the GitHub repository and place them in the 'assets' folder.")
        print("Repository link: https://jlaiii.github.io/TKH/")
        input("Press Enter to exit...")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("All assets loaded successfully. The script is ready to run.")
    print("Choose a game mode to start the automation:")
    print("1. 1v1 Mode (Classic)")
    print("2. 2v2 Mode")
    print("3. 1v1 Trophy Road Mode")
    print("-" * 50)
    
    mode_selection = ""
    while mode_selection not in ["1", "2", "3"]:
        mode_selection = input("Enter 1, 2 or 3: ")
    
    if mode_selection == "1":
        monitor_game_status("1v1", image_paths)
    elif mode_selection == "2":
        monitor_game_status("2v2", image_paths)
    elif mode_selection == "3":
        monitor_game_status("1v1_trophy_road", image_paths)