from PIL import Image, ImageDraw
from typing import Optional

import os


def _default_screenshot(self, map_path: str) -> Optional[str]:
    try:
        cell_size = 30
        padding = 20
        img_width = self.width * cell_size + padding * 2
        img_height = self.height * cell_size + padding * 2
        img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        for y in range(self.height):
            for x in range(self.width):
                rect_left = padding + x * cell_size
                rect_top = padding + (self.height - 1 - y) * cell_size
                rect_right = rect_left + cell_size
                rect_bottom = rect_top + cell_size

                cell_value = self.grid[y][x]
                if cell_value == self.OBSTACLE:
                    draw.rectangle(
                        [rect_left, rect_top, rect_right, rect_bottom], fill=(0, 0, 0)
                    )
                elif cell_value == self.START:
                    draw.rectangle(
                        [rect_left, rect_top, rect_right, rect_bottom], fill=(0, 255, 0)
                    )
                elif cell_value == self.GOAL:
                    draw.rectangle(
                        [rect_left, rect_top, rect_right, rect_bottom], fill=(255, 0, 0)
                    )
                else:
                    draw.rectangle(
                        [rect_left, rect_top, rect_right, rect_bottom],
                        fill=(255, 255, 255),
                    )

                draw.rectangle(
                    [rect_left, rect_top, rect_right, rect_bottom],
                    outline=(200, 200, 200),
                    width=1,
                )

        image_path = os.path.join(map_path, "preview.png")
        img.save(image_path)
        return image_path
    except Exception as e:
        print("[UNCATEGORIZED]: Error creating screenshot:", e)
        return None
