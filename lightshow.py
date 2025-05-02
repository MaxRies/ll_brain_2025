import baulichter
import artnet
from z2mLamps import BeatLampController


class lightshow:

    artnet_client: artnet.ArtnetClient
    bls: baulichter.baulichter
    mainDimmer = 0

    def __init__(self) -> None:

        self.bls = baulichter.baulichter('10.39.0.54',0)
        self.artnet_client = artnet.ArtnetClient('192.168.178.70',0,256)

        BROKER = "192.168.178.50"
        PORT = 1883
        lamp_topics = [
            "zigbee2mqtt/WSP_A1/set",
            "zigbee2mqtt/WSP_A2/set",
            "zigbee2mqtt/WSP_A3/set",
            "zigbee2mqtt/WSP_A4/set",
            "zigbee2mqtt/WSP_A5/set",
            "zigbee2mqtt/WSP_A6/set",
            "zigbee2mqtt/WSP_A7/set",
            "zigbee2mqtt/WSP_A8/set",
        ]
        self.beat_controller = BeatLampController(BROKER, PORT, lamp_topics, blink_duration=0.2)


    def send_prog_signal(self, program):
        # print("send program signal")

        self.bls.setProgram(program)
        self.artnet_client.changeColorScroll(program)
        self.beat_controller.select_pattern(program)
        
    def send_beat_signal(self):
        # print("send beat signal")

        self.bls.tick()
        self.artnet_client.artNetShow()
        # self.beat_controller.update_on_beat()

    def setMainDimmer(self, dimmer):
        self.mainDimmer = dimmer
        self.bls.mainDimmer = dimmer

        self.beat_controller.set_global_dimmer(dimmer/255.0)     
        
    def send_bar_signal(self):
        # print("send bar signal")
        pass

    def intensityChange(self, intensity):
        if(intensity==1):
            self.bls.setEnable(intensity)
        elif(intensity==0):
            self.bls.setEnable(intensity)
        else:
            pass

    def close(self):
        self.bls.close()
        self.artnet_client.close()
        self.beat_controller.disconnect()
