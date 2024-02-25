import threading
import visca_over_ip as Visca
import PyATEMMax

class Cameras():
    def __init__(self,atem_ip = None):
        self.atem = None
        if atem_ip:
            self.atem = PyATEMMax.ATEMMax()
            self.atem.connect(atem_ip)
            self.atem.waitForConnection()
            self.atem.registerEvent(self.atem.atem.events.receive, self.atemInputChanged)
        self.current = None
        self.cameras = []
        self.stopped = True
        self.pan = 0
        self.panning = False
        self.tilt = 0
        self.tilting = False
        self.zoom = 0
        self.currentPreset = 0
        self.focuscursor =  0
        self.iriscursor = 0
        self.speedcursor = 1
        self.controlmode = 3
        self.defaultPTMultiplier = 6
        self.defaultZoomMultiplier = 2
        self.modes = {"Presets":range(16),"Iris":("Iris -","Iris +"),"Focus":("AF","Focus -","Focus +"),"Speed":("Slow","Standard","Fast")}
        self.lockout = False
        self.visca = None
        
    class camera():
        def __init__(self,name,ip,atem_input = None):
            self.name = name
            self.ip = ip
            self.atem_input = atem_input
    def atemInputChanged(self,dict):
        if dict['cmd'] == 'PrvI':
                print("ATEM Input set to %s" % self.atem.previewInput[0].videoSource.value)
                latestInput = self.atem.previewInput[0].videoSource.value
                print("current input we are on is: %s " % self.cameras[self.current].atem_input)
                if self.cameras[self.current].atem_input != latestInput:
                    for c,cam in enumerate(self.cameras):
                        if self.cameras[c].atem_input == latestInput:
                            self.start(self.cameras[c].name)
                            print("switching to camera %s" % self.cameras[c].name)

    def nextModeOption(self):
        if self.controlmode == 0:
            #presets
            if self.currentPreset == len(self.modes["Presets"]) -1:
                self.currentPreset = 0
            else:
                self.currentPreset = self.currentPreset + 1
        if self.controlmode == 1:
            #iris
            if self.iriscursor == len(self.modes["Iris"]) -1:
                self.iriscursor = 0
            else:
                self.iriscursor = self.iriscursor + 1
        if self.controlmode == 2:
            #focus
            if self.focuscursor == len(self.modes["Focus"]) -1:
                self.focuscursor = 0
            else:
                self.focuscursor = self.focuscursor + 1
        if self.controlmode == 3:
            #focus
            if self.speedcursor == len(self.modes["Speed"]) -1:
                self.speedcursor = 0
            else:
                self.speedcursor = self.speedcursor + 1
    def prevModeOption(self):
        if self.controlmode == 0:
            #presets
            if self.currentPreset == 0:
                self.currentPreset = len(self.modes["Presets"]) -1
            else:
                self.currentPreset = self.currentPreset - 1
        if self.controlmode == 1:
            #iris
            if self.iriscursor == 0:
                self.iriscursor = len(self.modes["Iris"]) -1
            else:
                self.iriscursor = self.iriscursor - 1
        if self.controlmode == 2:
            #focus
            if self.focuscursor == 0:
                self.focuscursor = len(self.modes["Focus"]) -1
            else:
                self.focuscursor = self.focuscursor - 1
        if self.controlmode == 3:
            #focus
            if self.speedcursor == 0:
                self.speedcursor = len(self.modes["Speed"]) -1
            else:
                self.speedcursor = self.speedcursor - 1
    def nextCamera(self):
        print(self.current)
        nextCam = self.current + 1
        if self.current == len(self.cameras) - 1:
            nextCam = 0
        self.start(self.cameras[nextCam].name)
        if(self.atem):
            self.atem.setPreviewInputVideoSource(0, self.cameras[nextCam].atem_input)
    def prevCamera(self):
        print(self.current)
        prevCam = self.current - 1
        if self.current == 0:
            prevCam =len(self.cameras)-1
        self.start(self.cameras[prevCam].name)
        if(self.atem):
            self.atem.setPreviewInputVideoSource(0, self.cameras[prevCam].atem_input)
    def add(self,name,ip,atem_input = None):
        self.cameras.append(Cameras.camera(name,ip,atem_input))
    def start(self, name):
        for i,n in enumerate(self.cameras):
            if n.name == name:
                self.current = i
                print("send command to initiate camera %s at ip %s" % (n.name,n.ip))
                if self.visca != None:
                    self.visca.close_connection()
                self.visca = Visca.Camera(n.ip)
    def pt_stop(self):
        if not self.stopped and (self.pan == 0 and self.tilt == 0):
            print("STOP camera pan tilt %s at ip %s" % (self.cameras[self.current].name,self.cameras[self.current].ip))
            self.visca.pantilt(pan_speed=0, tilt_speed=0)
            self.stopped = True
            self.panning = False
            self.tilting = False
    def pt_forcestop(self):
        print("STOP camera pan tilt %s at ip %s" % (self.cameras[self.current].name,self.cameras[self.current].ip))
        self.visca.pantilt(pan_speed=0, tilt_speed=0)
        self.stopped = True
        self.panning = False
        self.tilting = False
        self.lockout = True
        t = threading.Timer(5.0, self.pt_unstop)
        t.start()
    def pt_unstop(self):
        self.lockout = False
    def ptz_pan(self,val):
        if not self.lockout:
            new = round(self.defaultPTMultiplier*(1 + self.speedcursor)*val)
            if new != self.pan:
                self.pan = new
                self.ptz_pantilt()
            if self.pan != 0:
                self.stopped = False
                self.panning = True
        
    def ptz_tilt(self,val):
        if not self.lockout:
            new = round(self.defaultPTMultiplier*(1 + self.speedcursor)*val)
            if new != self.tilt:
                self.tilt = new
                self.ptz_pantilt()
            if self.tilt != 0:
                self.stopped = False
                self.tilting = True

    def ptz_pantilt(self):
        if(self.pan == 0 and self.tilt == 0):
            #delegate ptz command
            self.pt_stop()
        else:
            #handle ptz command
            print("send command to pantilt camera %s at ip %s: Pan: %d Tilt: %d" % (self.cameras[self.current].name,self.cameras[self.current].ip,self.pan,self.tilt))
            self.visca.pantilt(pan_speed=(-1 * self.pan), tilt_speed=(-1*self.tilt))

    def ptz_zoom(self,val):
        if not self.lockout:
            speed = round(self.defaultZoomMultiplier*(1 + self.speedcursor)*val)
            if speed != self.zoom:
                self.zooming = True
                self.zoom = speed
                print("send command to zoom camera %s at ip %s with speed %d" % (self.cameras[self.current].name,self.cameras[self.current].ip,speed))
                self.visca.zoom(speed)
                self.stopped = False