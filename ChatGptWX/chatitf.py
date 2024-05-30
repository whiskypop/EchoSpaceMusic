import configparser
import json
import requests
import logging
import random

import openai
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from openai.error import ServiceUnavailableError
# config = configparser.ConfigParser()
# config.read('../conf.ini')

# openai.api_key = config['openai']['api_key']

# temperature = 0.5  ## 是否更有创造力 0为没有 1为更加有创造力
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from openai import AzureOpenAI
 
APPID = 'wx7eaaec27cb46c77a'
APPSECRET = 'eb9e2e6c01b1188f3d1067b102360be0'

key = "a80e905335c74fb589144adee45b9920"
key_bytes = key.encode()
# BASE_URL = "https://canadaazureopenai.openai.azure.com/";
 
os.environ["AZURE_OPENAI_KEY"] = key_bytes.decode('utf-8')
client = AzureOpenAI(
  azure_endpoint = "https://canadaazureopenai.openai.azure.com/", 
  api_key=os.environ["AZURE_OPENAI_KEY"], 
  api_version="2024-02-15-preview"
)
message_text = [
    {"role": "system", "content": "你是一位情感引导助手，擅长倾听和总结。"},
    {"role": "system", "content": "你要负责把用户的输入连成一段完整的故事，作为一首歌的故事背景。"}
]
@csrf_exempt
def call_prompt(req) -> HttpResponse:
    try:
        # print("post:{}".format(req.POST))
        # print("get:{}".format(req.GET))
        # print("body:{}".format(req.body))
        # return HttpResponse()
        body = json.loads(req.body)
        user_prompt = body.get('prompt', '')
        message_text.append({"role": "user", "content": user_prompt})
        response = client.chat.completions.create(\
            model="kaigpt4",\
            messages = message_text, \
            max_tokens = 300, \
            temperature = 0.3 )
        print("req:{}, response:{}", req.body, response)
        return HttpResponse(response.choices[0].message.content)
    # except ServiceUnavailableError as suError:
    #     logging.warning(suError)
    #     return HttpResponse("机器人很繁忙，请稍后重试")
    except Exception as e:
        logging.error(e)
        return HttpResponse("机器人很繁忙，请稍后重试")
    return HttpResponse("")

def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'access_token' in data:
            return data['access_token']
        else:
            raise Exception(f"Failed to get access_token: {data}")
    else:
        raise Exception(f"HTTP request failed: {response.status_code}")
    
@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        file_id = data.get('fileID')
        
        try:
            access_token = get_access_token()
            download_url = f"https://api.weixin.qq.com/tcb/batchdownloadfile?access_token={access_token}"
            
            payload = {
                "env": "cloud1-5gmggv5l8f2ead23",
                "file_list": [
                    {
                        "fileid": file_id,
                        "max_age": 7200
                    }
                ]
            }
            
            response = requests.post(download_url, json=payload)
            download_info = response.json()
            # 添加调试语句
            # print("Download info:", download_info)
            if 'file_list' in download_info and download_info['file_list'][0].get('download_url'):
                file_download_url = download_info['file_list'][0]['download_url']
                file_response = requests.get(file_download_url)
                if file_response.status_code == 200:
                    with open('downloaded_image.png', 'wb') as f:
                        f.write(file_response.content)
                    return JsonResponse({"message": "File downloaded successfully"}, status=200)
                else:
                    return JsonResponse({"message": "Failed to download file"}, status=500)
            else:
                return JsonResponse({"message": "Failed to get download URL"}, status=500)
        except Exception as e:
            logging.error(e)
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=400)