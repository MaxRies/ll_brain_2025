from lib.StupidArtnet import StupidArtnet
import time

class baulichter:
    target_ip = '10.39.0.54'
    universe = 0
    packet_size = 120
    artNetNode : StupidArtnet
    
    # colorScroll = [(255,0,0),(0,0,255)]

    numLamps = 8
    mainDimmer = 128
    program = 4
    enable = 0

    pattern_cycle_index = 0

    ledOffset = 1


    def __init__(self, target_ip, universe = 0, packet_size = 120 ) -> None:
        self.target_ip = target_ip
        self.universe = universe
        self.packet_size = packet_size
        self.artNetNode = StupidArtnet(self.target_ip, self.universe, self.packet_size,0)
    

    def setProgram(self, prog ):
        # if prog >= 4:
        self.program = prog
        # print("Baulichter prog {}".format(self.program))

        
    def setEnable(self, ena):
        self.enable = ena
        # print("Baulichter ena {}".format(ena))
        
    def tick(self):

        if self.enable > 0:
            
            if self.program == 4: # full blink 
                self.pattern_cycle_index = (self.pattern_cycle_index  +1) % self.numLamps # select next light
                if(self.pattern_cycle_index  % 2):
                    for i in range(self.numLamps):
                        self.artNetNode.set_single_value(i*3 + self.ledOffset, self.mainDimmer ) 
                else:
                    for i in range(self.numLamps):
                        self.artNetNode.set_single_value(i*3 + self.ledOffset, 0)                 

                
            elif self.program == 7: # alternate blink 
                for i in range(self.numLamps):
                    self.artNetNode.set_single_value(i*3 + self.ledOffset, 0 ) 
                
                self.pattern_cycle_index = (self.pattern_cycle_index +1) % (self.numLamps) # select next light

                for i in range(self.numLamps):
                    if(i +self.pattern_cycle_index)   % 2 :
                        self.artNetNode.set_single_value(i*3 + self.ledOffset, self.mainDimmer) # set next light on 

            else: # Lauflicht
                for i in range(self.numLamps):
                    self.artNetNode.set_single_value(i*3 + self.ledOffset, 0 ) 

                self.pattern_cycle_index = (self.pattern_cycle_index +1) % (self.numLamps) # select next light
                self.artNetNode.set_single_value(self.pattern_cycle_index*3 + self.ledOffset, self.mainDimmer) # set next light on 

        else:
            for i in range(self.numLamps):
                self.artNetNode.set_single_value(i*3 + self.ledOffset, 0)          

        self.artNetNode.show()


    def strobe(self):
        for i in range(self.numLamps):
            self.artNetNode.set_single_value(i*3 + self.ledOffset, 255) 
        self.artNetNode.show()  
        time.sleep(0.05)  
        for i in range(self.numLamps):
            self.artNetNode.set_single_value(i*3 + self.ledOffset, 0) 
        self.artNetNode.show()          

    def close(self):
        self.artNetNode.close()