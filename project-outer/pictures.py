import requests
import pandas as pd
import os
import shutil
import json
import cv2
import argparse
import glob
from pathlib import Path

class Getimg():
    """下载图片"""
    def __init__(self,filename):
        self.filename = filename
        self.output_dir = filename.split('.')[0]
    
    def download_img(self, img_url, api_token):
        header = {"Authorization": "Bearer " + api_token}  # 设置http header，视情况加需要的条目，这里的token是用来鉴权的一种方式
        r = requests.get(img_url, headers=header, stream=True)
        # print(r.status_code) # 返回状态码
        path = os.path.join(f'{self.output_dir}/', img_url.split('/')[-1])
        if r.status_code == 200:
            open(path, 'wb').write(r.content)  # 将内容写入图片
            # print('done')
        else:
            print(path)
    
    def forward(self, drop=True, column='文件完整路径'):
        data = pd.read_excel(self.filename)    
        if drop: 
            drop_data = data.drop_duplicates(subset=['文件完整路径'])  # 去重
            print(f"total_drop:{len(drop_data)}")
        else:
            drop_data = data.copy()
            print(f"total:{len(drop_data)}")
        
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir) 
        for img_url in drop_data[column]:
            api_token = "fklasjfljasdlkfjlasjflasjfljhasdljflsdjflkjsadljfljsda"
            self.download_img(img_url, api_token)
        print(f"{self.output_dir}图片下载完毕!")        

class Process():
    """将所有图片统一为jpg格式"""
    def __init__(self, input_path):
        super().__init__()
        self.input_path = input_path
        self.root_path = os.path.dirname(self.input_path)
        self.output_path = f'{self.input_path}_out'
        self.image_path = os.path.join(self.root_path,'images')
        self.label_path = os.path.join(self.root_path,'json')
        # self.find_image = os.path.join(self.root_path,'find')
        

    def change_Suffix(self):
        if not os.path.exists(self.output_path): os.makedirs(self.output_path)
        
        image_file = os.listdir(self.input_path)
        for image in image_file:   
            x,y = image.split('.')
            if y in ['bmp', 'jpg', 'jpeg', 'png', 'JPG', 'PNG']: # 原本是jpg的也转一遍
                new_img = f"{x}.jpg"
                input_path = os.path.join(self.input_path, image)
                out_path = os.path.join(self.output_path, new_img)
                img = cv2.imread(input_path)
                cv2.imwrite(out_path, img)
                # os.remove(input_path)
        print(f"modify done! file path: {self.output_path}")   
    
    def remove_chi(self, fromstr=['微信图片'], tostr=['']):
        """将图片名中的中文替换为空"""
        if not os.path.exists(self.output_path): os.makedirs(self.output_path)
        image_file = os.listdir(self.input_path)
        for image in image_file:   
            input_path = os.path.join(self.input_path, image)
            for i,s in enumerate(fromstr):
                if s in image: 
                    image = image.replace(s,tostr[i])
            out_path = os.path.join(self.output_path, image)
            os.rename(input_path, out_path)           
        print("modify done!")       
    
    def move_images(self):
        if not os.path.exists(self.image_path): os.mkdir(self.image_path) 
        files = glob.glob(str(Path(self.input_path) / '*.jpg'), recursive=True)
        for file in files:
            shutil.copy(file, self.image_path)
        print("move images done!\n")   
    
    def move_labels(self):
        if not os.path.exists(self.label_path): os.mkdir(self.label_path) 
        
        files = glob.glob(str(Path(self.input_path) / '*.json'), recursive=True)
        for file in files:
            shutil.copy(file, self.label_path)
            # shutil.move(file, self.label_path)
        print("move labels done!\n")      
    
    # def find_labels(self):
    #     # if not os.path.exists(self.label_path): os.mkdir(self.label_path) 
    #     files =  os.listdir(self.find_image)
    #     for file in files:
    #         json_file = os.path.join(self.label_path, file.split('.')[0]+'.json')
    #         shutil.copy(json_file, self.find_image)
    #     print("find json done!\n")   
    
    def check_pair(self):     
        """保证self.image_path中img和标注文件配对"""         
        self.move_labels() 
        
        img_files =  os.listdir(self.image_path)
        json_files =  os.listdir(self.label_path)
        for file in img_files:
            json_file = file.split('.')[0]+'.json'
            if json_file not in json_files:
                print(f"{file} don't have json file.")
                os.remove(os.path.join(self.image_path,file)) # 删掉图片
        print(f"check pair done! file path: {self.image_path}\n")   

if __name__ == '__main__':
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("--data_path", "-r", type=str, default='home/data/1') # 工作目录
        return parser.parse_args()
    args = parse_args()
    
    # # 下载图片
    # for cls in ['铜管']:   
    #     filename = f"{cls}.xlsx"
    #     getimg = Getimg(filename)
    #     getimg.forward()
    
    # 图片放到input文件夹下，将其他后缀改成jpg
    process = Process(args.data_path)
    process.check_pair()
    process.change_Suffix() # 所有图片转成jpg
  
    # process.find_labels() 
    # process.remove_chi(fromstr=['微信图片'], tostr=[''])

    
    
    # for name in ['新铜管']:
    #     # process_ocr(name)
    #     for data in ['室外机照片20230320-20230419']:
    #         data_f = pd.read_excel(f'{data}.xlsx')
    #         for img_url in data_f['文件完整路径']:
    #             api_token = "fklasjfljasdlkfjlasjflasjfljhasdljflsdjflkjsadljfljsda"
    #             download_img(img_url, api_token, data)
    #         print(f"{data}图片下载完毕!")
    # mv_picturs2()

    # process_fk()
    # mv_picturs()  # 移动图片
    # for name in ['true', 'false']:
    #     data_f = pd.read_excel(f'{name}.xlsx')
    #     for img_url in data_f['文件完整路径']:
    #         # 下载要的图片
    #         # img_url = "https://ra.marketsales.daikin.net.cn/php/uploadFiles/20220621170754399101.jpg"
    #         api_token = "fklasjfljasdlkfjlasjflasjfljhasdljflsdjflkjsadljfljsda"
    #         download_img(img_url, api_token, name)
    #     print(f"{name}图片下载完毕!")
