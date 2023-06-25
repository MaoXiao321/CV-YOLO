yolo task=pose mode=train data=my-pose.yaml model=yolov8m-pose.yaml pretrained=pretrained_model/yolov8m-pose.pt epochs=300 imgsz=640
yolo task=pose mode=train data=my-pose.yaml model=yolov8m-pose.yaml pretrained=runs/pose/train3/weights/last.pt epochs=300 imgsz=640
yolo task=pose mode=val data=my-pose.yaml model=yolov8m-pose.yaml model=runs/pose/train3/weights/best.pt
yolo task=pose mode=predict model=yolov8s-pose.pt source='bus.jpg'