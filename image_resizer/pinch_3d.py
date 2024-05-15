# ピンチ動作を認識してイメージを移動、縮小・拡大するサンプル
# Ultraleap python-bindings example 参照 : https://github.com/ultraleap/leapc-python-bindings/blob/main/examples/simple_pinching_example.py

import cv2
import time
import leap
from leap import datatypes as ldt

# トリガーが起動した時の指先のX, Y, Z 座標
prev_x = 0
prev_y = 0
prev_z = 0

# トリガーフラグ
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


# 指先の位置情報を取得する
def location_end_of_finger(hand: ldt.Hand, digit_idx: int) -> ldt.Vector:
    digit = hand.digits[digit_idx]
    return digit.distal.next_joint

# ベクトルのマップを作成する
def sub_vectors(v1: ldt.Vector, v2: ldt.Vector) -> list:
    return map(float.__sub__, v1, v2)


# ピンチ動作を判断する
# 親指先と人差し指先の距離が20px以下になったらピンチと判断
def fingers_pinching(thumb: ldt.Vector, index: ldt.Vector):
    diff = list(map(abs, sub_vectors(thumb, index)))

    if diff[0] < 20 and diff[1] < 20 and diff[2] < 20:
        return True, diff
    else:
        return False, diff


class PinchingListener(leap.Listener):
    def on_tracking_event(self, event):
        global curr_win_x, curr_win_y, prev_win_x, prev_win_y, prev_x, prev_y, prev_z, start, curr_win_w, curr_win_h, prev_win_h, prev_win_w
        if event.tracking_frame_id % 30 == 0:
            for hand in event.hands:
                hand_type = "Left" if str(hand.type) == "HandType.Left" else "Right"

                # 指先の位置情報を取得
                thumb = location_end_of_finger(hand, 0)
                index = location_end_of_finger(hand, 1)

                # ピンチの判断
                pinching, array = fingers_pinching(thumb, index)

                # ピンチ操作の場合、人差し指先の移動距離に応じてイメージを移動させる
                if pinching :
                    # ピンチ操作がトリガーとなり、人差し指先の位置情報を追跡し始める
                    if start is False:
                        prev_x = index.x
                        prev_y = index.y
                        prev_z = index.z

                        prev_win_x = curr_win_x
                        prev_win_y = curr_win_y

                        prev_win_w = curr_win_w
                        prev_win_h = curr_win_h

                        #トリガーフラグを変更
                        start = True

                    # 現在の人差し指先の位置 (x, y) とトリガーが起動した時の位置の差を、イメージの移動距離として反映する
                    curr_win_x = prev_win_x + (index.x - prev_x)
                    curr_win_y = prev_win_y - (index.y - prev_y)   

                    # 現在の人差し指先の位置 (z) とトリガーが起動した時の位置の差を、イメージのスケールとして反映する
                    # カメラのセンターから (-) 方向だと縮小、(+) 方向だと拡大される
                    resize_rate = index.z - prev_z                    
                    
                    curr_win_w = prev_win_w + resize_rate
                    curr_win_h = prev_win_h + resize_rate                  
                

                # ピンチではない場合、トリガーフラグを初期化する
                elif not pinching : 
                    start = False               
                        


def main():
    global curr_win_x, curr_win_y, curr_win_w, curr_win_h

    listener = PinchingListener()

    connection = leap.Connection()
    connection.add_listener(listener)

    

    with connection.open():
        while True:        
            dst = cv2.resize(img, (int(curr_win_w), int(curr_win_h)))
            cv2.imshow('img', dst)
            cv2.moveWindow('img', int(curr_win_x), int(curr_win_y))

            # 'q'キーを押すとプログラムが終了する
            if cv2.waitKey(1) == ord('q'):
                break
    cv2.destroyAllWindows()
            


if __name__ == "__main__":
    main()
