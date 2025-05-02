import threading
import queue
import baulichter
import artnet
from z2mLamps import BeatLampController

class lightshow:
    beatdiff = 0
    def __init__(self) -> None:
        # Queues pro Komponente
        self._queue_bls = queue.Queue()
        self._queue_artnet = queue.Queue()
        self._queue_beat = queue.Queue()
        self.running = True

        # Objekte
        self.bls = baulichter.baulichter('10.39.0.54', 0)
        self.artnet_client = artnet.ArtnetClient('192.168.178.70', 0 )
        # self.artnet_client = artnet.ArtnetClient('192.168.2.52', 0, 120)
        BROKER, PORT = "192.168.178.50", 1883
        lamp_topics = [f"zigbee2mqtt/WSP_A{i+1}/set" for i in range(8)]
        self.beat_controller = BeatLampController(BROKER, PORT, lamp_topics, blink_duration=0.2)

        # Threads starten
        threading.Thread(target=self._worker, args=(self._queue_bls,  self.bls),          daemon=True).start()
        threading.Thread(target=self._worker, args=(self._queue_artnet, self.artnet_client), daemon=True).start()
        threading.Thread(target=self._worker, args=(self._queue_beat,  self.beat_controller), daemon=True).start()

    def _worker(self, q: queue.Queue, obj):
        """Allgemeiner Worker: erwartet (method_name, args)-Tupel oder None als Stop-Signal."""
        while True:
            task = q.get()
            if task is None:
                break
            method_name, args = task
            getattr(obj, method_name)(*args)

    def send_strobe_signal(self):
        self._queue_bls.put(("strobe",       []))
        self._queue_artnet.put(("strobe", []))
        

    def send_prog_signal(self, program):
        # Befehle in die Queues schieben, nicht direkt ausführen
        self._queue_bls.put(("setProgram",       [program]))
        self._queue_artnet.put(("changeColorScroll", [program]))

        # if program < 12:
        self._queue_beat.put(("select_pattern",  [program]))

        if program == 12:
            self._queue_beat.put(("setHoldColorHSB",  [0,80,120]))            
        elif program == 13:
            self._queue_beat.put(("setHoldColorHSB",  [150,50,120]))
        elif program == 14:
            self._queue_beat.put(("setHoldColorHSB",  [260,80,120]))
        elif program == 15:
            self._queue_beat.put(("setHoldColorHSB",  [0,0,0]))                        

    def send_beat_signal(self):
        self._queue_bls.put(("tick",             []))
        self._queue_artnet.put(("artNetShow",      []))

        self.beatdiff = (self.beatdiff+1) % 2
        if self.beatdiff == 0:
            self._queue_beat.put(("update_on_beat", []))

    def setMainDimmer(self, dimmer):
        self.mainDimmer = dimmer
        # bls und beat_controller haben diese Methode bzw. Attribut
        self._queue_bls.put(("setEnable",       [int(bool(dimmer))]))
        self._queue_beat.put(("set_global_dimmer", [dimmer/255.0]))

    def send_bar_signal(self):
        # noch keine Implementierung – hier analog schieben:
        # self._queue_bls.put(("…", […]))
        pass

    def intensityChange(self, intensity):
        # direkt oder per Queue möglich, hier als Beispiel direkt:
        self._queue_bls.put(("setEnable", [int(intensity==1)]))

    def close(self):
        # Stop-Signale für alle Worker
        for q in (self._queue_bls, self._queue_artnet, self._queue_beat):
            q.put(None)
        # Original-Close-Calls
        self.bls.close()
        self.artnet_client.close()
        self.beat_controller.disconnect()
