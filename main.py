import json
import time
from operator import sub
from os import walk
from typing import Union

from PIL import Image
from PIL import ImageGrab
from pynput.mouse import Controller, Listener, Button

import killswitch
from screen import get_bbox

killswitch.activate()  # press F8 to raise exception if all goes wrong

# Constants
SUPPORTED_TYPES = [".bmp", ".gif", ".jpeg", ".jpg", ".png"]
CLICK_INTERVAL = 1/100

mouse = Controller()  # monitor and control mouse movement


def list_choice(selection_list: Union[list, dict], invalid_text="Invalid choice!") -> int:
    """Retrieves and sanitises user input based off list

    **Parameters**

    `selection_list`: List to choose options from

    `invalid_text`: Text which gets printed when user inputs invalid value

    **Returns**

    List index `(int)` of `selection_list`
    """
    while True:
        try:
            choice = input("> ")
            choice = int(choice)
            if 0 >= choice or choice >= len(selection_list) + 1:
                print(invalid_text)
            else:
                return choice-1
        except ValueError:
            print(invalid_text)


def get_nearest_colour(colour: tuple, palette: dict) -> tuple:
    """Approximates the closest colour given the available palette

    **Parameters**

    `colour`: RGB tuple to compare, format (255, 255, 255)

    `palette`: Dictionary containing available colours

    **Returns**

    RGB tuple, format (255, 255, 255)
    """
    colour_comparisons = []
    for palette_colour in palette.keys():
        # the following line subtracts both tuples, and produce a sum of all the absolute values.
        # it then adds that values to a list
        colour_comparisons.append(sum([abs(y) for y in list(map(sub, eval(palette_colour), colour))]))

    # and which ever value has the lowest values in the list is the closest colour
    closest_colour_index = colour_comparisons.index(min(colour_comparisons))

    # I was having strange issues with memory so this gets manually deleted
    del colour_comparisons

    # `palette` stores values as strings, so they must be evaluated to return the tuple counterpart
    # eval() is dangerous, might change later
    return eval(list(palette.keys())[closest_colour_index])


def setup():
    """
    Procedure to set up positions of canvas and colour palette
    """
    palette = {}

    print("Please select the drawing area (canvas)")

    # get the bounding box coordinates (x1, y1, x2, y2) of canvas
    canvas = get_bbox()

    print("Left click on the location of each colour on the palette, or right click to cancel/finish.")

    def _on_click(x, y, button, pressed):
        """
        Gets called whenever pynput sends a click event
        """

        # if user clicks left button
        if not pressed and button == Button.left:

            screenshot = ImageGrab.grab()  # gets a screenshot of the screen
            screenshot = screenshot.convert('RGB')  # removes any transparent pixels
            r, g, b = screenshot.getpixel((x, y))  # finds colour of pixel that was clicked

            valid = True

            # checking if the colour pressed is already in the palette
            for item in palette.keys():
                if item == str((r, g, b)):
                    print("Colour", (r, g, b), "already exists at", palette[str((r, g, b))])
                    valid = False

            # if not, add the colour to palette
            if valid:
                palette[str((r, g, b))] = (x, y)
                print('Added colour #%02x%02x%02x' % (r, g, b), "at position", (x, y))

        # if user clicks right button
        elif not pressed and button == Button.right:
            if len(palette) == 0:
                print("Please choose at 1 colour before continuing")
            else:
                return False  # finish palette configuration

    # activate mouse listener
    listener = Listener(on_click=_on_click)

    listener.start()
    listener.join()

    # load config from file
    with open('config.json') as json_file:
        configs = json.load(json_file)
        configs = dict(configs)

    print("What would you like to name this configuration?")

    # get input and validate it
    while True:
        filename = input("> ")

        # ensures filename is compatible with (most) operating systems
        keep_characters = (' ', '.', '_')
        "".join(c for c in filename if c.isalnum() or c in keep_characters).rstrip()

        if filename in configs.keys():
            print("A configuration with that name already exists!")
        else:
            break

    # save filename in config
    configs[filename] = {}

    configs[filename]['palette'] = palette
    configs[filename]['canvas'] = canvas

    # save palette, canvas and filename information to file
    with open('config.json', 'w') as outfile:
        json.dump(configs, outfile, indent=2)


# noinspection PyUnresolvedReferences
def draw():
    """
    Procedure to select all configurations options and draw image to screen
    """

    # TODO: ignore white pixels all together

    # load config from file
    with open('config.json') as json_file:
        configs = json.load(json_file)
        configs = dict(configs)

    if len(configs) <= 0:
        print("No configurations detected!")
        print("Please use the setup option before using the draw option!")
        return

    # get configuration choice from user
    print("Enter configuration")
    for configs_index, config_option in enumerate(configs.keys()):
        print(f"{configs_index + 1}) {config_option}")

    configs_choice = list_choice(configs, invalid_text="Invalid config option!")

    config = configs[list(configs.keys())[configs_choice]]

    # get names of all valid images in `./img/` folder (assuming it already exists)
    image_names = []
    for (_, _, filenames) in walk("./img"):
        for filename in filenames:
            for file_type in SUPPORTED_TYPES:
                if filename.endswith(file_type):
                    image_names.append(filename)

    # get image choice from user
    print("Chose an image")
    for image_names_index, image_name in enumerate(image_names):
        print(f"{image_names_index+1}) {image_name}")

    image_choice = list_choice(image_names)
    image_file = "./img/" + image_names[image_choice]

    # get resolution scaling choice from user
    resolutions = [1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/8, 1/10]
    resolutions_text = ["1", "1/2", "1/3", "1/4", "1/5", "1/6", "1/8", "1/10"]

    print("Choose resolution scale")
    for res_index, resolution in enumerate(resolutions_text):
        print(f"{res_index + 1}) {str(resolution)}")

    res_choice = list_choice(resolutions)
    resolution_scale_factor = int(1/resolutions[res_choice])  # 1/2 -> 2

    image = Image.open(image_file)  # load image

    # TODO: convert transparent pixels to white instead of black
    image = image.convert('RGB')  # remove any transparent pixels

    # appropriately scale image up/down, while maintaining aspect ratio
    (x1, y1, x2, y2) = config['canvas']

    smallest_canvas_edge = min((x2 - x1, y2 - y1))
    largest_image_edge = max((image.size[0], image.size[1]))

    scale_factor = (smallest_canvas_edge / largest_image_edge)

    resized_image = image.resize((round(image.size[0]*scale_factor), round(image.size[1]*scale_factor)))

    print("Recolouring image...", end="\r")

    pixels = resized_image.load()  # get pixels generator object

    # replace all (or within resolution scale) pixels within image with colours from colour palette
    for i in range(0, resized_image.size[0], resolution_scale_factor):
        for j in range(0, resized_image.size[1], resolution_scale_factor):
            colour = get_nearest_colour(pixels[i, j], config['palette'])
            pixels[i, j] = colour

    print("Recolouring image... Done!")
    print("")
    print("Printing image...", end="\r")

    pixels = resized_image.load()  # override old pixels, get pixels generator object with the new pixels

    # draw to screen
    for y in range(0, resized_image.size[1], resolution_scale_factor):
        # every row

        current_colour_coords = config['palette'][str(pixels[0, y])]  # get coordinates of current colour
        mouse.position = tuple(current_colour_coords)  # move mouse to location of desired colour
        time.sleep(CLICK_INTERVAL)
        mouse.press(Button.left)  # select colour
        mouse.release(Button.left)
        time.sleep(CLICK_INTERVAL)

        for x in range(0, resized_image.size[0], resolution_scale_factor):
            # every pixel

            mouse.position = (x+x1, y+y1)  # move mouse to position
            # out of bounds check
            if x+x1 > x2+5 or y+y1 > y2+5:
                print("Out of bounds! Cancelling operation")
                return
            mouse.press(Button.left)  # hold down left mouse

            # checking if second to last pixel
            if x < resized_image.size[0]-resolution_scale_factor:

                # if next pixel is not same, change colour
                if pixels[x, y] != pixels[x+resolution_scale_factor, y]:

                    time.sleep(CLICK_INTERVAL)
                    mouse.release(Button.left)

                    # same code as above
                    current_colour_coords = config['palette'][str(pixels[x+resolution_scale_factor, y])]
                    mouse.position = tuple(current_colour_coords)
                    time.sleep(CLICK_INTERVAL)
                    mouse.click(Button.left)
                    time.sleep(CLICK_INTERVAL)

        time.sleep(CLICK_INTERVAL)  # give time for website to catch up before proceeding to next row
        mouse.release(Button.left)

    mouse.release(Button.left)  # release mouse button so use can move their mouse without messing up output

    resized_image.show()  # show image at the end

    print("Printing image... Done!")  # done! :)


actions = [draw, setup]

while True:
    try:
        mode = None

        # choose operation
        print("Enter action")
        for action_index, operation in enumerate(actions):
            print(f"{action_index+1}) {operation.__name__}")

        mode_choice = list_choice(actions, invalid_text="Invalid mode!")

        mode = actions[mode_choice]

        # TODO: add repeatability to whole program
        mode()  # execute

    except KeyboardInterrupt:
        print("Bye Bye!")
        exit()
