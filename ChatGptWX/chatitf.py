import configparser
import json
import logging
import random

import openai
from django.http import HttpResponse
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
]
@csrf_exempt
def call_prompt(req) -> HttpResponse:
    try:
        # print("post:{}".format(req.POST))
        # print("get:{}".format(req.GET))
        # print("body:{}".format(req.body))
        # return HttpResponse()
        response = client.chat.completions.create(\
            model="kaigpt4",\
            messages = message_text, \
            max_tokens = 300, \
            temperature = 0.3 )
        print("req:{}, response:{}", req.body, response)
        return HttpResponse(response["choices"][0]["text"])
    except ServiceUnavailableError as suError:
        logging.warning(suError)
        return HttpResponse("机器人很繁忙，请稍后重试")
    except Exception as e:
        logging.error(e)
        return HttpResponse("机器人很繁忙，请稍后重试")
    return HttpResponse("")
