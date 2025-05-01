import numpy as np
from shoulder_surfer_gui import closest_color, guess_to_colors, guess_to_emojis

def test_closest_color():
    assert closest_color((255, 0, 0)) == "red"
    assert closest_color((0, 255, 255)) == "cyan"

def test_guess_to_colors():
    result = guess_to_colors([0, 1, 2])
    assert result == ["red", "magenta", "navy"]

def test_guess_to_emojis():
    result = guess_to_emojis([0, 1, 2])
    assert result == ["😀", "😎", "🐱"]
