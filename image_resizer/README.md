*LeapC, OpenCV, Numpy, screeninfo のインストールが必要です。


>pip install opencv-python
>
>pip install numpy
>
>pip install screeninfo

*LeapC インストール方法
- Ultraleap社 Github：https://github.com/ultraleap/leapc-python-bindings
- Cornes WEBマガジン：https://cornestech.co.jp/column/ultraleap_rpi
(「4. Python環境でハンドトラッキングを実現する Python-bindingの設定」参照)

pinch_3d.py: 片手のピンチジェスチャーを認識し、画像の移動と拡大縮小を行います。

* 画像移動: ピンチ状態のまま手をデバイスのX軸/Y軸方向に動かすと、画像がそれに応じて移動します。
* 画像拡大縮小: ピンチ状態のまま手をデバイスのZ軸方向に動かすと、Z座標に応じて画像の拡大縮小が行われます。

two_pinch.py: 両手のピンチジェスチャーを認識し、画像の移動と拡大縮小を行います。

* 画像移動 (片手): 片手のピンチ状態のまま手をデバイスのX軸/Y軸方向に動かすと、画像がそれに応じて移動します。
* 画像拡大縮小: 両手のピンチ状態における両手の距離が、画像の拡大縮小率に反映されます。

grab_3d.py: 片手のグラブジェスチャーを認識し、画像の移動と拡大縮小を行います。

* 画像移動: グラブ状態のまま手をデバイスのX軸/Y軸方向に動かすと、画像がそれに応じて移動します。
* 画像拡大縮小: グラブ状態のまま手をデバイスのZ軸方向に動かすと、グラブの開き具合に応じて画像の拡大縮小が行われます。
