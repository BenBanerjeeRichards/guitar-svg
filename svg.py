# Very simple SVG generation
# Uses simple string formatting
# Uses python dictionary API
from typing import *


class SvgLine:

    def __init__(self, x1, y1, x2, y2, width=2, endcap=False):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.width = width
        self.endcap = endcap


class Barre:

    def __init__(self, fret: int, string_start: int, string_end: int):
        # Remember that strings decrease
        assert string_start > string_end
        self.fret = fret
        self.string_start = string_start
        self.string_end = string_end


class Shape:

    def __init__(self, muted_strings: List[int], starting_fret: int, positions: List[Tuple[int, int]], barre=None):
        self.barre = barre
        self.positions = positions
        self.starting_fret = starting_fret
        self.muted_strings = muted_strings


VERTICAL = [15, 31, 47, 63, 79, 95]
HORIZONTAL = [10, 27, 44, 61, 78, 95]

# Various padding around the main grid
VERT_START = 10
VERT_END = 95
HOR_START = 14.6
HOR_END = 95

WIDTH = 200
HEIGHT = 250

ENDCAP_CORRECTION = 2.4


def generate_item(tag, attrs) -> str:
    attrs_str = ""
    for k, v in attrs.items():
        attrs_str += "{}=\"{}\" ".format(k, v)

    return "<{} {}/>".format(tag, attrs_str)


def generate_line(line: SvgLine):
    style = "stroke:rgb(0, 0, 0);stroke-width:{}".format(line.width)
    endcap = "stroke-linecap=\"round\"" if line.endcap else ""
    return "<line x1=\"{}%\" y1=\"{}%\" x2=\"{}%\" y2=\"{}%\" style=\"{}\" {}/>".format(line.x1, line.y1, line.x2,
                                                                                        line.y2, style, endcap)


def generate_circle(pos):
    return "<circle cx=\"{}%\" cy=\"{}%\" r=\"4%\"/>".format(pos[0], pos[1])


def generate_text(text: str, x, y, font_size, text_anchor=None, alignment_baseline=None):
    props = ""
    if text_anchor is not None:
        props += " text-anchor=\"{}\"".format(text_anchor)

    if alignment_baseline is not None:
        props += " alignment-baseline=\"{}\"".format(alignment_baseline)

    return "<text x=\"{}%\" y=\"{}%\" font-size=\"{}em\" {}>{}</text>".format(x, y, font_size, props, text)


def comment(text):
    return "<!-- {} -->".format(text)


def generate_start(width, height):
    return """
<svg version="1.1"
     baseProfile="full"
     xmlns="http://www.w3.org/2000/svg"
     width="{}pt"
     height="{}pt">
    """.format(width, height)


def generate_svg(width, height, items):
    svg = generate_start(width, height)
    svg += "\n"
    for item in items:
        svg += "\t" + item + "\n"
    svg += "</svg>"
    return (svg)


def string_no(string):
    if string == "E":
        return 6
    if string == "A":
        return 5
    if string == "D":
        return 4
    if string == "G":
        return 3
    if string == "B":
        return 2
    if string == "e":
        return 1


def dot_coords(string: int, fret: int):
    string_pos = VERTICAL[6 - string]
    fret_pos = (HORIZONTAL[fret - 1] + HORIZONTAL[fret]) / 2.0
    return (string_pos, fret_pos)


def generate_chord(shape: Shape):
    # Generate basic table
    grid = []
    items = []
    # Vertical strings
    for vert in VERTICAL:
        grid.append(SvgLine(vert, VERT_START, vert, VERT_END))

    # Horizontal fret wires excluding first one (this one might be bold if not a barre chord)
    for hor in HORIZONTAL[1:]:
        grid.append(SvgLine(HOR_START, hor, HOR_END, hor))

    # Handle first fret wire and fret number
    if shape.starting_fret == 1:
        # Solid bold line for first fret wire
        grid.append(SvgLine(HOR_START, HORIZONTAL[0], HOR_END, HORIZONTAL[0], width=5))
    else:
        # We need add a fret number and thin line
        grid.append(SvgLine(HOR_START, HORIZONTAL[0], HOR_END, HORIZONTAL[0], width=2))
        items.append(
            generate_text(str(shape.starting_fret), 1, (HORIZONTAL[0] + HORIZONTAL[1]) / 2, 2, None, "central"))

    if shape.barre is not None:
        barre_y = (HORIZONTAL[shape.barre.fret - 1] + HORIZONTAL[shape.barre.fret]) / 2
        barre_x1 = VERTICAL[6 - shape.barre.string_start] + ENDCAP_CORRECTION
        barre_x2 = VERTICAL[6 - shape.barre.string_end] - ENDCAP_CORRECTION

        grid.append(SvgLine(barre_x1, barre_y, barre_x2, barre_y, width=20, endcap=True))

    items = items + list(map(lambda x: generate_line(x), grid))

    # Add our open dots
    for string, fret in shape.positions:
        items.append(generate_circle(dot_coords(string, fret)))

    # Muted strings
    for mute in shape.muted_strings:
        items.append(generate_text("x", VERTICAL[(6 - mute)], 6, 2, "middle", None))

    return generate_svg(WIDTH, HEIGHT, items)


def main():
    svg = generate_chord(Shape([6, 2], 1, [(2, 3)], Barre(1, 6, 2)))
    with open("out.svg", "w+") as f:
        f.write(svg)


if __name__ == '__main__':
    main()
