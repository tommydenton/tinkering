import os, syslog
import pygame
import time
import datetime
import pywapi
import string

# Weather Icons used with the following permissions:
#
# VClouds Weather Icons
# Created and copyrighted by VClouds - http://vclouds.deviantart.com/
#
# The icons are free to use for Non-Commercial use, but If you use want to use it with your art please credit me and put a link leading back to the icons DA page - http://vclouds.deviantart.com/gallery/#/d2ynulp
#
# *** Not to be used for commercial use without permission!

time.sleep(20)
# Path to the icons
installPath = "/home/pi/personalCodingProjects/IOT/weatherstation/weatherDisplay/icons/"

# location for Fort Worth, TX on weather.com
weatherDotComLocationCode = 'USTX1766'

# convert mph = kpd / kphToMph
kphToMph = 1.60934400061
# convert mBar to InHg
mbarToinHg = 0.02953

# update interval
updateRate = 1200 # seconds

class pitft :
    screen = None;
    colourBlack = (0, 0, 0)

    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)
        os.putenv('SDL_FBDEV', '/dev/fb1')
        # Select frame buffer driver
        # Make sure that SDL_VIDEODRIVER is set
        driver = 'fbcon'
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            exit(0)
        time.sleep(0.5)
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        #self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        #self.screen.fill((0, 0, 0))
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pygame.font.init()
        # Turn the mouse off
        pygame.mouse.set_visible(False)
        # Render the screen
        pygame.display.update()
    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

# Create an instance of the PyScope class
mytft = pitft()

while True:
    # retrieve data from weather.com
    weather_com_result = pywapi.get_weather_from_weather_com(weatherDotComLocationCode, units='imperial' )

    # extract current data for today
    today = weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " \
            + weather_com_result['forecasts'][0]['date'][:4] \
            + weather_com_result['forecasts'][0]['date'][3:]
    windSpeed = int(weather_com_result['current_conditions']['wind']['speed']) #/ kphToMph
    currWind =  "{:.0f} mph ".format(windSpeed) + weather_com_result['current_conditions']['wind']['text']
    currTemp = weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + "F"
    currLike = weather_com_result['current_conditions']['feels_like'] + u'\N{DEGREE SIGN}' + "F"
    currPress = weather_com_result['current_conditions']['barometer']['reading'] + " InHg"
    uv = "UV {}".format(weather_com_result['current_conditions']['uv']['text'])
    humid = "Hum {}%".format(weather_com_result['current_conditions']['humidity'])
    sunrise = weather_com_result['forecasts'][0]['sunrise']
    sunset = weather_com_result['forecasts'][0]['sunset']
    update = weather_com_result['current_conditions']['last_updated'][8:]

    windLabel = "Wind:"
    pressureLabel = "Pressure:"
    uvindexLabel = "UV:"
    humidityLabel = "Humidty:"
    feelsLabel = "Feels Like:"
    riseLabel = "Sunrise:"
    setLabel = "Sunset:"
    luLabel = "LU:"

    # extract forecast data
    forecastDays = {}
    forecaseHighs = {}
    forecaseLows = {}
    forecastPrecips = {}
    forecastWinds = {}

    start = 0
    try:
        test = float(weather_com_result['forecasts'][0]['day']['wind']['speed'])
    except ValueError:
        start = 1

    for i in range(start, 3):

        if not(weather_com_result['forecasts'][i]):
            break
        forecastDays[i] = weather_com_result['forecasts'][i]['day_of_week'][0:3]
        forecaseHighs[i] = weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "F"
        forecaseLows[i] = weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "F"
        forecastPrecips[i] = weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
        forecastWinds[i] = "{:.0f}".format(int(weather_com_result['forecasts'][i]['day']['wind']['speed'])  ) + \
            weather_com_result['forecasts'][i]['day']['wind']['text']

# Set Varaiabled to draw the lines
    xmin = 0
    ymin = 0
    xmax = 320
    ymax = 240
    imgOff = 135
    lines = 5

    # Create come Colour
    colourWhite = (255, 255, 255)
    colourBlack = (0, 0, 0)
    colourRed = (255, 0 ,0)
    colourGreen = (0, 255 ,0)
    colourBlue = (0, 0 ,255)

    # blank the screen
    mytft.screen.fill(colourBlack)

    # Draw Screen Border
    pygame.draw.line( mytft.screen, colourBlue, (xmin,ymin),(xmax,ymin), lines )
    pygame.draw.line( mytft.screen, colourBlue, (xmin,ymin),(xmin,ymax), lines )
    pygame.draw.line( mytft.screen, colourBlue, (xmin,ymax),(xmax,ymax), lines )
    pygame.draw.line( mytft.screen, colourBlue, (xmax,ymin),(xmax,ymax), lines )
    # Draw dividing Lines
    pygame.draw.line( mytft.screen, colourBlue, (xmin+imgOff,ymin),(xmin+imgOff,ymax), lines )
    pygame.draw.line( mytft.screen, colourBlue, (xmin,ymin+imgOff),(xmin+imgOff,ymin+imgOff), lines )
    pygame.draw.line( mytft.screen, colourBlue, (xmin+43,ymin+imgOff),(xmin+43,ymax), lines-2 )
    pygame.draw.line( mytft.screen, colourBlue, (xmin+43+45,ymin+imgOff),(xmin+43+45,ymax), lines-2 )
    pygame.draw.line( mytft.screen, colourBlue, (xmin+imgOff,ymin+90),(xmax,ymin+90), lines-2 )

    # Fonts
    fn = pygame.font.match_font('freesans')
    sfn = pygame.font.match_font('freemono')
    suplargeFont = pygame.font.SysFont( fn, 50)
    largeFont = pygame.font.SysFont( fn, 44)
    medFont = pygame.font.Font(fn, 20)
    smallFont = pygame.font.SysFont( sfn, 18)
    supsmallFont = pygame.font.SysFont( sfn, 13)
    forcastFont = pygame.font.Font(fn, 13)

    # Render the weather logo at 0,0
    icon = installPath+ (weather_com_result['current_conditions']['icon']) + ".png"
    logo = pygame.image.load(icon).convert()
    mytft.screen.blit(logo, (4, 4))

    # set the anchor for the current weather data text
    textAnchorX = 140
    textAnchorY = 5
    textYoffset = 20

    # add current weather data text artifacts to the screen
    text_surface = largeFont.render(today, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    textAnchorY+=textYoffset+20
    text_surface = largeFont.render(currTemp, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+60, textAnchorY))
    textAnchorY+=textYoffset+30
    text_surface = smallFont.render(windLabel, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    text_surface = smallFont.render(currWind, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+70, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = smallFont.render(pressureLabel, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    text_surface = smallFont.render(currPress, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+70, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = smallFont.render(uvindexLabel, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    text_surface = smallFont.render(uv, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+70, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = smallFont.render(humidityLabel, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    text_surface = smallFont.render(humid, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+70, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = smallFont.render(feelsLabel, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    text_surface = smallFont.render(currLike, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+70, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = smallFont.render(riseLabel, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    text_surface = smallFont.render(sunrise, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+70, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = smallFont.render(setLabel, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    text_surface = smallFont.render(sunset, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+70, textAnchorY))

    text_surface = supsmallFont.render(update, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX+130, textAnchorY+10))
    # set X axis text anchor for the forecast text
    textAnchorX = 5
    textXoffset = 45

    # add each days forecast text
    for i in forecastDays:
        textAnchorY = 138
        text_surface = forcastFont.render(forecastDays[int(i)], True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = forcastFont.render(forecaseHighs[int(i)], True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = forcastFont.render(forecaseLows[int(i)], True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = forcastFont.render(forecastPrecips[int(i)], True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = forcastFont.render(forecastWinds[int(i)], True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorX+=textXoffset

    #print update

    # refresh the screen with all the changes
    pygame.display.update()

    # Wait
    time.sleep(updateRate)
