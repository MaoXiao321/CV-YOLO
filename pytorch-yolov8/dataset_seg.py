import glob
from pathlib import Path
import argparse
import shutil
import json
import os

class dataset_seg():
    def __init__(self, data_path = '/home/data/1'):
        self.data_path = data_path
        self.root_path = os.path.dirname(self.data_path)
        self.CLASSES = ['return_air_inlet','wall_opening']
        self.image_path = os.path.join(self.root_path,'images')
        self.label_path = os.path.join(self.root_path,'labels')
                
    def make_images(self):
        if not os.path.exists(self.image_path): os.mkdir(self.image_path) 
        image_files = glob.glob(str(Path(self.data_path) / '*.jpg'), recursive=True)
        for img in image_files:
            shutil.copy(img, self.image_path)
        print("move images done!\n")        
    
    def check_label(self):
        """label count: labelme多边形标注获得json文件"""
        filename = 'label_count.txt'
        if os.path.exists(filename): os.remove(filename)
        
        f = open(filename, 'a', encoding='utf-8')
        json_files = glob.glob(str(Path(self.data_path) / '*.json'), recursive=True)
        for json_path in json_files:
            dic = dict(zip(self.CLASSES,[0]*len(self.CLASSES)))
            json_labels = json.load(open(json_path, "r"))
            for annotation in json_labels['shapes']:
                try:
                    classname = annotation['label'] # 类别名
                    dic[classname] += 1               
                except:
                    continue
            line = '\t'.join([str(i) for i in dic.values()])
            line = f'{json_path}\t{line}\n'
            f.write(line)
        f.close()
        print("check labels done!\n")         

    def jsonTotxt(self):
        """labelme多边形标注json转txt"""
        if not os.path.exists(self.label_path): os.mkdir(self.label_path) 
        json_files = glob.glob(str(Path(self.data_path) / '*.json'), recursive=True)
        # 解析分割：<class-index> <x1> <y1> <x2> <y2> ... <xn> <yn>,归一化
        for json_path in json_files:
            json_labels = json.load(open(json_path, "r"))
            filename = json_labels['imagePath'] # list
            h = json_labels['imageHeight'] # list
            w = json_labels['imageWidth'] # list
            for annotation in json_labels['shapes']:
                try:
                    segmentation = annotation['points']  # 分割点坐标
                    classname = annotation['label'] # 类别名
                    category_id = self.CLASSES.index(classname) # 转下编号
                    
                    x = [i[0]/w for i in segmentation] # x坐标归一化
                    y = [i[1]/h for i in segmentation] # y坐标归一化
                    xy = ''
                    for i in range(len(x)):
                        xy += str(x[i]) + ' ' + str(y[i]) + ' '
                    line = str(category_id)+ ' ' + xy + '\n'
                    outfile = filename.split('.')[0]+'.txt'               
                    outfile = os.path.join(self.label_path,outfile)
                    with open(outfile,'a') as f:
                        f.write(line)
                except:
                    continue
        print("make labels done!\n")
    
    def split_data(self): 
        for path in ['train.txt','val.txt']:  
            if os.path.exists(path): os.remove(path)
        
        seed = [2,5]
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
        # self.check_label()
        self.make_images()
        self.jsonTotxt()
        self.split_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', default='home/data/2', type=str, help='iamges path')
    args = parser.parse_args()
    
    dataset = dataset_seg(data_path = args.data_path)
    dataset.forward()