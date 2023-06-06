## 代码准备
```
git clone https://github.com/ultralytics/yolov5
```
## 安装依赖
```
pip install -r requirements.txt
```
## 数据准备
原始数据存储在/home/data/1/下面，包含.jpg和.xml。创建以下目录：
```
mkdir /home/data/xml
mkdir /home/data/images
mkdir /home/data/labels
cp /home/data/1/*.xml /home/data/xml
cp /home/data/1/*.jpg /home/data/images
# 划分数据集：
mkdir /project/train/src_repo/yolov5/dataset
python /project/train/src_repo/yolov5/split_train_val.py --path /home/data/images --xml_path /home/data/xml  --txt_path /project/train/src_repo/yolov5/dataset
# 将xml转成txt
python /project/train/src_repo/yolov5/voc_label.py
```
## 训练
data中新建my.yaml，参照其他的yml文件写。
```
wget https://github.com/ultralytics/yolov5/releases/download/v6.2/yolov5s.pt
python /project/train/src_repo/yolov5/train.py  --batch-size 8 --data ./data/my.yaml --weights yolov5s.pt --cfg models/yolov5s.yaml --project /project/train/models/ --epochs 2 --workers 0
```
## predict
```
python detect.py --weights yolov5s.pt --source 0                               # webcam  --conf-thres 0.6
                                               img.jpg                         # image
                                               vid.mp4                         # video
                                               screen                          # screenshot
                                               path/                           # directory
                                               list.txt                        # list of images
                                               list.streams                    # list of streams
                                               'path/*.jpg'                    # glob
                                               'https://youtu.be/Zgi9g1ksQHc'  # YouTube
                                               'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP stream
```
## 转onnx
```
python export.py --data ./data/brass.yaml --weights /project/train/models/exp/weights/best.pt --include onnx
```
