from ultralytics import YOLO
from matplotlib import pyplot as plt
import cv2
import numpy as np
from shapely.geometry import Polygon
import os

def xy2points(xyxy):
    x1,y1,x2,y2 = np.float32(xyxy)
    points = np.float32([[x1,y1],[x2,y1],[x2,y2],[x1,y2]])
    return points

def find_returnair(box_out, box_in):
    # 判断wall和return_air是否是一对
    box_in = xy2points(box_in) # return_air
    box_out = xy2points(box_out) # wall
    area_both = Polygon(box_in).intersection(Polygon(box_out)).area # 回风口与wall的inter
    area_in = Polygon(box_in).area 
    ratio = area_both/area_in 
    # print(ratio)
    out = 1 if ratio > 0.9 else 0  # 1表示return_air在wall里
    return out

def find_minrec(mask):
    coords = np.where(mask==1) # np.nonzero(a).numpy()是（y,x）
    points = np.array([*zip(coords[1],coords[0])]) # (x,y),wall所有的坐标点
    minrec = cv2.minAreaRect(points)   
    return minrec

if __name__ == '__main__':
    input_path = 'input'
    output_path = f'{input_path}_out'
    
    if not os.path.exists(output_path): os.makedirs(output_path)
    f = open('result.txt', "a", encoding='utf-8')
        
    for filename in os.listdir('input'):
        model = YOLO('return_air_inlet/best.pt') 
        
        results = model(os.path.join(input_path,filename)) 
        boxes = results[0].boxes 
        masks = results[0].masks
        
        # 画图
        res_plotted = results[0].plot()
        # plt.imshow(res_plotted)
        cv2.imwrite(os.path.join(output_path,filename), res_plotted)

        # 获取标签的索引
        arr = boxes.cls.numpy()
        arr0 = [i[0] for i in np.argwhere(arr==0)] # return_air
        arr1 = [i[0] for i in np.argwhere(arr==1)] # wall
        
        if len(arr0) == 0 and len(arr1) == 0: 
            line = f'{filename}\t0 return_air 0 wall_opening\n'
            f.write(line)
        if len(arr0) == 0 and len(arr1) > 0: 
            line = f'{filename}\t0 return_air\n' 
            f.write(line)
        if len(arr1) == 0 and len(arr0) > 0: 
            line = f'{filename}\t0 wall_opening\n' 
            f.write(line)
        if len(arr0) >0 and len(arr1)>0:
            for obj1 in arr1:
                tmp = []
                mask = masks.data[obj1]

                # 找wall里的回风口是哪个
                for obj0 in arr0:
                    if find_returnair(boxes.xyxy[obj1],boxes.xyxy[obj0]) == 1: # 找到了回风口
                        tmp.append(obj0)
                        mask = mask + masks.data[obj0] # 拼接mask,还原wall 
                    
                if len(tmp) == 0: # 该wall没有匹配的回风口
                    continue
                else:
                    minrec_out = find_minrec(mask) # 获取wall的minAreaRect
                    _, (w_out,h_out), angle_out = minrec_out
                    if angle_out > 45: w_out,h_out = h_out,w_out
                    out = (w_out, h_out, angle_out)
                    print(f'wall:{out}') 

                    # 获取回风口的minAreaRect
                    w_in, h_in, angle_in = [],[],[]
                    for obj0 in tmp:
                        minrec_in = find_minrec(masks.data[obj0])
                        _, (w, h), angle = minrec_in
                        if angle > 45: w,h = h,w
                        out = (w, h, angle)    
                        print(f'return_air:{out}')    
                        w_in.append(w)
                        h_in.append(h)
                        angle_in.append(angle)   
                    w0 = np.max(w_in)
                    h0 = np.max(h_in)
                    
                    # 算空隙的宽高
                    if h_out < w_out:  # 横框
                        w = w_out - np.sum(w_in)
                        h = h_out
                    else:  # 竖框
                        w = w_out
                        h = h_out - np.sum(h_in)   
                    out = (w, h)
                    print(f'wall-return_air:{out}\t')    
                    
                    out = (w/w0,h/h0)       
                    print(f'ratio:{out}')    
                    line = f'{filename}\t{out}\n'
                    f.write(line)
                    print('-------------------------')   
    f.close()
                