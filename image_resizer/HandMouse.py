# beta版
# hand tracking & pinching 参照：https://github.com/ultraleap/leapc-python-bindings

import leap
from pynput import mouse
from leap import datatypes as ldt
import keyboard
from screeninfo import get_monitors
import threading


gm = get_monitors()
w = gm[0].width
h = gm[0].height

m = mouse.Controller()
map_x = map_y = 100

sensor_w = 640
sensor_h = 480
x_weight = int(w/sensor_w)
y_weight = int(h/sensor_h)
margin = 400

x, y = 0, 0
mouse_start = False
        
def mouse_click(pinching):
    if pinching :
        m.press(mouse.Button.left)                     
    else:
        m.release(mouse.Button.left)    

def palm_center(hand: ldt.Hand) -> ldt.Vector:
    center = hand.palm.position
    return center

def palm_velocity(hand: ldt.Hand):
    vel = hand.palm.velocity    
    return abs(vel.x), abs(vel.y)    

def location_end_of_finger(hand: ldt.Hand, digit_idx: int) -> ldt.Vector:
    digit = hand.digits[digit_idx]
    return digit.distal.next_joint

def sub_vectors(v1: ldt.Vector, v2: ldt.Vector) -> list:
    return map(float.__sub__, v1, v2)

def fingers_pinching(thumb: ldt.Vector, index: ldt.Vector):    
    diff = list(map(abs, sub_vectors(thumb, index)))
    if diff[0] < 20 and diff[1] < 20 and diff[2] < 20:
        return True, diff
    else:
        return False, diff

class MouseThread(threading.Thread):
    def run(self):
        global x, y, mouse_start        
        while True:
                intx = (x + (sensor_w/2)) * x_weight
                inty = ((sensor_h/2 + margin) - y) * y_weight    
                if mouse_start :           
                    if intx >= w :
                        intx = w - 5
                    elif intx <= 0 :
                        intx = 5

                    if inty >= h :
                        inty = h - 5
                    elif inty <= 0:
                        inty = 5        
                      
                    m.position = (intx, inty)
                    
                if keyboard.is_pressed('q'):                
                    break
                                     

class PinchingListener(leap.Listener):     
    def on_tracking_event(self, event): 
        global mouse_start, x, y                
        if event.tracking_frame_id % 30 == 0:            
            for i in range(0, len(event.hands)):          
                hand = event.hands[i] 
                #hand_type = "Left" if str(hand.type) == "HandType.Left" else "Right"
                #print("hand is detected")
                center = palm_center(hand)
                velx, vely = palm_velocity(hand)                

                thumb = location_end_of_finger(hand, 0)
                index = location_end_of_finger(hand, 1)
                
                pinching, _ = fingers_pinching(thumb, index)

                if velx * vely != 0 :
                    mouse_start = True
                else:
                    mouse_start = False
                

                x = int(center.x)
                y = int(center.y)

                mouse_click(pinching)                     

def main():   
    listener = PinchingListener()
    connection = leap.Connection()
    connection.add_listener(listener)       

    with connection.open():
        thread = MouseThread()
        thread.run()        
            

if __name__ == "__main__":
    main()
