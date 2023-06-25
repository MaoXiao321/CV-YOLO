yolo task=seg mode=train data=my-seg.yaml model=yolov8m-seg.yaml pretrained=pretrained_model/yolov8m-seg.pt epochs=300 imgsz=640
yolo task=seg mode=train data=my-seg.yaml model=yolov8m-seg.yaml pretrained=runs/segment/train3/weights/last.pt epochs=300 imgsz=640
yolo task=seg mode=val data=my-seg.yaml model=yolov8m-seg.yaml model=runs/segment/train3/weights/best.pt
yolo task=seg mode=predict model=yolov8s-seg.pt source='bus.jpg'