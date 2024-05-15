# Ultraleap python-bindings example 参照 : https://github.com/ultraleap/leapc-python-bindings/blob/main/examples/simple_pinching_example.py

import cv2
import time
import leap
from leap import datatypes as ldt

prev_x = 0
prev_y = 0
prev_z = 0
start = False

# 現在のイメージの位置 (移動先)
curr_win_x = 200
curr_win_y = 100

# トリガーが起動した時のイメージの位置
prev_win_x = 0
prev_win_y = 0

# トリガーが起動した時のイメージのサイズ
prev_win_w = 0
prev_win_h = 0

# 使用するイメージを読み込む
img = cv2.imread('img/univ_img.jpg')

# イメージのサイズ情報を取得する
curr_win_h, curr_win_w, _ = img.shape


# 手のひらの位置情報を取得
def palm_center(hand: ldt.Hand) -> ldt.Vector:
    center = hand.palm.position
    return center

# grab strengthでgrab状態を判断
def grab_hand(hand: ldt.Hand):
    strength = hand.grab_strength
    if strength >= 0.8:
        return True
    else:
        return False


class GrabListener(leap.Listener):
    def on_tracking_event(self, event):
        global curr_win_x, curr_win_y, prev_win_x, prev_win_y, prev_x, prev_y, prev_z, start, curr_win_w, curr_win_h, prev_win_h, prev_win_w
        if event.tracking_frame_id % 30 == 0:
            for hand in event.hands:
                hand_type = "Left" if str(hand.type) == "HandType.Left" else "Right"
                
                grab = grab_hand(hand)
                center = palm_center(hand)

                
                # grab操作の場合、手のひらの移動距離に応じてイメージを移動させる
                if grab :
                    # grab操作がトリガーとなり、手のひらの位置情報を追跡し始める
                    if start is False:
                        prev_x = center.x
                        prev_y = center.y
                        prev_z = center.z

                        prev_win_x = curr_win_x
                        prev_win_y = curr_win_y

                        prev_win_w = curr_win_w
                        prev_win_h = curr_win_h

                        #トリガーフラグを変更
                        start = True

                    # 現在の手のひらの位置 (x, y) とトリガーが起動した時の位置の差を、イメージの移動距離として反映する
                    curr_win_x = prev_win_x + (center[0] - prev_x)
                    curr_win_y = prev_win_y - (center[1] - prev_y)   

                    # 現在の手のひらの位置 (z) とトリガーが起動した時の位置の差を、イメージのスケールとして反映する
                    # カメラのセンターから (-) 方向だと縮小、(+) 方向だと拡大される
                    resize_rate = center.z - prev_z                    
                    
                    curr_win_w = prev_win_w + resize_rate
                    curr_win_h = prev_win_h + resize_rate                  
                

                # grabではない場合、トリガーフラグを初期化する
                elif not grab : 
                    start = False               
                        


def main():
    global curr_win_x, curr_win_y, curr_win_w, curr_win_h

    listener = GrabListener()

    connection = leap.Connection()
    connection.add_listener(listener)

    

    with connection.open():
        while True:        
            dst = cv2.resize(img, (int(curr_win_w), int(curr_win_h)))
            cv2.imshow('img', dst)
            cv2.moveWindow('img', int(curr_win_x), int(curr_win_y))     

            # 'q'キーを押して終了
            if cv2.waitKey(1) == ord('q'):
                break
    cv2.destroyAllWindows()
            


if __name__ == "__main__":
    main()
