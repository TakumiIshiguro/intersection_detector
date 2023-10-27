# intersection_detector
単眼カメラを用いた通路分類パッケージ

分類クラス：４つ  
[0]:straight_road [1]:3_way [2]:cross_road [3]:corridor  
または  
分類クラス：8つ  
[0]straight_road,[1]dead_end,[2]corner_right,[3]corner_left,  
[4]cross_road,[5]3_way_right,[6]3_way_center,[7]3_way_left  


## ネットワーク  
1. 時系列考慮なし
  - CNN３ ＋　全結合層２

2. 時系列考慮あり（intersectnet)　[推奨]
  - MobileNetV3-Large + lstm + fc    
D.Bhattらが提案したCNN＋LSTMを組み合わせたネットワークをベースに構築  
https://ieeexplore.ieee.org/document/8206317  

## INSTALL
```
git clone https://github.com/haruyama8940/intersection_detector.git
git clone https://github.com/haruyama8940/scenario_navigation_msgs.git
```

## RUN
### Create Dataset
データセットの作成はオンラインで作成する方法と  
rosbagを用いてオフラインで作成する方法があります．  
1.のネットワーク
```
roslaunch intersection_detector create_dataset.launch
```
2.のネットワーク
```
roslaunch intersection_detector create_dataset_lstm.launch
```
### Learning
1.のネットワーク
```
rosrun intersection_detactor learning2tensor.py
```
2.のネットワーク
```
rosrun intersection_detactor learning2tensor_lstm.py
```
### Detect
1.のネットワーク
```
roslaunch intersection_detector intersection_detect.launch
```  

2.のネットワーク
```
roslaunch intersection_detector intersection_detect_lrcn.launch 
```

## VIDEO
[![](https://img.youtube.com/vi/7Fzg816eF_I/0.jpg)](https://www.youtube.com/watch?v=7Fzg816eF_I)
