=========================
  LoL Queue Assistant
=========================

A Python-based GUI tool to automate parts of the League of Legends pre-game experience, including accepting queues and handling champion picks & bans.


--- Features ---

- Auto-Accept Queue: Automatically accepts the "Match Found" pop-up.
- Auto-Ban Champion: Automatically bans a predefined champion during the ban phase.
- Auto-Pick Champion: Automatically picks a predefined champion during the pick phase.
- Simple UI: A clean interface with individual toggles for each feature.


--- Requirements ---

- Python 3.7+
- League of Legends Client (running on Windows)


--- Setup ---

1. Clone or Download
   Download the .py script to a folder on your computer.

2. Install Dependencies
   Open a terminal in the script's folder and run:

   pip install customtkinter requests


--- Usage ---

1. Run the League Client
   Make sure the League of Legends client is open and you are logged in.

2. Run the Script
   Open a terminal in the script's folder and run:
   
   python your_script_name.py

   (Replace "your_script_name.py" with the actual file name)

3. Configure and Activate
   - Enter the champion names you wish to auto-ban and/or auto-pick in the text fields.
   - Toggle the features you want to enable using the switches.
   - Start a game queue. The application will monitor the client and perform the activated actions.


--- Compiling to .exe (Optional) ---

To create a standalone executable:

1. Install PyInstaller:
   pip install pyinstaller

2. Run the command:
   pyinstaller --onefile --windowed --icon="your_icon.ico" your_script_name.py


--- Disclaimer ---

This tool interacts with the local LCU API and is not affiliated with or endorsed by Riot Games. It does not interfere with gameplay. Use at your own risk. Incorrect usage (e.g., typos in champion names) may result in queue dodges.
