class GuiAssets:

    def __init__(self) -> None:

        self.menu_header = [
            "███╗   ██╗███████╗██╗    ██╗███████╗    ██████╗  ██████╗ ████████╗    ██████╗  ██████╗  ██████╗  ██████╗ ",
            "████╗  ██║██╔════╝██║    ██║██╔════╝    ██╔══██╗██╔═══██╗╚══██╔══╝    ╚════██╗██╔═████╗██╔═████╗██╔═████╗",
            "██╔██╗ ██║█████╗  ██║ █╗ ██║███████╗    ██████╔╝██║   ██║   ██║        █████╔╝██║██╔██║██║██╔██║██║██╔██║",
            "██║╚██╗██║██╔══╝  ██║███╗██║╚════██║    ██╔══██╗██║   ██║   ██║       ██╔═══╝ ████╔╝██║████╔╝██║████╔╝██║",
            "██║ ╚████║███████╗╚███╔███╔╝███████║    ██████╔╝╚██████╔╝   ██║       ███████╗╚██████╔╝╚██████╔╝╚██████╔╝",
            "╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚══════╝    ╚═════╝  ╚═════╝    ╚═╝       ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ",
        ]

        self.robot_parts = {
            "base": ["  ╒╛_`──'_──_`──'_╘╕  ", "╭╼╡ ╭────────────╮ ╞╾╮",
                     "│ │ ││          ││ │ │", "│ │ ││          ││ │ │",
                     "│ │ ││          ││ │ │", "╰╼╡ │/┅┅┅┅┅┅┅┅┅┅\│ ╞╾╯",
                     "  ╰─────┬───┬──────╯  ", "      ╭─╯ ╿ ╰─╮       "],
            "right": ["     ,──.    ,──.     ", "   ╭(( ◎))┅┅(( ܘ))╮   "],
            "left": ["     ,──.    ,──.     ", "   ╭((◎ ))┅┅((ܘ ))╮   "],
            "sad":  ["     ____    ____     ", "   ╭(,──.)┅┅(,──.)╮   "]
        }

    def draw_box(self, frame, height: int, width: int, pos_y: int, pos_x: int) -> None:
        """Draws a rectangle based on x and y for starting coordinates, and width and height for size"""

        # Draw horizontal edges, leaving room for corner pieces
        for i in range(pos_x, pos_x + width - 1):
            frame.addstr(pos_y, i, '─')
            frame.addstr(pos_y + height - 1, i, '─')

            # Draw vertical edges, leaving room for corner pieces
            for j in range(pos_y, pos_y + height - 1):
                frame.addstr(j, pos_x, '│')
                frame.addstr(j, pos_x + width - 1, '│')

            # Draw the corners
            frame.addstr(pos_y, pos_x, '╭')
            frame.addstr(pos_y, pos_x + width - 1, '╮')
            frame.addstr(pos_y + height - 1, pos_x, '╰')
            frame.addstr(pos_y + height - 1, pos_x + width - 1, '╯')

            # Erase any text within the area of the box.
            for j in range(height - 2):
                frame.addstr(pos_y + 1 + j, pos_x + 1, " " * (width - 2))
        frame.refresh()
