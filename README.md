S.C.S - Stratagem Control System
A standalone desktop utility for Helldivers 2, designed to make using stratagems faster and more reliable. This tool is focused on improving accessibility for players with physical limitations and providing freedom of play for those who prefer a more tactical experience over input dexterity.

This application is built with Python and does not modify any game files.

Why This Project is Open Source
The core function of this application requires listening to keyboard/mouse inputs and simulating key presses. This behavior is similar to how some malicious software operates, which can cause antivirus programs to flag the application as a potential threat (a "false positive").

By making this project fully open source, my goal is to be 100% transparent. You can examine every line of code in this repository to verify for yourself that the application is safe and does exactly what is described. There is nothing hidden.

How to Verify the Safety of the .exe
If you don't want to build from the source yourself, you can still verify the pre-compiled .exe file provided in the Releases section.

Download the .exe file.

Go to a site like VirusTotal.com.

Upload the .exe file.

VirusTotal will scan the file with over 70 different antivirus engines. You will see that while a few heuristic engines may flag it as "Riskware" (due to its macro-like behavior), the vast majority will report it as clean.

Features
12 Fully Customizable Hotkey Slots

Universal Hotkey Support: Keyboard, Numpad, F-Keys, and Side Mouse Buttons.

Advanced Profile Management: Save and load different loadouts for different missions.

In-Game Overlays: Toggleable status dot and a semi-transparent hotkey reminder list.

Deep Customization: Configure the stratagem menu key, global toggle key, input timings, and choose between Arrow Keys or WASD for macro input.

Building from Source
If you prefer not to use the pre-compiled executable, you can run the project directly from the source code.

Prerequisites:

Python 3.x installed on your system.

Your icon.ico file in the project directory.

Setup:

Clone this repository:

git clone https://github.com/your-username/SCS-Stratagem-Control-System.git
cd SCS-Stratagem-Control-System

Install the required libraries:

pip install PyQt6 pynput pyautogui pydirectinput

Run the application:

python your_script_name.py

License
This project is licensed under the MIT License. See the LICENSE file for details.