import glob
from pathlib import Path
import argparse
import shutil
import json
import os
import numpy as np
import math

class dataset_seg():
    def __init__(self, data_path = '/home/data/1'):
        self.data_path = data_path
        self.root_path = os.path.dirname(self.data_path)
        self.CLASSES = ['outer','f1', 'f2', 'f3', 'f4', 'b1', 'b2', 'b3', 'b4']
        self.image_path = os.path.join(self.root_path,'images')
        self.label_path = os.path.join(self.root_path,'labels')
                
    def make_images(self):
        if not os.path.exists(self.image_path): os.mkdir(self.image_path) 
        image_files = glob.glob(str(Path(self.data_path) / '*.jpg'), recursive=True)
        for img in image_files:
            shutil.copy(img, self.image_path)
        print("move images done!\n")        
    
    def check_label(self):
        """确保没有错误的label"""
        # filename = 'label_count.txt'
        # if os.path.exists(filename): os.remove(filename)
        # f = open(filename, 'a', encoding='utf-8')
        json_files = glob.glob(str(Path(self.data_path) / '*.json'), recursive=True)
        for json_path in json_files:
            # dic = dict(zip(self.CLASSES,[0]*len(self.CLASSES)))
            json_labels = json.load(open(json_path, "r"))
            for annotation in json_labels['shapes']:
                classname = annotation['label'] # 类别名
                if classname not in self.CLASSES:
                    print(f"label wrong:{json_path} don't have {classname}")
        print("check labels done!\n")   
    
    def check_groupid(self):
        """确保有groupid的关键点必须有匹配的box"""
        json_files = glob.glob(str(Path(self.data_path) / '*.json'), recursive=True)
        for json_path in json_files:
            # dic = dict(zip(self.CLASSES,[0]*len(self.CLASSES)))
            json_labels = json.load(open(json_path, "r"))
            group1,group2 = [],[]
            for annotation in json_labels['shapes']:
                classname = annotation['label'] # 类别名
                group_id = annotation['group_id']
                if not group_id: group_id = 'null'
                
                if classname in self.CLASSES[1:]: # 关键点
                    group1.append(group_id)
                if classname == 'outer':
                    group2.append(group_id)
            
            group1 = list(set(group1))
            group2 = list(set(group2))
            for group_id in group1:
                if group_id not in group2: print(f"groupid wrong: {json_path}, group_id = {group_id} not in box.")
        print("check groupid done!\n")   
        
    def GetAngle(self, line1, line2):
        """
        计算两条线段之间的夹角
        :param line1:
        :param line2:
        :return:
        """
        dx1 = line1[0][0] - line1[1][0]
        dy1 = line1[0][1] - line1[1][1]
        dx2 = line2[0][0] - line2[1][0]
        dy2 = line2[0][1] - line2[1][1]
        angle1 = math.atan2(dy1, dx1)
        angle1 = int(angle1 * 180 / math.pi)
        # print(angle1)
        angle2 = math.atan2(dy2, dx2)
        angle2 = int(angle2 * 180 / math.pi)
        # print(angle2)
        if angle1 * angle2 >= 0:
            insideAngle = abs(angle1 - angle2)
        else:
            insideAngle = abs(angle1) + abs(angle2)
            if insideAngle > 180:
                insideAngle = 360 - insideAngle
        insideAngle = insideAngle % 180
        return insideAngle
          

    def jsonTotxt(self):
        """labelme关键点标注json转txt"""
        if not os.path.exists(self.label_path): os.mkdir(self.label_path) 
        
        json_files = glob.glob(str(Path(self.data_path) / '*.json'), recursive=True)
        category_id = 0
        # 解析关键点：<class-index> <x> <y> <width> <height> <px1> <py1> <px2> <py2> ... <pxn> <pyn>,归一化
        for json_path in json_files:
            try:
                json_labels = json.load(open(json_path, "r"))
                # filename = json_labels['imagePath']      
                filename = json_path.split('\\')[-1].replace('.json','.txt')
                outfile = os.path.join(self.label_path,filename)
                
                h = json_labels['imageHeight'] # list
                w = json_labels['imageWidth'] # list
                dw = 1.0 / w
                dh = 1.0 / h
                
                # 找有几个group
                group_ids = []
                for annotation in json_labels['shapes']:
                    group_id = annotation['group_id']
                    if not group_id: group_id = 'null' 
                    group_ids.append(group_id)
                group_ids = list(set(group_ids))
                if not group_ids: print(f"no label: {json_path}")
                # print(f'roup_ids:{roup_ids}')
                
                # 存每个group的信息
                dic = dict(zip(self.CLASSES,[[0.0,0.0]]*len(self.CLASSES)))
                res = [dic] * len(group_ids)
                for annotation in json_labels['shapes']:
                    classname = annotation['label'] 
                    group_id = annotation['group_id']
                    if not group_id: group_id = 'null'
                    group_index = group_ids.index(group_id) # 找当前group的索引
                    dic = res[group_index].copy() 
                    
                    if classname in self.CLASSES[1:]: # 点
                        point = annotation['points'][0]  # [x,y]
                        dic[classname] = point
                        res[group_index] = dic
                    elif classname=='outer': # 多边形
                        point= annotation['points'] # [[x,y],[x,y]]
                        dic[classname] = point
                        res[group_index] = dic
                    else:
                        print(f"label wrong: {json_path}, group_id = {group_id} have no label.")
                # print(res)
                
                # 遍历group进行写入
                for dic in res:
                    all_points = [] # 存所有点
                    tmp = [] # 存非(0,0)的点，用于检查角度
                    for key in self.CLASSES[1:]:
                        value = dic[key]
                        if sum(value) > 0: tmp.append(key) 
                        all_points.append(value) # [[x,y],[x,y],...]
                    
                    # 对存在的点进行角度关系判断
                    if 'f1' in tmp and 'f2' in tmp and 'f3' in tmp and 'f4' in tmp:
                        line1 = [dic['f1'],dic['f2']]
                        line2 = [dic['f1'],dic['f3']]
                        angle1 = self.GetAngle(line1, line2)
                        line2 = [dic['f1'],dic['f4']]
                        angle2 = self.GetAngle(line1, line2)
                        if angle1 > angle2: print(f"angle wrong: {json_path}")
                    if 'f1' in tmp and 'f2' in tmp and 'b1' in tmp and 'b2' in tmp:
                        line1 = [dic['f1'],dic['f2']]
                        line2 = [dic['f1'],dic['b2']]
                        angle1 = self.GetAngle(line1, line2)
                        line2 = [dic['f1'],dic['b1']]
                        angle2 = self.GetAngle(line1, line2)
                        if angle1 > angle2: print(f"angle wrong: {json_path}") 
                    if 'b1' in tmp and 'b2' in tmp and 'b3' in tmp and 'b4' in tmp:
                        line1 = [dic['b1'],dic['b2']]
                        line2 = [dic['b1'],dic['b3']]
                        angle1 = self.GetAngle(line1, line2)
                        line2 = [dic['b1'],dic['b4']]
                        angle2 = self.GetAngle(line1, line2)
                        if angle1 > angle2: print(f"angle wrong: {json_path}")               
                    
                    # x = np.array(all_points)[:,0]
                    # y = np.array(all_points)[:,1]
                    # x = x[x>0]
                    # y = y[y>0]
                    # xmin,xmax = x.min(),x.max()
                    # ymin,ymax = y.min(),y.max()    
                    # print(xmin,xmax,ymin,ymax)     
                    # cx = (xmin + xmax) / 2 * dw
                    # cy = (ymax + ymin) / 2 * dh
                    # w = (xmax - xmin + 1) * dw
                    # h = (ymax - ymin + 1) * dh         
                    
                    # 算box的中心点和宽高，做归一化
                    x1,y1 = dic['outer'][0]  # 左上和右下角点位置不固定
                    x3,y3 = dic['outer'][1]
                    w = abs(x3 - x1 + 1) * dw
                    h = abs(y3 - y1 + 1) * dh
                    # if w < 0 or h < 0: print(f"{json_path}")
                    cx = (x1+x3) / 2 * dw
                    cy = (y1+y3) / 2 * dh
                    line = f'{category_id} {cx} {cy} {w} {h} '
                    
                    # 所有点做归一化
                    x = np.array(all_points)[:,0] * dw
                    y = np.array(all_points)[:,1] * dh
                    for i in range(len(x)):
                        line += str(x[i]) + ' ' + str(y[i]) + ' '
                    line += '\n'      
                    # print(line)      
                    with open(outfile,'a') as f:
                        f.write(line)
            except:
                print(f"wrong txt: {json_path} can't obtain txt file.")
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
        # self.check_groupid()
        # self.make_images()
        self.jsonTotxt()
        # self.split_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', default='home/data/1', type=str, help='iamges path')
    args = parser.parse_args()
    
    dataset = dataset_seg(data_path = args.data_path)
    dataset.forward()