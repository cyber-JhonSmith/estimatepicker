from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import pdfplumber
from dotenv import load_dotenv
import os
from os.path import join, dirname
import time

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

def adjustImage(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1]
    if file_type == 'pdf' or file_type == 'PDF':
        with pdfplumber.open(uploaded_file) as pdf:
            first_page = pdf.pages[0]
            image = first_page.to_image()
            image_path = f'./img/{os.path.splitext(uploaded_file.name)[0]}.png'
            image.save(image_path, format="png")
            image = Image.open(image_path)
    else:
        image = Image.open(uploaded_file)
        image_path = f"./img/{uploaded_file.name}"
        image.save(image_path)
    
    return([image, image_path])

def sculp_image(image, results):
    font_path = "./times.ttf"
    draw = ImageDraw.Draw(image)
    i = 1
    for result in results:
        x = result[1][0]
        y = result[1][1]
        w = result[1][2]
        h = result[1][5]
        #text = result[0]
        cap = f'[{i}]'

        font = ImageFont.truetype(font=font_path, size=15)
        #tx, ty = draw.textsize(cap, font)

        try:
            draw.rectangle([(x, y), (w, h)], 
                            fill=None, 
                            outline='green', 
                            width=1)
            # draw.rectangle([(w, y-ty), (w+tx, y)], 
            #                 fill=None,
            #                 outline=None)
        except:
            pass
        draw.text((w+5, y), cap, fill='green', font=font)

        i += 1
    
    return(image)

class ComputerVision:
    def __init__(self, subscription_key, endpoint, image_path):
        self.loca_image_path = image_path

        ## 参考:https://qiita.com/hedgehoCrow/items/2fd56ebea463e7fc0f5b
        # dotenv_path = join(os.getcwd(), '.env')
        # load_dotenv(dotenv_path)
        # API_KEY = os.environ.get("API_KEY")
        # ENDPOINT = os.environ.get("ENDPOINT")

        self.computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    def visionOCR(self):
        local_image_path = self.loca_image_path
        local_image = open(local_image_path, "rb")

        print("===== Read File - local =====")
        # Call API with URL and raw response (allows you to get the operation location)
        read_response = self.computervision_client.read_in_stream(local_image,  raw=True)

        # Get the operation location (URL with an ID at the end) from the response
        read_operation_location = read_response.headers["Operation-Location"]
        # Grab the ID from the URL
        operation_id = read_operation_location.split("/")[-1]

        # Call the "GET" API and wait for it to retrieve the results 
        while True:
            read_result = self.computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        # Print the detected text, line by line
        result_list = []
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    result_list.append([line.text, line.bounding_box])
        print()

        '''
        END - Read File - local
        '''

        print("End of Computer Vision.")

        return result_list