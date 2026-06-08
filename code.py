import requests, json, time, uuid, hashlib, os, oss2, mimetypes, math
from datetime import datetime, timezone

session = requests.Session()

def login(email, passwd):
	
	headers = {
	
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
		'Accept': 'application/json, text/plain, */*',
		'Accept-Language': 'en-US,en;q=0.9',
		'Accept-Encoding': 'gzip, deflate, br, zstd',
		'Referer': 'https://chat.qwen.ai/auth',
		'Content-Type': 'application/json',
		'Version': '0.2.63',
		'source': 'web',
		'X-Request-Id': str(uuid.uuid4()),
		'Timezone': datetime.now(timezone.utc).strftime(f'%a %b %d %Y %H:%M:%S GMT{datetime.now(timezone.utc).strftime("%z")}'),
		'bx-v': '2.5.36',
		'Origin': 'https://chat.qwen.ai',
		'Connection': 'keep-alive',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin',
		'Priority': 'u=4'
	}
	
	pass_hash = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
	
	payload = {
		"email":email,
		"password":pass_hash
	}
	
	url = "https://chat.qwen.ai/api/v2/auths/signin"
	
	resp = session.post(url, headers=headers, json=payload)
	
	
	
	if resp.status_code == 200:
		data = resp.json()
		if data and data.get('success'):
			return True
	
	return False
	
def createChat():
	
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
		'Accept': 'application/json, text/plain, */*',
		'Accept-Language': 'en-US,en;q=0.9',
		'Accept-Encoding': 'gzip, deflate, br, zstd',
		'Referer': 'https://chat.qwen.ai/c/new-chat',
		'Content-Type': 'application/json',
		'Version': '0.2.63',
		'source': 'web',
		'X-Request-Id': str(uuid.uuid4()),
		'Timezone': datetime.now(timezone.utc).strftime(f'%a %b %d %Y %H:%M:%S GMT{datetime.now(timezone.utc).strftime("%z")}'),
		'bx-v': '2.5.36',
		'Origin': 'https://chat.qwen.ai',
		'Connection': 'keep-alive',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin',
		'Priority': 'u=0'
	}
	
	payload = {
		"title":"New Chat",
		"models":["qwen3.7-plus"],
		"chat_mode":"normal",
		"chat_type":"t2t",
		"timestamp":int(time.time()) * 1000,
		"project_id":""
	}
	
	
	url = "https://chat.qwen.ai/api/v2/chats/new"
	resp = session.post(url, headers=headers, json=payload)
	
	if resp.status_code != 200:
		return None
	
	data = resp.json()
	
	if data and data.get('success'):
		new_id = data['data']['id']
		#print(new_id)
		return new_id
	return None


def getSTS(name):
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
		'Accept': 'application/json, text/plain, */*',
		'Accept-Language': 'en-US,en;q=0.9',
		'Accept-Encoding': 'gzip, deflate, br, zstd',
		'Referer': 'https://chat.qwen.ai/c/1633df7b-604f-43e3-851f-5eb0ca2dc7cf',
		'Content-Type': 'application/json',
		'Version': '0.2.63',
		'source': 'web',
		'X-Request-Id': str(uuid.uuid4()),
		'Timezone': datetime.now(timezone.utc).strftime(f'%a %b %d %Y %H:%M:%S GMT{datetime.now(timezone.utc).strftime("%z")}'),
		'bx-v': '2.5.36',
		'Origin': 'https://chat.qwen.ai',
		'Connection': 'keep-alive',
		#'Cookie': token,
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin'
	}
	
	
	
	payload = {
		"filename":os.path.basename(name),	#"Untitled.png",
		"filesize":str(os.path.getsize(name)),	#"837",
		"filetype":"image" if name.lower().endswith(('.png','.jpg','.jpeg','.gif','.bmp','.webp')) else "file"
	}
	
	url = "https://chat.qwen.ai/api/v2/files/getstsToken"
	
	resp = session.post(url, headers = headers, json = payload)
	
	if resp.status_code != 200:
		return None
	
	data = resp.json()
	
	if data and data.get('data'):
		return data.get('data')
	else:
		return None

def sendSTS(newToken,name):
	auth = oss2.StsAuth(newToken.get('access_key_id'), newToken.get('access_key_secret'), newToken.get('security_token'))	
	bucket = oss2.Bucket(auth, f"https://{newToken.get('endpoint')}", newToken.get('bucketname'))
	if os.path.getsize(name) <= 5*1024*1024:

		
		with open(name, 'rb') as f:
			resp = bucket.put_object(newToken.get('file_path'),f, headers = {'Content-Type': mimetypes.guess_type(name)[0] or 'application/octet-stream'})
			if resp.status == 200:
				return True
			return False
	else:
		upload_id = bucket.init_multipart_upload(newToken.get('file_path')).upload_id
		parts = []
		with open(name,'rb') as f:
			for i in range(1, math.ceil(os.path.getsize(name)/ (5*1024*1024)) + 1):
				chunk = f.read(5*1024*1024)
				if not chunk: break
				etag = bucket.upload_part(newToken.get('file_path'), upload_id, i, chunk).etag
				parts.append(oss2.models.PartInfo(i, etag))
		bucket.complete_multipart_upload(newToken.get('file_path'),upload_id,parts)
		return True
		
	

def sendMessage(msg, chat_id, parent_id, files = None):
	
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
		'Accept': 'application/json',
		'Accept-Language': 'en-US,en;q=0.9',
		'Accept-Encoding': 'gzip, deflate, br, zstd',
		'Referer': 'https://chat.qwen.ai/c/' + chat_id,
		'X-Accel-Buffering': 'no',
		'X-Request-Id': str(uuid.uuid4()),
		'Content-Type': 'application/json',
		'Version': '0.2.63',
		'source': 'web',
		'Timezone': datetime.now(timezone.utc).strftime(f'%a %b %d %Y %H:%M:%S GMT{datetime.now(timezone.utc).strftime("%z")}'),
		'bx-v': '2.5.36',
		'Origin': 'https://chat.qwen.ai',
		'Connection': 'keep-alive',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin',
		'Priority': 'u=0'
	}
	
	fid = str(uuid.uuid4())
	child = str(uuid.uuid4())
	
	
	payload = {
		"stream":True,
		"version":"2.1",
		"incremental_output":True,
		"chat_id":chat_id,
		"chat_mode":"normal",
		"model":"qwen3.7-plus",
		"parent_id":parent_id,
		"messages":[{
			"fid":fid,
			"parentId":parent_id,
			"childrenIds":[child],
			"role":"user",
			"content":msg,
			"user_action":"chat",
			"files":[],
			"timestamp":int(time.time()),
			"models":["qwen3.7-plus"],
			"chat_type":"t2t",
			"feature_config":{
				"thinking_enabled":True,
				"output_schema":"phase",
				"research_mode":"normal",
				"auto_thinking":True,
				"thinking_mode":"Auto",
				"thinking_format":"summary",
				"auto_search":True
			},
			"extra":{
				"meta":{"subChatType":"t2t"}
			},
			"sub_chat_type":"t2t",
			"parent_id":parent_id,
		}],
		"timestamp":int(time.time())
	}
	
	if files:
		for i in range(len(files)):
			
			newToken = getSTS(files[i])
			
			if not newToken:
				continue
			
			status = sendSTS(newToken,files[i])
			
			if not status:
				continue
			
			payload['messages'][0]['files'].append({
				"type": "image" if files[i].lower().endswith(('.png','.jpg','.jpeg','.gif','.bmp','.webp')) else "file",
				"id": str(uuid.uuid4()),
				"url": newToken.get('file_url'),
				"name": os.path.basename(files[i]),
				"status": "uploaded",
				"size": os.path.getsize(files[i]),
				"file_type": mimetypes.guess_type(files[i])[0]
			})
			
	
	url = f"https://chat.qwen.ai/api/v2/chat/completions?chat_id={chat_id}"
	resp = session.post(url, headers=headers, json=payload)
	
	text = []
	
	chunk = {}
	
	for line in resp.iter_lines(decode_unicode = True, chunk_size = 1):
		if not line or not line.startswith('data:'):
			continue
		
		data = line.split('data:',1)[1].strip()
		
		if data == '[DONE]':
			break
		
		try:
			chunk = json.loads(data)
			
			choices = chunk.get('choices',[])
			if choices:
				content = choices[0].get('delta',{}).get('content')
				phase = choices[0].get('delta',{}).get('phase')
				
				if content and phase == 'answer':
					text.append(content)
				
		except json.JSONDecodeError:
			continue
	
	if chunk.get('response_id'):
		response_id = chunk['response_id']
	#else:
	#	response_id = None
	
	full_text = ''.join(text)
	return response_id, full_text
		
		
	
if login("",""):
	print("successfully loggen in")

new_id = createChat()
if new_id:
	print(f"successfully created new chat. chat_id = {new_id}")

#newtoken = getSTS("Untitled.png")
#print(newtoken.get('access_key_id') + '\n' + newtoken.get('access_key_secret') + '\n' + newtoken.get('security_token') + '\n' + newtoken.get('file_url'))


parent_id = None

#while True:
#	print(parent_id)
msg = "testing my programm"	#input(" msg> ").strip()
parent_id, full_text = sendMessage(msg,new_id,parent_id)


#	print('\n' + full_text + '\n' + '-' * 100 + '\n')


