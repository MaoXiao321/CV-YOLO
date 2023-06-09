# YOLOV8
git clone https://github.com/ultralytics/ultralytics.git
## 环境创建
```
# Python>=3.7 PyTorch>=1.7
conda create -n yolo python=3.8
conda install pytorch==1.10.0 torchvision -c pytorch  # 从pytorch官网找安装命令
pip install ultralytics -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt

pip install ultralytics --upgrade # 升级
```
## detect
### 创建数据集(百度云盘：dataset_box_smple.zip)
原始数据存储在/home/data/831/下面，包含.jpg和.xml。运行以下脚本创建images、labels文件夹，并划分数据集产生train.txt和val.txt
```
python dataset_box.py /home/data/831/
```
### train
（1）从ultralytics/datasets下复制coco128.yaml命名为my.yaml，填写train,test的路径（数据集划分时生成的）和类别：
```
train:  /project/train/src_repo/yolov8/dataset/train.txt
val: /project/train/src_repo/yolov8/dataset/val.txt  
names:
  0: head
  1: person
  2: hat
```
（2）从ultralytics/models/v8下复制yolov8.yaml（根据自己需要），把类别数改成自己的。参考：https://docs.ultralytics.com/modes/train/#arguments查看训练参数设置，模型默认保存在runs路径下
```
yolo task=detect mode=train data=ultralytics/datasets/my.yaml model=ultralytics/models/v8/yolov8s.yaml pretrained=yolov8s.pt epochs=2 imgsz=640 batch=8 save_period=1
```
### export
```
yolo export model=yolov8s.pt format=onnx opset=12 
或者：
from ultralytics import YOL
model = YOLO('yolov8s.pt') 
model.export(format='onnx', opset=12)
```
### predict
```
yolo predict model=yolov8s.pt source='bus.jpg'  
# source写链接(https://ultralytics.com/images/bus.jpg)也可，model也支持onnx.输出结果在runs/detect/predict下
或者：
results = model('bus.jpg') # 包含前处理、推理以及后处理
```
## seg
用法参考：https://docs.ultralytics.com/tasks/segment/。数据集准备（百度云盘：dataset_seg_sample.zip和coco数据集instances_500.zip）
以coco数据集为例(instances,500张)，划分train和val<br>
从ultralytics/datasets下复制coco128-seg.yaml到当前目录，命名为my-seg.yaml，改train,val和类别<br>
从ultralytics/models/v8下复制yolov8-seg.yaml到当前目录<br>
```
# train，参数介绍：https://docs.ultralytics.com/usage/cfg/#train（断点继续训练需要改代码，暂时不能直接训练）
yolo task=segment mode=train data=my-seg.yaml model=yolov8m-seg.yaml pretrained=pretrained_model/yolov8m-seg.pt epochs=1
# val
yolo task=segment mode=val data=my-seg.yaml model=yolov8s-seg.yaml model=runs/segment/train/weights/best.pt
# predict
yolo task=segment mode=predict model=yolov8s-seg.pt source='bus.jpg' conf=0.25
# export
yolo export model=path/to/best.pt format=onnx
```
## pose
数据集准备（dataset_keypoints_sample.zip和coco数据集person_keypoints_2d_500.zip）
从ultralytics/datasets下复制yolov8-pose.yaml到当前目录，命名为my-pose.yaml，修改：
```
train:  /project/train/src_repo/yolov8/dataset/train.txt
val: /project/train/src_repo/yolov8/dataset/val.txt 
# Keypoints
kpt_shape: [17, 2]  # number of keypoints, number of dims (2 for x,y or 3 for x,y,visible)
flip_idx: [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]
# Classes
names:
  0: person
```
从ultralytics/models/v8下复制yolov8-pose.yaml到当前目录<br>
```
# train
yolo task=pose mode=train data=my-pose.yaml model=yolov8m-pose.yaml pretrained=pretrained_model/yolov8m-pose.pt epochs=300 imgsz=640
# predict
yolo task=pose mode=predict model=yolov8s-pose.pt source='bus.jpg'
# export
yolo export model=path/to/best.pt format=onnx
```