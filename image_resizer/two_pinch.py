# 両手のピンチ動作を認識してイメージを移動、縮小・拡大するサンプル
# Ultraleap python-bindings example 参照 : https://github.com/ultraleap/leapc-python-bindings/blob/main/examples/simple_pinching_example.py
import cv2
import time
import leap
from leap import datatypes as ldt
import numpy as np
from screeninfo import get_monitors

# イメージがモニター外に移動しないようにモニター解像度を読み込む
m = get_monitors()
monitor_w = m[0].width
monitor_h = m[0].height

# サイズ変更のトリガーフラグ
start = False
# 左手・右手のピンチ
pinching_l = False
pinching_r = False
# 移動のトリガーフラグ
m_start = False

# 左手と右手の距離変動値
diff_dist = 0
# トリガーが起動した時のイメージのサイズ
prev_dist = 0
scale = 1

# 初期化
point_l = np.array((0,0,0))
point_r = np.array((0,0,0))
index_l = (0, 0, 0)
index_r = (0, 0, 0)

curr_win_x = prev_win_x = init_win_x = 100
curr_win_y = prev_win_y = init_win_y = 100


# 使用するイメージを読み込む
img = cv2.imread('img/univ_img.jpg')

# イメージのサイズ情報を取得する
curr_win_h, curr_win_w, _ = img.shape

# イメージの大きさを制限するためのしきい値
w_min_thr = curr_win_w * 0.1
h_min_thr = curr_win_h * 0.1

w_max_thr = curr_win_w * 5
h_max_thr = curr_win_h * 5


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
        global diff_dist, prev_dist, curr_win_w, curr_win_h, center, pinching_l, pinching_r, start, scale, angle, prev_angle
        global curr_win_x, curr_win_y, prev_win_x, prev_win_y, m_start, index_l, index_r, point_l, point_r
        
        if event.tracking_frame_id % 30 == 0:            
            for i in range(0, len(event.hands)):
                hand = event.hands[i]              

                # 左手のピンチ動作を判断する
                if (str(hand.type) == "HandType.Left"):                                     
                    thumb_l = location_end_of_finger(hand, 0)
                    index_l = location_end_of_finger(hand, 1)
                    point_l = np.array((index_l.x, index_l.y, index_l.z))  
                    pinching_l, _ = fingers_pinching(thumb_l, index_l)
                


                # 右手のピンチ動作を判断する
                if (str(hand.type) == "HandType.Right"):                     
                    thumb_r = location_end_of_finger(hand, 0)
                    index_r = location_end_of_finger(hand, 1)
                    point_r = np.array((index_r.x, index_r.y, index_r.z))  
                    pinching_r, _ = fingers_pinching(thumb_r, index_r)
                              
                          
            # 両手がピンチ動作をしている場合、左手と右手の距離に応じてイメージを縮小・拡大する
            if pinching_l and pinching_r :
                # ピンチ動作がトリガーとなり、人差し指先の位置情報を追跡し始める
                if start == False:         
                    # 両手の距離を計算する (ユークリッド距離)
                    prev_dist = np.linalg.norm(point_l - point_r) 
                    prev_vector = (index_l.x - index_r.x, index_l.y - index_r.y)                    
                    start = True

                # 両手の距離の変動値を計算する
                curr_dist = np.linalg.norm(point_l - point_r)
                diff_dist = curr_dist - prev_dist
                
                
                # イメージ出力でエラーが出ないように変動できるスケールを制限する
                scale = 1+(diff_dist/curr_win_w)
                if scale < 0.1 :
                    scale = 0.1
                if scale > 5:
                    scale = 5

                # イメージのリサイジング
                curr_win_w = curr_win_w * scale
                curr_win_h = curr_win_h * scale

                if (curr_win_w < w_min_thr) or (curr_win_h < h_min_thr):
                    curr_win_w = w_min_thr
                    curr_win_h = h_min_thr

                if (curr_win_w > w_max_thr) or (curr_win_h > h_max_thr):
                    curr_win_w = w_max_thr
                    curr_win_h = h_max_thr
                        
            if not (pinching_l and pinching_r)  : 
                start = False           


            # 片手の位置変動を取得し、イメージの移動距離として反映させる
            if pinching_l != pinching_r :

                # 左手でイメージを動かす
                if pinching_l :
                    win_x = index_l.x
                    win_y = index_l.y
                    
                    if m_start == False:
                        prev_win_x = win_x
                        prev_win_y = win_y
                        m_start = True
                    

                # 右手でイメージを動かす
                if pinching_r :
                    win_x = index_r.x
                    win_y = index_r.y

                    if m_start == False:
                        prev_win_x = win_x
                        prev_win_y = win_y
                        m_start = True
                        
                curr_win_x += win_x - prev_win_x
                curr_win_y -= win_y - prev_win_y

            if not pinching_l and not pinching_r :
                m_start = False
                
            
                
                
                    
                        


def main():
    global curr_win_w, curr_win_h, curr_win_x, curr_win_y
    
    listener = PinchingListener()
    connection = leap.Connection()
    connection.add_listener(listener)    

    with connection.open():
        while True:        

            if curr_win_x <=0 : curr_win_x = 10
            elif curr_win_x > monitor_w : curr_win_x = (monitor_w - 100)

            if curr_win_y <=0 : curr_win_y = 10
            elif curr_win_y > monitor_h : curr_win_y = (monitor_h - 100)
                
            dst = cv2.resize(img, (int(curr_win_w), int(curr_win_h)))
            cv2.imshow('img', dst)
            cv2.moveWindow('img', int(curr_win_x), int(curr_win_y))

            # 'q'キーを押して、プログラムを終了する
            if cv2.waitKey(1) == ord('q'):
                break
    cv2.destroyAllWindows()
            


if __name__ == "__main__":
    main()
