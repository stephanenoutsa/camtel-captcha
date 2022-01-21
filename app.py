from dotenv import load_dotenv
from fastai.vision import *
from flask import Flask
from flask_restful import Api, Resource, reqparse
import werkzeug

load_dotenv()

app = Flask(__name__)
api = Api(app)

BASE_URL = 'http://myxtremnet.cm/web/'
URL = BASE_URL + 'index!login.action'
CAPTCHAS_DIR = 'captchas/'

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

api.add_resource(CaptchaPredictor, '/predict')

def load_model():
    # defaults.device = torch.device('cpu')
        
    base_path = '/var/www/html/camtel-captcha/captchas/test/models' # FOR PRODUCTION!!
    # base_path = './captchas/test/models' # FOR DEVELOPMENT!!
    
    learn_list = []
        
    for i in range(4):
        file = 'stage-indi-pos-' + str(i+1) + '.pkl'

        learner = load_learner(base_path, file)
        learn_list.append(learner)
    
    return learn_list

if __name__ == '__main__':
    # learn_list = load_model()
    
    app.run(debug=True)
