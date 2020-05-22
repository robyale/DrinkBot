import board
import digitalio
import adafruit_ssd1306
import RPi.GPIO as GPIO
import time
import threading
import sys

from menu import *
from drinks import drinkList, ingredients
from pumps import pumps
from debounce import ButtonHandler
from display import Display

# Display Dimensions
WIDTH = 128
HEIGHT = 64
BORDER = 5
ROWS = 5

# Button Pins
LEFT_BTN_PIN = 23
RIGHT_BTN_PIN = 24
SELECT_BTN_PIN = 18
BOUNCE = 10

# OLED Screen Pins
RESET_PIN = board.D4
CS_PIN = board.D5
DC_PIN = board.D6

# LED Constants
RED_PIN = 17
GREEN_PIN = 22
BLUE_PIN = 27
FADE_SLEEP = 0.01

# Pump Flow Rate
FLOW_RATE = 60.0/100.0


class Bartender(MenuDelegate):
    def __init__(self):
        self.running = False

        # Set the oled screen height
        self.screen_width = WIDTH
        self.screen_height = HEIGHT

        # Set up buttons
        self.btn1Pin = LEFT_BTN_PIN
        self.btn2Pin = RIGHT_BTN_PIN
        self.btn3Pin = SELECT_BTN_PIN

        # Configure interrups for buttons
        GPIO.setup(self.btn1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.btn2Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.btn3Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Configure Screen
        spi = board.SPI()
        oled_reset = digitalio.DigitalInOut(RESET_PIN)
        oled_cs = digitalio.DigitalInOut(CS_PIN)
        oled_dc = digitalio.DigitalInOut(DC_PIN)
        self.oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset, oled_cs)

        # load the pump configuration
        self.pumps = pumps
        for pump in self.pumps:
            GPIO.setup(pump["pin"], GPIO.OUT, initial=GPIO.HIGH)
        
        # Configure LED Pins
        GPIO.setup(RED_PIN, GPIO.OUT)
        GPIO.setup(GREEN_PIN, GPIO.OUT)
        GPIO.setup(BLUE_PIN, GPIO.OUT)
        
        # set RGB for lights
        self.red = GPIO.PWM(RED_PIN, 50)
        self.green = GPIO.PWM(GREEN_PIN, 50)
        self.blue = GPIO.PWM(BLUE_PIN, 50)
        
        # start LEDs
        self.red.start(0)
        self.green.start(0)
        self.blue.start(0)

    # Create up button interrupts with debounce
    def startInterrupts(self):
        self.cb_left = ButtonHandler(self.btn1Pin, self.left_btn, edge='rising', bouncetime=BOUNCE)
        self.cb_left.start()
        GPIO.add_event_detect(self.btn1Pin, GPIO.FALLING, callback=self.cb_left)
        
        self.cb_right = ButtonHandler(self.btn2Pin, self.right_btn, edge='rising', bouncetime=BOUNCE)
        self.cb_right.start()
        GPIO.add_event_detect(self.btn2Pin, GPIO.FALLING, callback=self.cb_right)
        
        self.cb_select = ButtonHandler(self.btn3Pin, self.select_btn, edge='rising', bouncetime=BOUNCE)
        self.cb_select.start()
        GPIO.add_event_detect(self.btn3Pin, GPIO.FALLING, callback=self.cb_select)

    # Stop button interrupts
    def stopInterrupts(self):
        GPIO.remove_event_detect(self.btn1Pin)
        GPIO.remove_event_detect(self.btn2Pin)
        GPIO.remove_event_detect(self.btn3Pin)

    # Initialize the menus
    def initializeMenu(self, drinkList, ingredients):
        # Set up main menu
        myMenu = Menu("Main Menu")
        drinkMenu = Menu("Drink Menu")
        shotMenu = Menu("Shot Menu")

        # Make main menu the parent of sub menus
        drinkMenu.setParent(myMenu)
        shotMenu.setParent(myMenu)

        # Add back buttons
        drinkMenu.addChild(Back("Back"))
        shotMenu.addChild(Back("Back"))

        # Add drinks to drink menu
        for i in drinkList:
            drinkMenu.addChild(MenuItem("drink", i["name"], {"ingredients": i["ingredients"]}))

        # Add shots to shot menu
        for i in ingredients:
            shotMenu.addChild(MenuItem("shot", i["name"], {"ingredients": i["ingredients"]}))

        # Add sub menus
        myMenu.addChild(drinkMenu)
        myMenu.addChild(shotMenu)    
        myMenu.addChild(MenuItem('clean', 'Clean'))

        # Add a menu context for navigation
        self.menuContext = MenuContext(myMenu, self)
        self.filterDrinks(myMenu)

    # Filter available drinks
    def filterDrinks(self, menu):
        for i in menu.children:
            if(i.type == "drink"):
                i.visible = False
                ingredients = i.attributes["ingredients"]
                presentIng = 0
                for ing in ingredients.keys():
                    for p in self.pumps:
                        if (ing == p["value"]):
                            presentIng += 1
                if (presentIng == len(ingredients.keys())): 
                    i.visible = True
            elif (i.type == "menu"):
                self.filterDrinks(i)
                
    # Called when a menu is clicked, routes to appropriate action
    def menuItemClicked(self, menuItem):
        if (menuItem.type == "drink" or menuItem.type == "shot"):
            self.makeDrink(menuItem.name, menuItem.attributes["ingredients"])
            return True
        elif(menuItem.type == "clean"):
            self.clean()
            return True
        return False
    
    # Cleans the tubing
    def clean(self):
        waitTime = 20
        pumpThreads = []

        # cancel any button presses while the drink is being made
        # self.stopInterrupts()
        self.running = True

        # define pump threads
        for pump in self.pumps:
            pump_t = threading.Thread(target=self.pour, args=(pump["pin"], waitTime))
            pumpThreads.append(pump_t)

        # start the pump threads
        for thread in pumpThreads:
            thread.start()

        # start the progress bar
        self.progressBar(waitTime)

        # wait for threads to finish
        for thread in pumpThreads:
            thread.join()

	    # show the main menu
        self.displayMenuItem(self.menuContext.currentMenu)

	    # sleep for a couple seconds to make sure the interrupts don't get triggered
        time.sleep(2)

	    # reenable interrupts
	    # self.startInterrupts()
        self.running = False

    # Display a menu item
    def displayMenuItem(self, menu):
        dsp = Display(self.oled, WIDTH, HEIGHT, ROWS, menu)
        dsp.drawMenu()

    # Make lights glow
    def cycleLights(self):
        # Fade from nothing up to full red
        for i in range(100):
            self.red.ChangeDutyCycle(i)
            time.sleep(FADE_SLEEP)
            
    
        # Now fade from violet (red + blue) down to red
        for i in range(100, -1, -1):
            self.blue.ChangeDutyCycle(i)
            time.sleep(FADE_SLEEP)
        
        # Fade from red to yellow (red + green)
        for i in range(100):
            self.green.ChangeDutyCycle(i)
            time.sleep(FADE_SLEEP)
        
        # Fade from yellow to green
        for i in range(100, -1, -1):
            self.red.ChangeDutyCycle(i)
            time.sleep(FADE_SLEEP)
        
        # Fade from green to teal (blue + green)
        for i in range(100):
            self.blue.ChangeDutyCycle(i)
            time.sleep(FADE_SLEEP)
        
        # Fade from teal to blue
        for i in range(100, -1, -1):
            self.green.ChangeDutyCycle(i)
            time.sleep(FADE_SLEEP)

# Currently a bug prevents cycleLights from stopping
# during an interrupt, causes issues with progress bar
# **TODO**
#     def lightsProgressBar(self, waitTime):
#         # make lights red
#         self.red.ChangeDutyCycle(100)
#         self.green.ChangeDutyCycle(0)
#         self.blue.ChangeDutyCycle(0)
# 
#         fade = waitTime / 200.0
# 
#         # fade to yellow
#         for i in range(100):
#             self.green.ChangeDutyCycle(i)
#             time.sleep(fade)
# 
#         # fade to green
#         for i in range(100, -1, -1):
#             self.red.ChangeDutyCycle(i)
#             time.sleep(fade)

    # Activates pump for specified amount of time
    def pour(self, pin, waitTime):
        GPIO.output(pin, GPIO.LOW)
        time.sleep(waitTime)
        GPIO.output(pin, GPIO.HIGH)

    # Display a progress bar
    def progressBar(self, waitTime):
        dsp = Display(self.oled, WIDTH, HEIGHT, ROWS)
        dsp.progressBar(waitTime)

    # Make the specified drink
    def makeDrink(self, drink, ingredients):
        self.running = True

        # Parse the drink ingredients and spawn threads for pumps
        maxTime = 0
        pumpThreads = []
        for ing in ingredients.keys():
            for pump in self.pumps:
                if ing == pump["value"]:
                    waitTime = ingredients[ing] * FLOW_RATE
                    if (waitTime > maxTime):
                        maxTime = waitTime
                    pump_t = threading.Thread(target=self.pour, args=(pump["pin"], waitTime))
                    pumpThreads.append(pump_t)

        # start the pump threads
        for thread in pumpThreads:
            thread.start()

        # launch a thread to control lighting
        #lightsThread = threading.Thread(target=self.lightsProgressBar, args=(maxTime,))
        #lightsThread.start()

        # start the progress bar
        self.progressBar(maxTime)

        # wait for threads to finish
        for thread in pumpThreads:
            thread.join()

        # show the main menu
        #self.menuContext.showMenu()
        self.displayMenuItem(self.menuContext.currentMenu)

        # stop the light thread
        #lightsThread.do_run = False
        #lightsThread.join()

        # sleep for a couple seconds to make sure the interrupts don't get triggered
        time.sleep(2)
        
        self.running = False

    # Go to previous menu item
    def left_btn(self, ctx):
        if not self.running:
            self.menuContext.currentMenu.before()
            self.menuContext.showMenu()

    # Go to next menu item
    def right_btn(self, ctx):
        if not self.running:
            self.menuContext.currentMenu.next()
            self.displayMenuItem(self.menuContext.currentMenu)

    # Select menu item
    def select_btn(self, ctx):
        print("button press")
        if not self.running:
            self.menuContext.select()

    # Main loop, runs constantly
    def run(self):
        self.startInterrupts()
        # main loop
        try:  
            while True:
                self.cycleLights()
        except KeyboardInterrupt:  
            GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
        GPIO.cleanup()           # clean up GPIO on normal exit 

		#traceback.print_exc()
    
# Start program
bartender = Bartender()
bartender.initializeMenu(drinkList, ingredients)
bartender.run()