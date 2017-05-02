from papirus import Papirus
from papirus import PapirusText
from papirus import PapirusTextPos
from papirus import PapirusImage
import RPi.GPIO as GPIO
import time
from urllib import urlopen
import json

screen = Papirus()
text = PapirusTextPos()

userMonthGallons= 2250.000
avgMonthGallons=1500.000
lastMonthGallons = 2500.000
userMonthElectricBtu= 3000000.000
avgMonthEletricBtu=2650000.000
lastMonthElectricBtu = 3100000.000
userMonthGasBtu=5000000.000
avgMonthGasBtu=4266666.000
lastMonthGasBtu = 5100000.000
waterScore = 0
electricScore = 0
gasScore = 0

GPIO.setmode(GPIO.BCM)
chan_list = [21, 16,26,20]# add as many channels as you want!#you can tuples instead i.e.: #chan_list = (11, 12)
GPIO.setup(chan_list, GPIO.IN)
currentState = True

#!/usr/bin/env python

import os
import sys
import string
from papirus import Papirus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep
import RPi.GPIO as GPIO

# Check EPD_SIZE is defined
EPD_SIZE=0.0
if os.path.exists('/etc/default/epd-fuse'):
    execfile('/etc/default/epd-fuse')
if EPD_SIZE == 0.0:
    print("Please select your screen size by running 'papirus-config'.")
    sys.exit()

# Running as root only needed for older Raspbians without /dev/gpiomem
if not (os.path.exists('/dev/gpiomem') and os.access('/dev/gpiomem', os.R_OK | os.W_OK)):
    user = os.getuid()
    if user != 0:
        print("Please run script as root")
        sys.exit()

# Command line usage
# papirus-buttons

hatdir = '/proc/device-tree/hat'

WHITE = 1
BLACK = 0
SIZE = 27
SW2 = 26
SW3 = 20
AC = True

def checkAC()
    global AC = True

def main():
    global SIZE
    papirus = Papirus()
    # Use smaller font for smaller dislays
    if papirus.height <= 96:
        SIZE = 18
    papirus.clear()
    write_text(papirus, "Ready... SW1 + SW2 to exit.", SIZE)
    while True:
        if GPIO.input(SW2) == False:
            write_text(papirus, "Two", SIZE)
        if GPIO.input(SW3) == False:
            write_text(papirus, "Three", SIZE)
        sleep(0.1)

def write_text(papirus, text, size):

    # initially set all white background
    image = Image.new('1', papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', size)

    # Calculate the max number of char to fit on line
    line_size = (papirus.width / (size*0.65))

    current_line = 0
    text_lines = [""]

    # Compute each line
    for word in text.split():
        # If there is space on line add the word to it
        if (len(text_lines[current_line]) + len(word)) < line_size:
            text_lines[current_line] += " " + word
        else:
            # No space left on line so move to next one
            text_lines.append("")
            current_line += 1
            text_lines[current_line] += " " + word

    current_line = 0
    for l in text_lines:
        current_line += 1
        draw.text( (0, ((size*current_line)-size)) , l, font=font, fill=BLACK)

    papirus.display(image)
    papirus.partial_update()

if __name__ == '__main__':
    main()

def windowInfoDisplay():
    if math.fabs(tempInside()-tempOutside())<2:
        if AC:
            text.AddText("Your AC is on when it can be turned off" , 10, 10, Id = "Bad")
        else:
            if not door():
                text.AddText("Your window is closed when the temperature inside and ouside are the same. You can open your window" , 10, 10, Id = "Bad")
    else:
        if AC:
            if door():
                text.AddText("Your AC is on when the window is open. Please close the window." , 10, 10, Id = "Bad")

def door():
    # pin is 21
    global currentState
    if (GPIO.input(21) == False and currentState==True):
        text.Clear()
        text.AddText("Window is closed" , 10, 10, Id = "Closed")
        currentState = False
        #we don't do anything
    elif(GPIO.input(21) == True and currentState==False):
        #the door is open if we have reached here,
        #so we should send a value to Adafruit IO.
        text.Clear()
        text.AddText("Window is open" , 10, 10, Id = "Open")
        currentState = True
    time.sleep(.1)

def tempOutside():
    apikey= '06e1dbcfafa9653b'
    url="http://api.wunderground.com/api/"+apikey+"/conditions/q/USA/CA/Claremont.json"
    meteo=urlopen(url).read()
    meteo = meteo.decode('utf-8')
    weather = json.loads(meteo)
    cur_temp =weather['current_observation']['temperature_string'].split()
    tempOut= cur_temp[0]
    text.AddText(tempOut , 10, 10, Id = "Label")
    return (float)(tempOut)

def tempInside():
    reading = GPIO.input(16)
    voltage = reading * 5.0
    voltage /= 1024.0
    temperatureC = (voltage - 0.5) * 100 #converting from 10 mv per degree wit 500 mV offset
    #now convert to Fahrenheit
    temperatureF = (temperatureC * 9.0 / 5.0) + 32.0
    text.AddText((str)(temperatureF) , 10, 10, Id = "Temp")
    text.AddText("degrees F" , 10, 10, Id = "Label")
    return (float)(temperatureF)

def first(userMonthGallons):
    text.AddText("Your monthly water usage is " + str(userMonthGallons) + " gallons", 10, 10, Id = "Start")

def second(userMonthGallons, lastMonthGallons):
    global waterScore
    if userMonthGallons > lastMonthGallons:
        text.AddText("Over last month's water usage by "
        + str(round(abs((lastMonthGallons-userMonthGallons)/lastMonthGallons)*100,2)) + " pecent", 10, 10, Id= "Water2")
        waterScore -= 1
    elif userMonthGallons<lastMonthGallons:
        text.AddText("Under last month's water usage by "
        + str(round(abs((lastMonthGallons-userMonthGallons)/lastMonthGallons)*100,2)) + " percent", 10, 10, Id= "Water2")
        waterScore += 1

def third(userMonthGallons, avgMonthGallons):
    if userMonthGallons > avgMonthGallons:
        text.AddText("Over the average water usage by "
        + str(round(abs((userMonthGallons-avgMonthGallons)/avgMonthGallons)*100,2)) + " percent", 10, 10, Id= "Water3")
        waterScore -= 1
    elif userMonthGallons < avgMonthGallons:
        text.AddText("Under the average water usage by "
        + str(round(abs((userMonthGallons-avgMonthGallons)/avgMonthGallons)*100,2)) + " percent", 10, 10, Id = "Water3")
        waterScore += 1

def fourth(userMonthElectricBtu):
    text.AddText("Your monthly electric usage is " + str(userMonthElectricBtu) + " electric British thermal units", 10, 10, Id = "Start1")

def fifth(userMonthElectricBtu, lastMonthElectricBtu):
    global electricScore
    if userMonthElectricBtu > lastMonthElectricBtu:
        text.AddText("Over last month's electric usage by "
        + str(round(abs((lastMonthElectricBtu-userMonthElectricBtu)/lastMonthElectricBtu)*100,2)) + " pecent", 10, 10, Id= "Electric2")
        electricScore -= 1
    elif userMonthElectricBtu<lastMonthElectricBtu:
        text.AddText("Under last month's electric usage by "
        + str(round(abs((lastMonthElectricBtu-userMonthElectricBtu)/lastMonthElectricBtu)*100,2)) + " percent", 10, 10, Id= "Electric2")
        electricScore += 1

def sixth(userMonthElectricBtu, avgMonthEletricBtu):
    if userMonthElectricBtu > avgMonthEletricBtu:
        text.AddText("Over the average electric usage by "
        + str(round(abs((userMonthElectricBtu-avgMonthEletricBtu)/avgMonthEletricBtu)*100,2)) + " percent", 10, 10, Id= "Electric3")
        electricScore -= 1
    elif userMonthElectricBtu < avgMonthEletricBtu:
        text.AddText("Under the average electric usage by "
        + str(round(abs((userMonthElectricBtu-avgMonthEletricBtu)/avgMonthEletricBtu)*100,2)) + " percent", 10, 10, Id = "Electric3")
        electricScore += 1 

def seventh(userMonthGasBtu):
    text.AddText("Your monthly gas usage is " + str(userMonthGasBtu) + " gas British thermal units", 10, 10, Id = "Start2")

def eighth(userMonthGasBtu, lastMonthGasBtu):
    global gasScore
    if userMonthGasBtu > lastMonthGasBtu:
        text.AddText("Over last month's gas usage by "
        + str(round(abs((lastMonthGasBtu-userMonthGasBtu)/lastMonthGasBtu)*100,2)) + " pecent", 10, 10, Id= "Gas2")
        gasScore -= 1
    elif userMonthGasBtu<lastMonthGasBtu:
        text.AddText("Under last month's gas usage by "
        + str(round(abs((lastMonthGasBtu-userMonthGasBtu)/lastMonthGasBtu)*100,2)) + " percent", 10, 10, Id= "Gas2")
        gasScore += 1

def ninth(userMonthGasBtu, avgMonthGasBtu):
    if userMonthGasBtu > avgMonthGasBtu:
        text.AddText("Over the average gas usageby "
        + str(round(abs((userMonthGasBtu-avgMonthGasBtu)/avgMonthGasBtu)*100,2)) + " percent", 10, 10, Id= "Gas3")
        gasScore -= 1
    elif userMonthGasBtu < avgMonthGasBtu:
        text.AddText("Under the average gas usage by"
        + str(round(abs((userMonthGasBtu-avgMonthGasBtu)/avgMonthGasBtu)*100,2)) + "percent", 10, 10, Id = "Gas3")
        gasScore += 1

def genSuggestions(water, electricity, gas):
    displayBuffer = ""
    if water > 0:
        displayBuffer += "Youre doing great on water, keep it up!" + "\n"
    elif water == 0:
        displayBuffer += "Youre doing ok on water... Consider taking shorter showers, turning off the faucet when brushing, etc." + "\n"
    elif water < 0:
        displayBuffer += "You could use some improvement on water on usage. Make sure to turn off water when youre not using it! Try shorter showers might and reducing time on watering the lawn." + "\n"

    if electricity > 0:
        displayBuffer += "Youre doing great on electricity, keep it up!" + "\n"
    elif electricity == 0:
       displayBuffer += "Youre doing ok on electricity... Consider unplugging chargers when not in use." + "\n"
    elif electricity < 0:
        displayBuffer += "You could use some improvement on electricity usage. Make sure to turn off lights when you dont need them!" + "\n"

    if gas > 0:
        displayBuffer += "Youre doing great on gas, keep it up!" + "\n"
    elif gas == 0:
        displayBuffer += "Youre doing ok on gas... Consider using colder water in showers and to wash dishes." + "\n"
    elif gas < 0:
        displayBuffer += "You could use some improvement on gas usage. Make sure to turn off the stove when youre done cooking! Use colder water in showers and to wash dishes/clothes." + "\n"

    text.AddText(displayBuffer)

def getWords(text):
    counter = 0
    array = []
    for word in text.split(" "):
        for other in word.split("\n"):
            array.append(other)
    return array

def wordsIntoLines(stuff):
    words = getWords(stuff)
    lines = []
    lineBuffer = ""
    for word in words:
        if word == "\n":
            lines.append(lineBuffer)
            lineBuffer = ""
        elif len(lineBuffer) + len(word) <= 20:
            lineBuffer += word + " "
        else:
            lines.append(lineBuffer)
            lineBuffer = word + " "
    lines.append(lineBuffer)
    return lines

def wrap(text):
    pages = []
    lines = wordsIntoLines(text)
    pageBuffer = []
    for i in range(len(lines)):
        pageBuffer.append(lines[i])
        if i % 10 == 9:
            pages.append("\n".join(pageBuffer))
            pageBuffer = []
    pages.append("\n".join(pageBuffer))
    return pages