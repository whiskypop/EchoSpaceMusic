from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import sys
import requests
import pyodbc
import uuid
import threading
sys.stdout.reconfigure(encoding='utf-8')
from openai import AzureOpenAI

# Azure SQL Database 配置
server = 'echo-server.database.windows.net'
database = 'echoSpace'
username = 'echoSpace'
password = '3ch0Space'
driver = '{ODBC Driver 18 for SQL Server}'

def get_db_connection():
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    return conn

suno_api_url = "http://localhost:3000/api/custom_generate"
# suno_api_url = "http://SunoApi:3000/api/custom_generate"
# 设置Azure OpenAI的API密钥和端点
key = "a80e905335c74fb589144adee45b9920"
key_bytes = key.encode()
os.environ["AZURE_OPENAI_KEY"] = key_bytes.decode('utf-8')

client = AzureOpenAI(
  azure_endpoint = "https://canadaazureopenai.openai.azure.com/", 
  api_key=os.environ["AZURE_OPENAI_KEY"], 
  api_version="2024-02-15-preview"
)

# @csrf_exempt
# def write_song(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             mood_description = data.get('moodDescription')
#             themes = data.get('themes')
#             music_types = data.get('musicTypes')

#             # 检查必需的数据是否存在
#             if not mood_description or not themes or not music_types:
#                 return JsonResponse({'success': False, 'message': '缺少必要的数据'})

#             # 生成歌词、标签和标题
#             lyrics = generate_lyrics(mood_description, themes, music_types)
#             tags = generate_tags(mood_description, themes, music_types)
#             title = generate_title(mood_description, themes)

#             # 将生成的数据传递给 suno API
#             audio_info = generate_audio(lyrics, tags, title)
            
#             return JsonResponse({
#                 'success': True, 
#                 'message': '数据处理成功', 
#                 'lyrics': lyrics, 
#                 'title': title, 
#                 'tags': tags,
#                 'audio_info': audio_info
#             })
#         except json.JSONDecodeError:
#             return JsonResponse({'success': False, 'message': '无效的JSON数据'})
#     else:
#         return JsonResponse({'success': False, 'message': '仅支持POST请求'})

# 创建任务
def write_song(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mood_description = data.get('moodDescription')
            themes = data.get('themes')
            music_types = data.get('musicTypes')

            if not mood_description or not themes or not music_types:
                return JsonResponse({'success': False, 'message': '缺少必要的数据'})

            job_id = str(uuid.uuid4())
            request_data = json.dumps(data)
            job_status = 'pending'
            response_data = ''

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Jobs (jobID, jobStatus, requestData, responseData) VALUES (?, ?, ?, ?)',
                (job_id, job_status, request_data, response_data)
            )
            conn.commit()
            cursor.close()
            conn.close()

            # 启动后台线程处理任务
            threading.Thread(target=process_task, args=(job_id, mood_description, themes, music_types)).start()

            return JsonResponse({'success': True, 'jobID': job_id})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '无效的JSON数据'})
    else:
        return JsonResponse({'success': False, 'message': '仅支持POST请求'})
    
# 处理任务的后台线程函数
def process_task(job_id, mood_description, themes, music_types):
    # 模拟任务处理
    lyrics = generate_lyrics(mood_description, themes, music_types)
    tags = generate_tags(mood_description, themes, music_types)
    title = generate_title(mood_description, themes)
    audio_info = generate_audio(lyrics, tags, title)

    response_data = json.dumps({
        'lyrics': lyrics, 
        'title': title, 
        'tags': tags,
        'audio_info': audio_info
    })
    job_status = 'done'

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE Jobs SET jobStatus = ?, responseData = ? WHERE jobID = ?',
        (job_status, response_data, job_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

# 查询任务状态
def check_job_status(request, job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT jobStatus, responseData FROM Jobs WHERE jobID = ?', (job_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            job_status, response_data = row
            return JsonResponse({'success': True, 'jobStatus': job_status, 'responseData': response_data})
        else:
            return JsonResponse({'success': False, 'message': '任务不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
def generate_lyrics(mood_description, themes, music_types):
    # 构建歌词生成的 prompt
    prompt = f"描述是: {mood_description}\n主题是: {''.join(themes)}\n音乐风格是: {''.join(music_types)}"
    # print(prompt)
    
    # 调用 Azure OpenAI API 生成歌词
    message_text = [
        {"role": "system", "content": "你是一位才华横溢的歌词创作大师，根据描述,主题和音乐风格整合成一首连贯的歌词,总共不要超过100tokens。"},
        {"role": "user", "content": "请将以下文本片段整合成一首歌的歌词。\n\n" + prompt}
    ]
    response = client.chat.completions.create(
        model="kaigpt4",  # 模型名称
        messages=message_text,
        temperature=0.7,
        max_tokens=400,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    # 获取生成的歌词
    return response.choices[0].message.content

def generate_tags(mood_description, themes, music_types):
    # 生成标签的 prompt
    prompt = f"描述是: {mood_description}\n主题是: {''.join(themes)}\n音乐风格是: {''.join(music_types)}"
    # print(prompt)

    # 调用 Azure OpenAI API 生成标签
    message_text = [
        {"role": "system", "content": "你是一位AI音乐创作助手，负责生成适合你选择的描述，主题和音乐类型的标签。"},
        {"role": "user", "content": "请为以下描述、主题和音乐类型生成适当的标签，请不要生成多余的内容，生成的形式像这样“heartfelt anime”，以空格形式隔开。\n\n" + prompt}
    ]
    response = client.chat.completions.create(
        model="kaigpt4",  # 模型名称
        messages=message_text,
        temperature=0.7,
        max_tokens=50,  # 根据需要调整生成的 tags 长度
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    # 获取生成的标签
    return response.choices[0].message.content

def generate_title(mood_description, themes):
    # 生成标题的 prompt
    # prompt = f"描述是: {mood_description}\n主题是: {''.join(themes)}\n"
    # print(prompt)
    
    # 调用 Azure OpenAI API 生成标题
    message_text = [
        {"role": "system", "content": "你是一位AI音乐创作助手，负责生成适合的一个标题。"},
        {"role": "user", "content": "请根据以下描述和主题生成一个合适的标题，不要生成多余的内容，生成的形式要像这样Rhythm of the World。\n\n" + f"描述是: {mood_description}\n主题是: {''.join(themes)}\n"}
    ]
    response = client.chat.completions.create(
            model="kaigpt4",  # 模型名称
            messages=message_text,
            temperature=0.7,
            max_tokens=50,  # 根据需要调整生成的标题长度
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        # 获取生成的标题
    return response.choices[0].message.content
         
def generate_audio(lyrics, tags, title):
    # 构建请求的数据
    data = {
        "prompt": lyrics,
        "tags": tags,
        "title": title,
        "make_instrumental": True,
        "wait_audio": True
    }

    # 发送 POST 请求到本地 suno API
    try:
        response = requests.post(suno_api_url, json=data)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print("请求失败:", response.status_code, response.text)
            return None
    except Exception as e:
        print("请求出错:", e)
        return None