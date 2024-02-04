#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This was built heavily upon the work here:
# https://github.com/denilsonsa/pygame-joystick-test

from __future__ import division
from __future__ import print_function

import os

# I see no reason to disable screensaver for this tool.
os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"

# Maybe people want to keep watching the joystick feedback even when this
# window doesn't have focus. Possibly by capturing this window into OBS.
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

# A tiny performance/latency hit isn't a problem here. Instead, it's more
# important to keep the desktop compositing effects running fine. Disabling
# compositing is known to cause issues on KDE/KWin/Plasma/X11 on Linux.
os.environ["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"


import sys
import pygame
from pygame.locals import *

import camera_manager

cams = camera_manager.Cameras()
cams.add("Camera 1","192.168.1.30")
cams.add("Camera 2","192.168.1.31")
cams.add("Camera 3","192.168.1.32")
cams.add("Camera 4","192.168.1.34")
cams.add("Camera 5","192.168.1.35")
cams.start("Camera 5")

axisNames = ["Pan","Tilt","Zoom","Choir"]

class joystick_handler(object):
    def __init__(self, id):
        self.id = id
        self.joy = pygame.joystick.Joystick(id)
        self.name = self.joy.get_name()
        self.joy.init()
        self.numaxes    = self.joy.get_numaxes()
        self.numballs   = self.joy.get_numballs()
        self.numbuttons = self.joy.get_numbuttons()
        self.numhats    = self.joy.get_numhats()

        self.axis = []
        for i in range(self.numaxes):
            self.axis.append(self.joy.get_axis(i))

        self.ball = []
        for i in range(self.numballs):
            self.ball.append(self.joy.get_ball(i))

        self.button = []
        for i in range(self.numbuttons):
            self.button.append(self.joy.get_button(i))

        self.hat = []
        for i in range(self.numhats):
            self.hat.append(self.joy.get_hat(i))

class input_test(object):
    class program:
        "Program metadata"
        name    = "Pygame Joystick Test"
        version = "0.2"
        author  = "Denilson Figueiredo de Sá Maia"
        nameversion = name + " " + version

    class default:
        "Program constants"
        fontnames = [
            # Bold, Italic, Font name
            (0, 0, "Bitstream Vera Sans Mono"),
            (0, 0, "DejaVu Sans Mono"),
            (0, 0, "Inconsolata"),
            (0, 0, "LucidaTypewriter"),
            (0, 0, "Lucida Typewriter"),
            (0, 0, "Terminus"),
            (0, 0, "Luxi Mono"),
            (1, 0, "Monospace"),
            (1, 0, "Courier New"),
            (1, 0, "Courier"),
        ]
        # TODO: Add a command-line parameter to change the size.
        # TODO: Maybe make this program flexible, let the window height define
        #       the actual font/circle size.
        fontsize     = 40
        circleheight = 10
        resolution   = (640, 480)

    def load_the_main_font(self):
        # The only reason for this function is that pygame can find a font
        # but gets an IOError when trying to load it... So I must manually
        # workaround that.

        # self.font = pygame.font.SysFont(self.default.fontnames, self.default.fontsize)
        for bold, italic, f in self.default.fontnames:
            try:
                filename = pygame.font.match_font(f, bold, italic)
                if filename:
                    self.font = pygame.font.Font(filename, self.default.fontsize)
                    # print("Successfully loaded font: %s (%s)" % (f, filename))
                    break
            except IOError as e:
                # print("Could not load font: %s (%s)" % (f, filename))
                pass
        else:
            self.font = pygame.font.Font(None, self.default.fontsize)
            # print("Loaded the default fallback font: %s" % pygame.font.get_default_font())
    def load_the_alt_font(self):
        # The only reason for this function is that pygame can find a font
        # but gets an IOError when trying to load it... So I must manually
        # workaround that.

        # self.font = pygame.font.SysFont(self.default.fontnames, self.default.fontsize)
        for bold, italic, f in self.default.fontnames:
            try:
                filename = pygame.font.match_font(f, bold, italic)
                if filename:
                    self.altfont = pygame.font.Font(filename, 20)
                    # print("Successfully loaded font: %s (%s)" % (f, filename))
                    break
            except IOError as e:
                # print("Could not load font: %s (%s)" % (f, filename))
                pass
        else:
            self.altfont = pygame.font.Font(None, self.default.fontsize)
            # print("Loaded the default fallback font: %s" % pygame.font.get_default_font())

    def pre_render_circle_image(self):
        size = self.default.circleheight
        self.circle = pygame.surface.Surface((size,size))
        self.circle.fill(Color("magenta"))
        basecolor  = ( 63,  63,  63, 255)  # RGBA
        lightcolor = (255, 255, 255, 255)
        for i in range(size // 2, -1, -1):
            color = (
                lightcolor[0] + i * (basecolor[0] - lightcolor[0]) // (size // 2),
                lightcolor[1] + i * (basecolor[1] - lightcolor[1]) // (size // 2),
                lightcolor[2] + i * (basecolor[2] - lightcolor[2]) // (size // 2),
                255
            )
            pygame.draw.circle(
                self.circle,
                color,
                (int(size // 4 + i // 2) + 1, int(size // 4 + i // 2) + 1),
                i,
                0
            )
        self.circle.set_colorkey(Color("magenta"), RLEACCEL)

    def init(self):
        pygame.init()
        pygame.event.set_blocked((MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN))
        # I'm assuming Font module has been loaded correctly
        self.load_the_main_font()
        self.load_the_alt_font()
        # self.fontheight = self.font.get_height()
        self.fontheight = self.font.get_linesize()
        self.background = Color("black")
        self.statictext = Color("#FFFFA0")
        self.dynamictext = Color("white")
        self.alerttext = Color("#FF1100")
        self.antialias = 1
        self.pre_render_circle_image()
        # self.clock = pygame.time.Clock()
        self.joycount = pygame.joystick.get_count()
        if self.joycount == 0:
            print("This program only works with at least one joystick plugged in. No joysticks were detected.")
            self.quit(1)
        self.joy = []
        for i in range(self.joycount):
            self.joy.append(joystick_handler(i))

        # Find out the best window size
        rec_height = max(
            5 + joy.numaxes + joy.numballs + joy.numhats + (joy.numbuttons + 9) // 10
            for joy in self.joy
        ) * self.fontheight
        rec_width = max(
            [self.font.size("W" * 13)[0]] +
            [self.font.size(joy.name)[0] for joy in self.joy]
        ) * self.joycount
        self.resolution = (400, rec_height)

    def run(self):
        self.screen = pygame.display.set_mode(self.resolution, RESIZABLE)
        pygame.display.set_caption(self.program.nameversion)
        self.circle.convert()

        while True:
            for i in range(self.joycount):
                self.draw_joy(i)
            pygame.display.flip()
            # self.clock.tick(30)
            for event in [pygame.event.wait(), ] + pygame.event.get():
                # QUIT             none
                # ACTIVEEVENT      gain, state
                # KEYDOWN          unicode, key, mod
                # KEYUP            key, mod
                # MOUSEMOTION      pos, rel, buttons
                # MOUSEBUTTONUP    pos, button
                # MOUSEBUTTONDOWN  pos, button
                # JOYAXISMOTION    joy, axis, value
                # JOYBALLMOTION    joy, ball, rel
                # JOYHATMOTION     joy, hat, value
                # JOYBUTTONUP      joy, button
                # JOYBUTTONDOWN    joy, button
                # VIDEORESIZE      size, w, h
                # VIDEOEXPOSE      none
                # USEREVENT        code
                if event.type == QUIT:
                    self.quit()
                elif event.type == KEYDOWN and event.key in [K_ESCAPE, K_q]:
                    self.quit()
                elif event.type == VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, RESIZABLE)
                elif event.type == JOYAXISMOTION:
                    self.joy[event.joy].axis[event.axis] = event.value
                    #axis 0 and 1 are pan and tilt
                    #axis 3 is zoom
                    #axis 2 is not visca, reserve for controlling mixer slider
                    #throw out a wide dead zone
                    if event.value > .3 or event.value < -.3:
                        if event.axis == 0:
                            cams.ptz_pan(event.value)
                        if event.axis == 1:
                            cams.ptz_tilt(event.value)
                        if event.axis == 3:
                            cams.ptz_zoom(event.value)
                    else:
                        if event.value < .3 and event.value > -.3:
                            #zero out any movement
                            if event.axis == 0:
                                cams.ptz_pan(0)
                            if event.axis == 1:
                                cams.ptz_tilt(0)
                            if event.axis == 3:
                                cams.ptz_zoom(0)
                elif event.type == JOYBALLMOTION:
                    self.joy[event.joy].ball[event.ball] = event.rel
                elif event.type == JOYHATMOTION:
                    self.joy[event.joy].hat[event.hat] = event.value
                    print(event.value)
                    if event.value[0] == 1:
                        cams.nextModeOption()
                    if event.value[0] == -1:
                        cams.prevModeOption()
                    if event.value[1] == -1:
                        cams.nextCamera()
                    if event.value[1] == 1:
                        cams.prevCamera()
                elif event.type == JOYBUTTONUP:
                    self.joy[event.joy].button[event.button] = 0
                elif event.type == JOYBUTTONDOWN:
                    self.joy[event.joy].button[event.button] = 1
                    if event.button == 0:
                        cams.pt_forcestop()
                    if event.button == 4:
                        if cams.controlmode == 0:
                            print("fire preset %s" % cams.currentPreset)
                            cams.visca.recall_preset(cams.currentPreset)
                        if cams.controlmode == 1:
                            print("execute %s" % cams.modes["Iris"][cams.iriscursor])
                        if cams.controlmode == 2:
                            print("execute %s" % cams.modes["Focus"][cams.focuscursor])
                        if cams.controlmode == 3:
                            print("execute %s" % cams.modes["Speed"][cams.speedcursor])
                    if event.button == 5:
                        print("save preset %s" % cams.currentPreset)
                        cams.visca.save_preset(cams.currentPreset)
                    if event.button == 1:
                        if cams.controlmode != 0:
                            cams.controlmode = 0
                        else:
                            cams.controlmode = 3
                    if event.button == 2:
                        cams.controlmode = 1
                    if event.button == 3:
                        cams.controlmode = 2

    def rendertextline(self, text, pos, color, linenumber=0):
        self.screen.blit(
            self.font.render(text, self.antialias, color, self.background),
            (pos[0], pos[1] + linenumber * self.fontheight)
            # I can access top-left coordinates of a Rect by indexes 0 and 1
        )

    def draw_slider(self, value, pos):
        width  = pos[2]
        height = self.default.circleheight
        left   = pos[0]
        top    = pos[1] + (pos[3] - height) // 2
        self.screen.fill(
            (127, 127, 127, 255),
            (left + height // 2, top + height // 2 - 2, width - height, 2)
        )
        self.screen.fill(
            (191, 191, 191, 255),
            (left + height // 2, top + height // 2, width - height, 2)
        )
        self.screen.fill(
            (127, 127, 127, 255),
            (left + height // 2, top + height // 2 - 2, 1, 2)
        )
        self.screen.fill(
            (191, 191, 191, 255),
            (left + height // 2 + width - height - 1, top + height // 2 - 2, 1, 2)
        )
        self.screen.blit(
            self.circle,
            (left + (width - height) * (value + 1) // 2, top)
        )

    def draw_hat(self, value, pos, invert):
        xvalue =  value[0] + 1
        yvalue = -value[1] + 1
        if invert:
            yvalue = value[1] + 1
        width  = min(pos[2], pos[3])
        height = min(pos[2], pos[3])
        left   = pos[0] + (pos[2] - width ) // 2
        top    = pos[1] + (pos[3] - height) // 2
        self.screen.fill((127, 127, 127, 255), (left, top              , width, 1))
        self.screen.fill((127, 127, 127, 255), (left, top + height // 2, width, 1))
        self.screen.fill((127, 127, 127, 255), (left, top + height  - 1, width, 1))
        self.screen.fill((127, 127, 127, 255), (left             , top, 1, height))
        self.screen.fill((127, 127, 127, 255), (left + width // 2, top, 1, height))
        self.screen.fill((127, 127, 127, 255), (left + width  - 1, top, 1, height))
        offx = xvalue * (width  - self.circle.get_width() ) // 2
        offy = yvalue * (height - self.circle.get_height()) // 2
        # self.screen.fill((255,255,255,255),(left + offx, top + offy) + self.circle.get_size())
        self.screen.blit(self.circle, (left + offx, top + offy))

    def draw_preset(self, value, pos, selected):
        width  = min(pos[2], pos[3])
        height = min(pos[2], pos[3])
        left   = pos[0] + (pos[2] - width ) // 2
        top    = pos[1] + (pos[3] - height) // 2
        self.screen.fill((127, 127, 127, 255), (left, top              , width, 1))
        self.screen.fill((127, 127, 127, 255), (left, top + height  - 1, width, 1))
        self.screen.fill((127, 127, 127, 255), (left             , top, 1, height))
        self.screen.fill((127, 127, 127, 255), (left + width  - 1, top, 1, height))
        bg = self.background
        if selected:
            bg = Color("#808080")
        self.screen.blit(self.altfont.render(str(value), self.antialias, "white", bg),(left + 10,top + 2))

    def draw_joy(self, joyid):
        joy = self.joy[joyid]
        width = self.screen.get_width() // self.joycount
        height = self.screen.get_height()
        pos = Rect(width * joyid, 0, width, height)
        self.screen.fill(self.background, pos)

        # This is the number of lines required for printing info about this joystick.
        # self.numlines = 5 + joy.numaxes + joy.numballs + joy.numhats + (joy.numbuttons+9)//10

        # Joy name
        # 0 Axes:
        # -0.123456789
        # 0 Trackballs:
        # -0.123,-0.123
        # 0 Hats:
        # -1,-1
        # 00 Buttons:
        # 0123456789

        # Note: the first character is the color of the text.
        text_colors = {
            "D": self.dynamictext,
            "S": self.statictext,
            "A": self.alerttext,
        }
        output_strings = [
            "S%s"             % "  ~~VISCA PTZ~~",
            "S%s" % "  ~~Commander~~"]
        for i,v in enumerate(cams.cameras):
            if i == cams.current:
                output_strings.append("A>%s<" % v.name)
            else:
                output_strings.append("D %s" % v.name)

        """
        output_strings = output_strings + [ "D    %d=% .3f"   % (i, v) for i, v in enumerate(joy.axis) ]+[
            "S%d hats:"       % joy.numhats
        ]+[ "D  %d=% d,% d"   % (i, v[0], v[1]) for i, v in enumerate(joy.hat ) ]+[
            "S%d buttons:"    % joy.numbuttons
        ]"""
        """
        s = ""
        if cams.current != None:
            s = cams.cameras[cams.current].name
        output_strings.append("D" + "".join(s))
        
        self.screen.blit(
            self.font.render("Btn 2: Call Preset", self.antialias, Color("#808080"), self.background),
            (pos[0], pos[1] + 9 * self.fontheight)
        )
        """
        for i, line in enumerate(output_strings):
            color = text_colors[line[0]]
            self.rendertextline(line[1:], pos, color, linenumber=i)
        
        tmpwidth = self.font.size("    ")[0]
        self.draw_hat((joy.axis[0],joy.axis[1]),
                      (
                    pos[0] + 225,
                    pos[1] + (2 + cams.current) * self.fontheight,
                    tmpwidth,
                    self.fontheight
                ),True
            )
        self.draw_slider(
            joy.axis[3],
            (
                    pos[0] + 300,
                    pos[1] + (2 + cams.current) * self.fontheight,
                    tmpwidth,
                    self.fontheight
            )
        )
        """
        for i, v in enumerate(joy.axis):
            self.draw_slider(
                v,
                (
                    pos[0],
                    pos[1] + (2 + i) * self.fontheight,
                    tmpwidth,
                    self.fontheight
                )
            )
        """
        presetcolor = self.statictext
        iriscolor = "white"
        focuscolor = "white"
        if cams.controlmode == 0:
            tmpwidth = self.font.size(" ")[0] *2
            for i in cams.modes["Presets"]:
                preset = False
                if cams.currentPreset == i:
                    preset = True
                toptrim = 0
                if i%2 == 1:
                    toptrim = self.fontheight
                self.draw_preset(
                    i+1,
                    (
                        pos[0] + (i * (tmpwidth/2)),
                        pos[1] + (3.25 + joy.numaxes + joy.numballs) * self.fontheight + toptrim,
                        tmpwidth - 10,
                        self.fontheight
                    ),preset
                )
            self.screen.blit(self.altfont.render("Btn 5: Call Preset", self.antialias, presetcolor, Color("#000000")),(pos[0],pos[1] + 9.25 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 6: Set Preset", self.antialias, presetcolor, Color("#000000")),(pos[0],pos[1] + 9.75 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 3: Open Iris Ctrl", self.antialias, iriscolor, Color("#000000")),(pos[0],pos[1] + 10.25 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 2: Open Speed Settings", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 10.75 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 4: Open Focus Ctrl", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 11.25 * self.fontheight))
 
        if cams.controlmode == 1:
            presetcolor = "white"
            iriscolor = self.statictext
            focuscolor = "white"
            for i,v in enumerate(cams.modes["Iris"]):
                preset = False
                if cams.iriscursor == i:
                    preset = True
                self.draw_preset(
                    v,
                    (
                        pos[0] + (i * (tmpwidth)),
                        pos[1] + (3.25 + joy.numaxes + joy.numballs) * self.fontheight,
                        tmpwidth - 10,
                        self.fontheight
                    ),preset
                )
            self.screen.blit(self.altfont.render("Btn 5: Select", self.antialias, iriscolor, Color("#000000")),(pos[0],pos[1] + 9.25 * self.fontheight))
            #self.screen.blit(self.altfont.render("Btn 6: Set Preset", self.antialias, presetcolor, Color("#000000")),(pos[0],pos[1] + 9.75 * self.fontheight))
            #self.screen.blit(self.altfont.render("Btn 3: Open Iris Ctrl", self.antialias, iriscolor, Color("#000000")),(pos[0],pos[1] + 10.25 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 2: Open Preset Ctrl", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 10.75 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 4: Open Focus Ctrl", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 11.25 * self.fontheight))
 
        if cams.controlmode == 2:
            presetcolor = "white"
            focuscolor = self.statictext
            iriscolor = "white"
            for i,v in enumerate(cams.modes["Focus"]):
                preset = False
                if cams.focuscursor == i:
                    preset = True
                self.draw_preset(
                    v,
                    (
                        pos[0] + (i * (tmpwidth)),
                        pos[1] + (3.25 + joy.numaxes + joy.numballs) * self.fontheight,
                        tmpwidth - 10,
                        self.fontheight
                    ),preset
                )
            self.screen.blit(self.altfont.render("Btn 5: Select", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 9.25 * self.fontheight))
            #self.screen.blit(self.altfont.render("Btn 6: Set Preset", self.antialias, presetcolor, Color("#000000")),(pos[0],pos[1] + 9.75 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 3: Open Iris Ctrl", self.antialias, iriscolor, Color("#000000")),(pos[0],pos[1] + 10.25 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 2: Open Preset Ctrl", self.antialias, presetcolor, Color("#000000")),(pos[0],pos[1] + 10.75 * self.fontheight))
            #self.screen.blit(self.altfont.render("Btn 4: Open Focus Ctrl", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 11.25 * self.fontheight))
            #self.screen.blit(self.altfont.render("Btn 1/Trigger: Stop PTZ moves", self.antialias, "white", Color("#000000")),(pos[0],pos[1] + 11.25 * self.fontheight))
        if cams.controlmode == 3:
            presetcolor = "white"
            iriscolor = self.statictext
            focuscolor = "white"
            for i,v in enumerate(cams.modes["Speed"]):
                preset = False
                if cams.speedcursor == i:
                    preset = True
                self.draw_preset(
                    v,
                    (
                        pos[0] + (i * (tmpwidth)),
                        pos[1] + (3.25 + joy.numaxes + joy.numballs) * self.fontheight,
                        tmpwidth - 10,
                        self.fontheight
                    ),preset
                )
            self.screen.blit(self.altfont.render("Current speed is highlighted", self.antialias, iriscolor, Color("#000000")),(pos[0],pos[1] + 9.25 * self.fontheight))
            #self.screen.blit(self.altfont.render("Btn 6: Set Preset", self.antialias, presetcolor, Color("#000000")),(pos[0],pos[1] + 9.75 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 3: Open Iris Ctrl", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 10.25 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 2: Open Preset Ctrl", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 10.75 * self.fontheight))
            self.screen.blit(self.altfont.render("Btn 4: Open Focus Ctrl", self.antialias, focuscolor, Color("#000000")),(pos[0],pos[1] + 11.25 * self.fontheight))
 
    def quit(self, status=0):
        pygame.quit()
        sys.exit(status)

if __name__ == "__main__":
    program = input_test()
    program.init()
    program.run()  # This function should never return