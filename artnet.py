from lib.StupidArtnet import StupidArtnet




class ArtnetClient:
    target_ip = '192.168.2.52'
    universe = 0
    packet_size = 100
    artNetNode : StupidArtnet

    # print(artNetNode)
    mode = 0
    colorIndex = 0
    colorScroll = [(255,0,0),(0,0,255)]

    alternator = 0

    numLamps = 10

    def __init__(self, target_ip, universe, packet_size = 100 ) -> None:
        self.target_ip = target_ip
        self.universe = universe
        self.packet_size = packet_size

        self.artNetNode = StupidArtnet(target_ip, universe, packet_size,0)



    def setPARLight(self, artNetNode, lampe, r, g, b,dimmer = 255, effect= 0, speed= 0):
        offset = lampe * 6
        
        artNetNode.set_single_value(1 + offset, dimmer) # master dimmer
        artNetNode.set_single_value(2 + offset, r)	   # red channel
        artNetNode.set_single_value(3 + offset, g)	   # green channel
        artNetNode.set_single_value(4 + offset, b)	   # blue channel
        # 0-50    strobe and linear dimming
        # 51-100  Transition
        # 101-150 Gradient
        # 151-200 Variable pulse
        # 201-255 sound control
        artNetNode.set_single_value(5 + offset, effect)	   # effect channel
        artNetNode.set_single_value(6 + offset, speed)	   # effect speed channel


    def setAllColor(self,r,g,b):
        for i in range(0,self.numLamps-1):
            self.setPARLight(self.artNetNode,i, r, g, b)

    def setAltColor(self,r,g,b):
        if self.alternator % 2:
            r1 = r
            r2 = 0
            g1 = b
            g2 = 0
            b1 = b
            b2 = 0
        else:
            r1 = 0
            r2 = r
            g1 = 0
            g2 = g
            b1 = 0
            b2 = b


        self.alternator += 1

        for i in range(0,self.numLamps-1):
            if i % 2:
                self.setPARLight(self.artNetNode,i, r1, g1, b1)
            else:
                self.setPARLight(self.artNetNode,i, r2, g2, b2)

    # calm_programs = [
    #     2,  # Full Color Slow
    #     5,  # Retro
    #     8,  # Wipe Noise
    # ]
    # normal_programs = [
    #     1,  # Full Color Moving
    #     3,  # Fill Up Once
    #     6,  # Kitt
    # ]
    # intense_programs = [
    #     4,  # Fill Up Repeat
    #     7,  # Flash Noise
    # ]

    def changeColorScroll(self,program):
        self.mode = 0
        self.colorIndex = 0
        self.alternator = 0
        
        if program == 0:
            self.colorScroll = [(255,0,0),(0,0,255)]
        elif program == 1:
            self.colorScroll = [(255,0,0),(0,255,0),(0,0,255)]
        elif program == 2:
            self.colorScroll = [(255,0,0),(192,192,0),(0,255,0),(192,192,0)]  
        if program == 3:
            self.colorScroll = [(255,0,0),(0,0,255)]
            self.mode = 1
        if program == 4:
            self.colorScroll = [(255,0,0)]
            self.mode = 1
        if program == 5:
            self.colorScroll = [(255,0,0),(192,192,0),(0,255,0),(0,192,192),(0,0,255),(192,0,192)]
        if program == 6:
            self.colorScroll = [(255,0,0),(0,255,0)]
        if program == 7:
            self.colorScroll = [(255,0,0),(192,0,192)]
        if program == 8:
            self.colorScroll = [(192,128,0)]      
            self.mode = 1                                          
        else:
            self.colorScroll = [(255,0,0),(0,0,255)]
        
        print("Change colorScroll to {:d} and mode to {:d}".format(program, self.mode))   
        # print(self.colorScroll)         

       


    def setNextColor(self):
        c = self.colorScroll[self.colorIndex]

        self.colorIndex +=1
        if self.colorIndex >= len(self.colorScroll):
            self.colorIndex = 0

        if self.mode == 0:
            self.setAllColor(c[0],c[1],c[2])
        elif self.mode == 1:
            self.setAltColor(c[0],c[1],c[2])
        else:
            self.setAllColor(c[0],c[1],c[2])


    def artNetShow(self,beat_index):

        self.setNextColor()
        # print("artnet update " + "Beat: {:d}".format(bpm))
        self.artNetNode.show()

