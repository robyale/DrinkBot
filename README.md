# DrinkBot
## Installation and Use
To install the required dependencies, use the following command
```
pip install -r requirements.txt
```

This project is based off of the [hackster.io smart bartender](https://github.com/HackerShackOfficial/Smart-Bartender#readme), so this will follow much of the same guidelines as their machine.

## Raspberry Pi
You must install the following on your Raspberry Pi:
- [Python 3.x](https://www.python.org/downloads/)
- [pip](https://www.raspberrypi.org/documentation/linux/software/python.md)

## Enable SPI and I2C
Our OLED screen will be using SPI. To enable, type the following into the terminal.
```
raspi-config
```
Navigate to interfacing options, and select SPI.
To enable I2C, type the following in the terminal.
```
sudo vim /etc/modules
```
Then press i, and paste the following into the file.
```
i2c-bcm2708
i2c-dev
```
press esc then zz to exit

## OLED Display
The methods the hackershack team used for the display have since depreciated. Adafruit put together a [great tutorial](https://learn.adafruit.com/monochrome-oled-breakouts/overview) on making the OLED work. You simply need to run the command 
```
pip install adafruit_ssd1306
```
and the display should work.

## Run at Startup
To enable running at startup, simply use the pwd command in the repository to get the path to your repository. Copy this, and then type 
```
sudo vim /etc/rc.local
```
Press i to edit, and then add the following lines right before the last line:
```
cd your/path/here
sudo python main.py
```

## Background
When I first saw the HackerShack team build this, I thought it would be a fun side project to get out of my comfort zone of C++ and Arduino and get more familiar with python and Raspberry Pi. What I thought was a fun side project turned into an overhaul of the original design. Multiple depenencies had depreciated and ended up not working, so I had to to redesign the code to get everything working. See changes below for a full list of changes.
## This Project
My goal for this project is to 1) learn the basics of circuitPython for microcontrollers, 2) learn the basics of using a Raspberry PI, and 3) grow my skills in using Fusion 360 CAD software. Simply write the drinks you want in the drinks.py file, add the ingedients to the pump configuration file pumps.py, and fire up your Raspberry Pi running main.py to get drinks automatically made for you at the press of a button! Some installation required.
## Changes
### Hardware
- Added a third button to support previous, next, and select
- Expanded pumps from 6 pumps to 12 pumps for added drink options
- Moved electronics from the bottom to the top of the DrinkBot to prevent liquid leaking onto electronics
- Moved display to top for easier viewing
- Added a larger display
- Pumps moved to the inside of the DrinkBot for a sleek look
- Changed the lights from digital to analog
- Made the DrinkBot taller to support tumblers
### Software
- Added a display module to handle displaying menu items
- Display now shows multiple items per page
- Added a button debounce module to prevent multiple button clicks
- Removed json in favor of nested python dictionaries
- Added software to control analog lights
- Added shot menu for shots of ingredients
- Refactored menu module
- Designed new DrinkBot in Fusion 360
## Picture of Model
![Model of the DrinkBot](/DrinkBotModel.JPG)
## Future Versions and Considerations
While it was nice to shake things up and use different software/hardware combinations, Arduino would have made this project much simpler. Ardiuno has much more libraries to support the devices I used, and it is easier to set up the GPIO pins. If I were to redo this, I would have used a Raspberry Pi zero, or fully converted over to Aruidno. The Raspberry Pi is simply more powerful than what is needed by this project. Also, the peristoltic pumps I used were too slow; it took almost 20 seconds to make a drink. I didn't need the precision given by the pumps, and I would instead opt for a faster, less accurate pump. A friend of mine used aquatic pumps for a project of his, and he didn't notice much of a drop in accuracy. I would opt to use those pumps for faster drink making. Lastly, I heavily considered making this a wifi enabled DrinkBot. However, someone would have to make sure there is a glass inside the machine, and then have to go get the drink after it has been made. The wifi wouldn't add any value to the DrinkBot; it would have been a complete gimmick
