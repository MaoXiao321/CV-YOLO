import glob
from pathlib import Path
import argparse
import shutil
import os
import xml.etree.ElementTree as ET
import numpy as np

class dataset_box():
    def __init__(self, data_path = '/home/data/1'):
        self.data_path = data_path
        self.root_path = os.path.dirname(data_path)
        self.CLASSES = self.get_class('names.txt')
        self.image_path = os.path.join(self.root_path,'images')
        self.label_path = os.path.join(self.root_path,'labels')
    
    def get_class(self, filename):
        with open(filename,'r',encoding='utf-8') as f:
            lines = f.readlines()
        return [line.split('\n')[0] for line in lines]
    
    def check_label(self):
        """labelme目标检测标注，寻找类别错误的图片"""
        files = glob.glob(str(Path(self.data_path) / '*.xml'), recursive=True)
        for xml_file in files:
            tree = ET.parse(xml_file)
            root = tree.getroot() # annotation
            for object in root.findall('object'):
                name = object.find('name').text    
                if name not in self.CLASSES:
                    print(xml_file)
        print("check labels done!\n")
    
    def make_images(self):
        if not os.path.exists(self.image_path): os.mkdir(self.image_path) 
        files = glob.glob(str(Path(self.data_path) / '*.jpg'), recursive=True)
        for file in files:
            shutil.copy(file, self.image_path)
        print("make images done!\n")     
    
    def xmlTotxt(self):
        """xml转txt"""
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
            for object in root.findall('object'):
                classname = object.find('name').text
                category_id = self.CLASSES.index(classname) # 转下编号
                
                bndbox = object.find('bndbox')
                xmin = float(bndbox.find('xmin').text)
                xmax = float(bndbox.find('xmax').text)
                ymin = float(bndbox.find('ymin').text)
                ymax = float(bndbox.find('ymax').text)
                cx = (xmin + xmax) / 2 * dw
                cy = (ymax + ymin) / 2 * dh
                w = (xmax - xmin + 1) * dw
                h = (ymax - ymin + 1) * dh
                
                line = f'{category_id} {cx} {cy} {w} {h}\n'
                with open(outfile,'a') as f:
                    f.write(line)
        print("make labels done!\n")
    
    def split_data(self):
        ls = ['train.txt','val.txt']   
        for path in ls: 
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
    parser.add_argument('--data_path', default='home/data/2', type=str, help='iamges path')
    args = parser.parse_args()
    
    dataset = dataset_box(data_path = args.data_path)
    dataset.forward()
    
    


