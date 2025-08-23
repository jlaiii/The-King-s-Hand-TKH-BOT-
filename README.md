# The King's Hand TKH BOT

This bot automates gameplay in Clash Royale. It uses image recognition to find game elements and perform actions like clicks. It's designed to work with **Google Play Games PC**.

## Prerequisites

* **Google Play Games PC**: The bot is built for the game's interface on this platform. Get it here: [https://play.google.com/googleplaygames](https://play.google.com/googleplaygames)
* **Python**: You must have Python installed. Download it here: [https://www.python.org/downloads/](https://www.python.org/downloads/)
* **Game Window**: The game must be open and active on your screen.

---

## How to Install & Run

### Step 1: Download the Files

1.  Download the bot's main script, `TKH.py`.
2.  Also download the required image assets: `battle_button.png`, `ok.png`, `playagain.png`, `2v2end.png`, and `inbattle.png`.

**Important**: Create a new folder for the bot. Place `TKH.py` in the main folder and put all the `.png` files inside a new subfolder named **`assets`**.

### Step 2: Run the Bot

1.  **Double-click `TKH.py`**. The script will automatically install the needed libraries (`pyautogui` and `pydirectinput`) if you don't have them.
2.  If that fails, open your terminal or command prompt, navigate to the bot's folder, and run:
    ```bash
    pip install pyautogui pydirectinput
    python TKH.py
    ```

### Step 3: Choose a Game Mode

A menu will appear asking you to choose a game mode:
* `1`: 1v1 Mode
* `2`: 2v2 Mode
* `3`: 1v1 Trophy Road Mode

Enter your choice and press **Enter**.

The bot will now begin monitoring your screen and playing the game automatically.

---

## How It Works

The bot operates by continuously monitoring the screen for specific images that represent different game states:

* **Main Menu**: It looks for `battle_button.png`. Once found, it clicks the button to start a new game.
* **In-Battle**: It detects the `inbattle.png` marker to know it's in a live match. While in a battle, it performs "jitter clicks" (clicks with a random offset) to place cards on the screen.
* **Battle Complete**:
    * For 1v1, it looks for the `ok.png` button to end the match and return to the main menu.
    * For 2v2, it looks for the `2v2end.png` button to end the match.
    * For 1v1 Trophy Road, it looks for the `playagain.png` button to start another match or `ok.png` as a fallback.
