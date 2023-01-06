"""Package that allows to create contents for displaying on a remote matrix."""
__version__ = "0.1"

import json
from abc import ABC, abstractmethod
from typing import List, Union
from PIL import Image as PILImage


class Flattenable(ABC):
    """Interface that allows flattening of objects."""

    @abstractmethod
    def flatten(self) -> Union[dict, list]:
        """Flatten the object into a dictionary."""
        raise NotImplementedError

    def to_json(self) -> str:
        """Convert the object into a JSON string."""
        return json.dumps(self.flatten())

    def save_json(self, path: str):
        """Save the object as a JSON file."""
        with open(path, "w") as f:
            f.write(self.to_json())


class MatrixContent(Flattenable):
    """
    Class that represents a content for a remote matrix.
    The content may contain multiple frames which in turn contain an arbitrary number of elements.
    """
    frames: List["Frame"]
    current_index = 0

    def __init__(self):
        self.frames = [Frame()]

    def frame(self, index: int = None) -> "Frame":
        """Return the frame at the given index or the current frame if no index is given."""
        if index is None:
            return self.frames[self.current_index]
        return self.frames[index]

    def new_frame(self) -> "Frame":
        """Create a new frame and return it."""
        self.current_index += 1
        self.frames.append(Frame())
        return self.frames[self.current_index]

    def flatten(self) -> dict:
        """Flatten the matrix content into a list of frames."""
        return {
            "type": "matrix",
            "frames": [frame.flatten() for frame in self.frames]
        }


class Frame(Flattenable):
    """
    Class that represents a frame for a remote matrix.
    A frame contains an arbitrary number of elements.
    """
    elements: List['ContentPiece']
    duration: float

    def __init__(self, elements=None, duration: float = 0):
        if elements is None:
            elements = []
        self.elements = elements
        self.duration = duration

    def add(self, element: 'ContentPiece'):
        """Add an element to the frame."""
        self.elements.append(element)

    def remove(self, element: 'ContentPiece'):
        """Remove an element from the frame."""
        self.elements.remove(element)

    # enable += operator
    def __iadd__(self, other: 'ContentPiece'):
        self.add(other)

    def flatten(self) -> Union[dict, list]:
        """Flatten the frame into a dictionary."""
        return {
            "type": "frame",
            "duration": self.duration,
            "elements": [element.flatten() for element in self.elements]
        }


class Color(Flattenable):
    """
    Class that represents a color.
    """
    r: int
    g: int
    b: int

    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    # Method to get hex code:
    def hex(self) -> str:
        """Return the hex code of the color."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    # Enable hex(x) call
    __hex__ = hex

    def flatten(self) -> dict:
        """Flatten as hex code"""
        return {
            "color": self.hex()
        }


class Location(Flattenable):
    """
    Class that represents a location.
    """
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def flatten(self) -> dict:
        return {
            "x": self.x,
            "y": self.y
        }


class ContentPiece(Flattenable, ABC):
    """
    Class that represents an element for a remote matrix.
    This class is abstract
    """
    color: Color
    location: Location

    def __init__(self, location: Location = None, color: Color = None):
        self.color = color
        if self.color is None:
            self.color = Color(255, 255, 255)
        self.location = location
        if self.location is None:
            self.location = Location(0, 0)

    def flatten(self) -> Union[dict, list]:
        """Flatten the content piece into a dictionary."""
        return {
            **self.color.flatten(),
            **self.location.flatten()
        }


class Text(ContentPiece):
    """
    Class that represents a text element for a remote matrix.
    """

    def __init__(self, text: str, location: Location = None, color: Color = None):
        super().__init__(location, color)
        self.text = text

    def flatten(self) -> dict:
        return {
            "type": "text",
            "text": self.text,
            **super().flatten()
        }


class Circle(ContentPiece):
    """
    Class that represents a circle element for a remote matrix.
    """
    radius: int
    fill: bool

    def __init__(self, radius: int, fill: bool = True, location: Location = None, color: Color = None):
        super().__init__(location, color)
        self.fill = fill
        self.radius = radius

    def flatten(self) -> dict:
        return {
            "type": "circle",
            "radius": self.radius,
            "fill": self.fill,
            **super().flatten()
        }


class Pixel(ContentPiece):
    """
    Class that represents a pixel element for a remote matrix.
    """

    def __init__(self, location: Location = None, color: Color = None):
        super().__init__(location, color)

    def flatten(self) -> dict:
        return {
            "type": "pixel",
            **super().flatten()
        }


class Triangle(ContentPiece):
    """
    Class that represents a triangle element for a remote matrix.
    """
    p1: Location
    p2: Location
    p3: Location
    fill: bool

    def __init__(self, p1: Location, p2: Location, p3: Location, fill: bool = True, color: Color = None):
        super().__init__(None, color)
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.fill = fill

    def flatten(self) -> dict:
        return {
            "type": "triangle",
            "p1": self.p1.flatten(),
            "p2": self.p2.flatten(),
            "p3": self.p3.flatten(),
            "color": self.color.flatten()
        }


class Rectangle(ContentPiece):
    """
    Class that represents a rectangle element for a remote matrix.
    """
    width: int
    height: int
    fill: bool

    def __init__(self, width: int, height: int, fill=True, location: Location = None, color: Color = None):
        super().__init__(color, location)
        self.width = width
        self.height = height
        self.fill = fill

    def flatten(self) -> dict:
        return {
            "type": "rect",
            "width": self.width,
            "height": self.height,
            "fill": self.fill,
            **super().flatten()
        }


class Line(ContentPiece):
    """
    Class that represents a line element for a remote matrix.
    """
    end_location: Location

    def __init__(self, start_location: Location = None, end_location: Location = None, color: Color = None):
        super().__init__(start_location, color)
        self.end_location = end_location
        if self.end_location is None:
            self.end_location = Location(0, 0)

    def flatten(self) -> dict:
        return {
            "type": "line",
            "end_location": self.end_location.flatten(),
            **super().flatten()
        }


class Image(ContentPiece):
    """
    Class that represents a bitmap element for a remote matrix.
    """
    image: PILImage

    def __init__(self, filename, location: Location = None):
        super().__init__(location)
        self.image = PILImage.open(filename).convert("RGB")

    def flatten(self) -> dict:
        # get width and height of image
        width, height = self.image.size
        # If a lot of different colors are present encode image as list of pixels
        # Otherwise encode colors and reference them

        # Check if count of colors are below 10 or < 50% of the total pixels
        if len(self.image.getcolors()) < 10 or \
                len(self.image.getcolors()) < self.image.size[0] * self.image.size[1] / 2:
            # Use colors as a list, reference them
            colors = list(self.image.getcolors())
            # Sort colors by count
            colors.sort(key=lambda x: x[0], reverse=True)
            # Remove count from colors
            colors = [color[1] for color in colors]
            # Make pixel as reference to color
            pixels = []
            for pixel in self.image.getdata():
                pixels.append(colors.index(pixel))
            return {
                "type": "image",
                "width": width,
                "height": height,
                "colors": [Color(*pixel).hex() for pixel in colors],
                "pixels": pixels,
                "location": self.location.flatten()
            }
        else:
            # Encode as list of pixels
            return {
                "type": "image",
                "width": width,
                "height": height,
                "pixels": [Color(*pixel).hex() for pixel in self.image.getdata()]
            }
