# Auto-draw

A small program which will take and input file and draw it using the mouse and available colours

### Features
- Automagically draw .png or .jpg files on apps like [garticphone](https://garticphone.com/) and [skribbl.io](https://skribbl.io/) using the mouse
- Simple setup utility
- Configure & save presets to use later
- Image scaling to improve speed

### Installation
- Clone repository using `git clone https://github.com/Shuppin/Auto-draw`
- Navigate to the cloned directory and open a terminal
- In the terminal type `pip install -r requirements.txt`

### Usage
- Run `main.py` using `python3 main.py`
- When you run the program you will be presented with 2 options
- You won't have any configurations yet so lets make one
- Select option 2 (setup) and follow the on-screen prompts
    - If the program stops at this point the canvas window might not have opened properly
    - Just click on the icon in the taskbar to open it
- Once you have created your configuration you can now use the draw function
- Select option 1 (draw) and follow the on-screen prompts

### Notes
- Only tested in Python 3.9

## TODO
- Add command line arguments for quicker use
- Automatically detect colours
- Add dynamic presets which change depending on resolution
