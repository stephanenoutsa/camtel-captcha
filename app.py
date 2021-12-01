from bs4 import BeautifulSoup
from captcha.image import ImageCaptcha
from dotenv import load_dotenv
from fastai.vision import *
from flask import Flask
from flask_restful import abort, Api, Resource, reqparse
from pathlib import Path
import os, requests, shutil, time, werkzeug

load_dotenv()

app = Flask(__name__)
api = Api(app)

BASE_URL = 'http://myxtremnet.cm/web/'
URL = BASE_URL + 'index!login.action'
CAPTCHAS_DIR = 'captchas/'

class CaptchaReader(Resource):
    def get(self):
        for i in range(3027):
            page = requests.get(URL)
        
            soup = BeautifulSoup(page.content, 'html.parser')
            
            loginForm = soup.find(id='formLogin')
            
            tables = loginForm.find_all('table', class_='l_tb')
            
            if len(tables) == 0:
                abort(404, 'Table element to scrape not found')
            
            table = tables[0]
            
            images = table.find_all('img')
            
            if len(images) == 0:
                abort(404, 'Image element to scrape not found')
            
            img = images[0]['src']
            captcha_url = BASE_URL + img
            captcha = requests.get(captcha_url)
            
            open(CAPTCHAS_DIR + str(time.time()) + '.jpg', 'wb').write(captcha.content)
            
        return 'Captcha images downloaded'
    
class CaptchaLabeler(Resource):
    def get(self):
        src_path = CAPTCHAS_DIR + 'a'
        
        entries = Path(src_path)
        
        for entry in entries.iterdir():
            filename = entry.name
            filename_without_extension = filename.split('.jpg')[0]
            
            src = src_path + '/' + filename + '.jpg'
            
            dest_path = CAPTCHAS_DIR + 'a/' + filename_without_extension
            dest = Path(dest_path)
            dest.mkdir(exist_ok=True)
            
            if (os.path.isfile(os.path.join(src_path, filename + '.jpg'))):
                # count file in the dest folder with same name..
                count = sum(1 for dest_f in os.listdir(dest_path) if dest_f == filename + '.jpg')
                
                # suffix file count if duplicate file exists in dest folder
                if count:
                    dest_file = filename + '_' + str(count + 1) + '.jpg'
                else:
                    dest_file = filename + '.jpg'
                
                # shutil.move(src, dest_path)
                shutil.move(src, os.path.join(dest_path, dest_file))
            else:
                continue
        
        return 'Captcha images labeled'
    
class CaptchaClassifier(Resource):
    def get(self):
        base_path = CAPTCHAS_DIR + 'a/'
        dirs = os.listdir(base_path)
        
        for label in dirs:
            label_path = base_path + label
            images = os.listdir(label_path)
            image_count = len(images)
            
            if (image_count == 0):
                print(label_path)
            elif (image_count < 100):
                src_path = label_path + '/' + images[0]
                loop_count = 100 - image_count
                
                for x in range(image_count, loop_count + 1):
                    prefix = label_path + '/' + label + '_'
                    suffix = str(x + 1)
                    
                    dest_path = prefix + suffix + '.jpg'
                    
                    shutil.copy(src_path, dest_path)
            else:
                continue
        
        return 'Captcha images classified'
    
class CaptchaGenerator(Resource):
    def get(self):
        base_path = CAPTCHAS_DIR + 'generated/'
        image = ImageCaptcha()
        
        start_label = 1111
        end_label = 10000
        
        for i in range(start_label, end_label):
            label = str(i)
            print(base_path + label)
            
            if '0' not in label:
                image.generate(label)
                image.write(label, base_path + label + '.png')
                
                # dest_path = base_path + label
                # dest = Path(dest_path)
                # dest.mkdir(exist_ok=True)
                
                # for j in range(1000):
                #     image.generate(label)
                #     image.write(label, dest_path + '/' + str(j+1) + '.png')
        
        return 'Captcha images generated'

class CaptchaPredictor(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('image', type=werkzeug.datastructures.FileStorage, location='files')
        
        args = parser.parse_args()
        
        image = args['image']
        image = open_image(image)
        
        prediction = ''
        
        learn_list = load_model()
        
        for i in learn_list:
            print(i.path)
            pred_class, pred_idx, outputs = i.predict(image)
            
            prediction += str(pred_class)
        
        return prediction
    
api.add_resource(CaptchaReader, '/fetch')
api.add_resource(CaptchaLabeler, '/label')
api.add_resource(CaptchaClassifier, '/classify')
api.add_resource(CaptchaGenerator, '/generate')
api.add_resource(CaptchaPredictor, '/predict')

def load_model():
    defaults.device = torch.device('cpu')
        
    base_path = './captchas/test/'
    bs = 64
    
    alist = os.listdir(base_path)

    for i in range(len(alist)):
        alist[i] = [alist[i]]
        
        for j in range(4):
            alist[i].append(alist[i][0][j])

    df = pd.DataFrame(alist)
    
    learn_list = []
        
    for i in range(4):
        data = ImageDataBunch.from_df(base_path, df, folder='', size=(77, 247), bs=bs, seed=43, label_col=i+1)
        
        learn = cnn_learner(data, models.resnet50, metrics=accuracy, ps=0.1, pretrained=False)
        learn.load('stage-indi-pos-' + str(i+1))
        
        learn_list.append(learn)
    
    return learn_list

if __name__ == '__main__':
    # learn_list = load_model()
    
    app.run(debug=True)
