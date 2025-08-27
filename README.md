# LoL Queue Assistant

![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A Python GUI tool to automate parts of the League of Legends pre-game experience, including accepting queues and handling champion picks & bans.

---

##  Features

| Feature | Description |
| :--- | :--- |
| **Auto-Accept Queue** | Automatically accepts the "Match Found" pop-up. |
| **Auto-Ban Champion** | Automatically bans a predefined champion during the ban phase. |
| **Auto-Pick Champion** | Automatically picks a predefined champion during the pick phase. |
| **Simple UI** | A clean interface with individual toggles for each feature. |

---

##  Getting Started

### Prerequisites

-   Python 3.7+
-   League of Legends Client (running on Windows)

### Installation

1.  **Clone or Download** the repository to your computer.
2.  **Install Dependencies** by opening a terminal in the project folder and running:

    ```bash
    pip install customtkinter requests
    ```

---

##  How to Use

1.  **Run the League Client**
    * Make sure the League of Legends client is open and you are logged in.

2.  **Run the Script**
    * Open a terminal in the script's folder and run:
        ```bash
        python bork.py
        ```
    *(Replace `bork.py` with the actual file name)*

3.  **Configure and Activate**
    * Enter the champion names you wish to auto-ban and/or auto-pick.
    * Toggle the features you want to enable using the switches.
    * Start a game queue. The application will monitor the client and perform the actions.

---

##  Compiling to .exe (Optional)

To create a standalone executable that doesn't require Python to be installed:

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Run the compile command:**
    ```bash
    pyinstaller --onefile --windowed --icon="icon.ico" bork.py
    ```
    The final `.exe` will be located in the `dist` folder.

---

> ###  Disclaimer
>
> This tool interacts with the local LCU API and is not affiliated with or endorsed by Riot Games. It does not interfere with gameplay. Use at your own risk. Incorrect usage (e.g., typos in champion names) may result in queue dodges.
