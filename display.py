from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import itertools
import math
import time

# Class to handle displaying menus
class Display(object):
    def __init__(self, oled, width, height, rows = 5, menu = None):
        self.oled = oled
        self.width = width
        self.height = height
        self.rows = rows
        self.menu = menu
        
        self.image = Image.new("1", (width, height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

        oled.fill(0)
        oled.show
        
    # Get indices of menu items that can be displayed
    def getVisible(self):
        indices = []
        index = 0
        for item in self.menu.children:
            if(item.visible == True):
                indices.append(index)
            index += 1
        return indices
        
    # Get indices of menu items to display
    def getIndex(self):
        start = 0
        rows = self.rows
        indices = self.getVisible()
        end = len(indices)
        
        # If there has to be more than 1 page
        if(end > rows):
            # Get the current page, and max amount of pages
            curPage = 0
            curPage = math.floor(self.menu.selected / rows) + 1
            maxPage = math.ceil(end / rows)
            strPage = str(curPage) + "/" + str(maxPage)

            # Draw page location in corner
            self.draw.text((self.width-20, 5), strPage, font=self.font, fill=255)

            # Get starting index
            start = (curPage - 1) * rows

            # Determine end index
            if(curPage != maxPage):
                end = curPage * rows
            else:
                end = start + (end % rows)
        
        return list(itertools.islice(indices, start, end))
        
    # Draw the menu
    def drawMenu(self):        
        indices = self.getIndex()
        position = 0
        for i in indices:
            # Get the text to be displayed
            text = self.menu.children[i].name
            # Get dimensions of font
            (font_width, font_height) = self.font.getsize(text)
            # Draw the text
            self.draw.text((5, font_height * position), text, font=self.font, fill=255)
            # If selected, append *
            if(i == self.menu.selected):
                self.draw.text((font_width + 10, font_height * position + 2), "*", font=self.font, fill=255)
            position += 1
        
        # Draw menu
        self.oled.image(self.image)
        self.oled.show()
        
    # Draw the progress bar
    def progressBar(self, waitTime):
        interval = waitTime / 10.0
        for i in range(1, 11):
            self.draw.rectangle((0, 0, i * 10, self.oled.height - 30), outline=255, fill=255)
            self.oled.image(self.image)
            self.oled.show()
            time.sleep(interval)