import glob
from pathlib import Path
import argparse
import shutil
import json
import os
import xml.etree.ElementTree as ET
import numpy as np

"""
<?xml version="1.0" encoding="UTF-8"?>
<annotation>
  <filename>20220401114142781789.jpg</filename>
  <size>
    <width>4000</width>
    <height>3000</height>
    <depth>3</depth>
  </size>
  <polygon>
    <class>sticker_air_outlet</class>
    <points>1473,1488;1454,1625;2771,1640;2752,1505</points>
  </polygon>
</annotation>
"""

class dataset_keypoints():
    def __init__(self, data_path = '/home/data/1'):
        self.data_path = data_path
        self.root_path = os.path.dirname(data_path)
        self.CLASSES = ['out_air_outlet','sticker_air_outlet','enter_air_outlet']
        self.image_path = os.path.join(self.root_path,'images')
        self.label_path = os.path.join(self.root_path,'labels')
    
    def check_label(self):
        """xml多边形标注，寻找非四点标注的图片"""
        files = glob.glob(str(Path(self.data_path) / '*.xml'), recursive=True)
        for xml_file in files:
            tree = ET.parse(xml_file)
            root = tree.getroot() # annotation
            for polygon in root.findall('polygon'):
                points = polygon.find('points').text    
                if len(points.split(';')) != 4:
                    print(xml_file)
        print("check labels done!\n")
    
    def make_images(self):
        if not os.path.exists(self.image_path): os.mkdir(self.image_path) 
        files = glob.glob(str(Path(self.data_path) / '*.jpg'), recursive=True)
        for file in files:
            shutil.copy(file, self.image_path)
        print("make images done!\n")     
    
    def order_points(self, pts):
        """顺时针排序box四个点"""
        pts = np.float32(pts) 
        center = np.array([0,0])
        for i in range(4):
            center = center + pts[i]
        center = center / 4
        # 水平框
        left,right = [],[]
        for i in range(4): left.append(pts[i]) if pts[i][0] < center[0] else right.append(pts[i])
        if len(left) == len(right):
            tl = left[0] if left[0][1] < left[1][1] else left[1]
            tr = right[0] if right[0][1] < right[1][1] else right[1]
            bl = left[1] if left[0][1] < left[1][1] else left[0]
            br = right[1] if right[0][1] < right[1][1] else right[0]    
        else:
            # 竖直框
            top,bottom = [],[]
            for i in range(4): top.append(pts[i]) if pts[i][1] < center[1] else bottom.append(pts[i])
            tl = top[0] if top[0][0] < top[1][0] else top[1]
            tr = top[1] if top[0][0] < top[1][0] else top[0]
            bl = bottom[0] if bottom[0][0] < bottom[1][0] else bottom[1]
            br = bottom[1] if bottom[0][0] < bottom[1][0] else bottom[0]
        point = np.float32([tl, tr, br, bl])
        return point
    
    def xmlTotxt(self):
        """xml多边形标注转txt"""
        if not os.path.exists(self.label_path): os.mkdir(self.label_path) 
        
         # 解析关键点：<class-index> <x> <y> <width> <height> <px1> <py1> <px2> <py2> ... <pxn> <pyn>,归一化
        files = glob.glob(str(Path(self.data_path) / '*.xml'), recursive=True)
        for xml_path in files:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            filename = root.find('filename').text
            outfile = os.path.join(self.label_path,filename.split('.')[0]+'.txt')
            
            size = root.find('size')
            width_int = int(size.find('width').text)
            height_int = int(size.find('height').text)
            dw = 1.0 / width_int
            dh = 1.0 / height_int
            for polygon in root.findall('polygon'):
                classname = polygon.find('class').text
                category_id = self.CLASSES.index(classname) # 转下编号
                points_txt = (polygon.find('points').text).split(';')
                
                all_points = []
                for point in points_txt:
                    x,y = [float(i) for i in point.split(',')]
                    all_points.append([x, y])
                xmin = np.array(all_points)[:,0].min()
                xmax = np.array(all_points)[:,0].max()
                ymin = np.array(all_points)[:,1].min()
                ymax = np.array(all_points)[:,1].max()
                cx = (xmin + xmax) / 2 * dw
                cy = (ymax + ymin) / 2 * dh
                w = (xmax - xmin + 1) * dw
                h = (ymax - ymin + 1) * dh
                
                points = self.order_points(all_points) 
                points[:,0] *= dw
                points[:,1] *= dh
                line = f'{category_id} {cx} {cy} {w} {h} '
                for point in points:
                    line += ' '.join([str(i) for i in point])
                    line += ' '
                line += '\n'
                with open(outfile,'a') as f:
                    f.write(line)
        print("make labels done!\n")
    
    def split_data(self): 
        for path in ['train.txt','val.txt'] : 
            if os.path.exists(path): os.remove(path) 
        
        seed = [2]
        ftrain = open('train.txt', 'a', encoding='utf-8')
        fval = open('val.txt', 'a', encoding='utf-8')
        image_files = glob.glob(str(Path(self.image_path)/ '*.jpg'), recursive=True)
        for i, img in enumerate(image_files):
            flag = 'val' if (i + 1) % 10 in seed else 'train'  # 划分train和val,10张里取一张作为val
            line = f'{img}\n' 
            fval.write(line) if flag == 'val' else ftrain.write(line)
        ftrain.close()
        fval.close()
        print("split done!\n")
    
    def forward(self):
        self.check_label()
        self.make_images()
        self.xmlTotxt()
        self.split_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', default='home/data/3', type=str, help='iamges path')
    args = parser.parse_args()
    
    dataset = dataset_keypoints(data_path = args.data_path)
    dataset.forward()