import sys
import random
import time
import datetime
import pygame

pygame.init()

#Screen
size = width, height = 340, 240 #Make sure background image is same size
screen = pygame.display.set_mode(size)

done = False

#Time Info
Time = 0
Minute = 0
Hour = 0
Day = 0
counter=0

#Colour
Black = (0,0,0)
White = (255, 255, 255)

#Fonts
Font = pygame.font.SysFont("Trebuchet MS", 25)

#Day
DayFont = Font.render("Day:{0:03}".format(Day),1, Black) #zero-pad day to 3 digits
DayFontR=DayFont.get_rect()
DayFontR.center=(985,20)
#Hour
HourFont = Font.render("Hour:{0:02}".format(Hour),1, Black) #zero-pad hours to 2 digits
HourFontR=HourFont.get_rect()
HourFontR.center=(1085,20)
#Minute
MinuteFont = Font.render("Minute:{0:02}".format(Minute),1, Black) #zero-pad minutes to 2 digits
MinuteFontR=MinuteFont.get_rect()
MinuteFontR.center=(1200,20)

Clock = pygame.time.Clock()
CLOCKTICK = pygame.USEREVENT+1
pygame.time.set_timer(CLOCKTICK, 1000) # fired once every second

screen.fill(White)
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == CLOCKTICK: # count up the clock
            #Timer
            Minute=Minute+1
            if Minute == 60:
                Hour=Hour+1
                Minute=0
            if Hour==12:
                Day=Day+1
                Hour=0
            # redraw time
            screen.fill(White)
            MinuteFont = Font.render("Minute:{0:02}".format(Minute),1, Black)
            screen.blit(MinuteFont, MinuteFontR)
            HourFont = Font.render("Hour:{0:02}".format(Hour),1, Black)
            screen.blit(HourFont, HourFontR)
            DayFont = Font.render("Day:{0:03}".format(Day),1, Black)
            screen.blit(DayFont, DayFontR)

            pygame.display.flip()

    Clock.tick(60) # ensures a maximum of 60 frames per second
print Minute
pygame.quit()
