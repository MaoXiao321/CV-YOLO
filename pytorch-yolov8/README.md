## YOLOV8
git clone https://github.com/ultralytics/ultralytics.git

### 环境创建
```
Python>=3.7
PyTorch>=1.7
pip install ultralytics -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
```

### 创建数据集
原始数据存储在/home/data/831/下面，包含.jpg和.xml。创建以下目录：
```
mkdir dataset
mkdir /home/data/xml
mkdir /home/data/images
mkdir /home/data/labels
cp /home/data/831/*.xml /home/data/xml
cp /home/data/831/*.jpg /home/data/images
# 划分数据集
python /project/train/src_repo/yolov8/split_train_val.py --path /home/data/images --xml_path /home/data/xml  --txt_path /project/train/src_repo/yolov8/dataset
# 将xml转成txt
python /project/train/src_repo/yolov8/voc_label.py
```

### 训练
（1）从ultralytics/datasets下复制一个ymal命名为my.yaml，填写train,test的路径和类别：
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

### 导出onnx
yolo export model=yolov8s.pt format=onnx opset=12 