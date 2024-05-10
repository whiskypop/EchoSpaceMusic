import unittest

from django.core.handlers.wsgi import WSGIRequest

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


class MyTestCase(unittest.TestCase):
    message_text = [
        {"role": "system", "content": "你需要扮演为一位情感助手，会用温和的语气和我对话"},
        {"role": "system", "content": "你是一个很善于倾听的人，你总是耐心的倾听我的问题，并耐心的回答我的问题"},
        {"role": "system", "content": "你很擅长总结我们的聊天内容，帮助我理清自己的情感"},
    ]
    response = client.chat.completions.create(\
        model="kaigpt4",\
        messages = message_text, \
        max_tokens = 300, \
        temperature = 0.1 )
    print(response['choices'][0])


if __name__ == '__main__':
    unittest.main()
