# The King's Hand TKH BOT

This is a simple bot designed to automate gameplay in a specific mobile game on a computer. It works by using image recognition to identify the current game state and performing actions like clicks to progress through battles.

## Important Prerequisites

* **Ensure the Game is Running**: The game must be open and in focus on your screen for the bot to work correctly.
* **Install Python**: You need to have Python installed on your system. You can download it from the official Python website: https://www.python.org/downloads/

## How to Set Up and Run

1.  **Download the Files**:
    * `bot.py`
    * `battle_button.png`
    * `ok.png`
    * `2v2end.png`
    * `inbattle.png`

    Make sure all these files are in the same folder.

2.  **Run the Bot**:
    * **Method 1 (Recommended)**: Double-click the `bot.py` file. The script is designed to automatically check for and install the required Python libraries (`pyautogui` and `pydirectinput`) if they are missing.
    * **Method 2 (Manual Installation)**: If the automatic installation fails, open a terminal or command prompt, navigate to the folder where you saved the files, and run the following commands to install the necessary libraries manually:
        ```bash
        pip install pyautogui
        pip install pydirectinput
        ```
        Then, run the script with the command:
        ```bash
        python bot.py
        ```

3.  **Choose a Game Mode**:
    * After starting the script, a command window will appear and prompt you to select a game mode:
        * **1** for 1v1
        * **2** for 2v2
    * Enter your choice and press Enter.

4.  **Start the Game**:
    * Ensure the game is the active window.
    * The bot will now begin monitoring the screen and will start playing automatically.

## How the Bot Works

The bot operates by continuously monitoring the screen for specific images that represent different game states:

* **Main Menu**: It looks for `battle_button.png`. Once found, it initiates a new game by clicking the appropriate location.
* **In-Battle**: It detects the `inbattle.png` marker to know it's in a live match. While in a battle, it performs a series of "jitter clicks" (clicks with a random offset) to place cards on the screen.
* **Battle Complete**:
    * For 1v1, it looks for the `ok.png` button to confirm the end of the match.
    * For 2v2, it looks for the `2v2end.png` button to confirm the end of the match.

The bot uses **image recognition** and **screen coordinates** to automate its actions, making sure it can handle different screen resolutions by using relative positions from the detected images.
