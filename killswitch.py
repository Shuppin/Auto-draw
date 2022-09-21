"""
Simple module which adds a background listener to kill the program when a key is pressed.
Particularly useful for programs which control input devices
"""
import threading
import _thread  # Internal threading module to raise exception in main
from pynput import keyboard
import sys


def _listen():
    def on_release(key):
        if key == keyboard.Key.f8:
            print("Closing program")
            _thread.interrupt_main()
            sys.exit()

    with keyboard.Listener(
            on_release=on_release) as listener:
        listener.join()

    listener = keyboard.Listener(
        on_release=on_release)
    listener.start()


def activate():
    """
    Activates killswitch
    """
    x = threading.Thread(target=_listen)
    x.start()

    print("Killswitch enabled")


if __name__ == '__main__':
    activate()

# :-) 38 lines is bad luck
