# Aim Trainer

## Overview
Aim Trainer is a simple aim training application written in Python using Pygame. It helps you improve your mouse accuracy and reaction time, similar to popular FPS games like Counter-Strike 2.

## How to Run
To start the application, simply run:

```
python main.py
```

This will launch the main menu window.

## File Descriptions

### menu.py
- This file contains the main menu interface.
- Allows you to:
  - Start the aim training game
  - Change mouse sensitivity (with a CS2-like formula)
  - Change crosshair color
  - View a preview image
  - Exit the application
- All settings are saved to `settings.json`.

### aim_sec.py
- This file contains the main aim training game logic.
- Features:
  - Targets appear on the screen, and you must click them as quickly as possible
  - Mouse sensitivity is applied using a formula similar to CS2
  - Your score, accuracy, and high score are displayed at the end
  - The high score is saved in `settings.json`

## Screenshots

### Main Menu
![image](https://github.com/user-attachments/assets/e80cffd6-d1b0-4b7f-9c9d-3921e535a79f)


### Aim Trainer Game
![image](https://github.com/user-attachments/assets/a7dabcb5-45cf-4ef2-a054-d71c46013e2e)
![image](https://github.com/user-attachments/assets/e5aaab99-32af-4f7d-83a2-709a10635b6c)


---

**Enjoy training your aim!** 
