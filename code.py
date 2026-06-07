import requests, json, time, uuid, hashlib
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
		

def sendMessage(msg, chat_id, parent_id):
	
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
	
	
	payload = {
		"stream":True,
		"version":"2.1",
		"incremental_output":True,
		"chat_id":chat_id,
		"chat_mode":"normal",
		"model":"qwen3.7-plus",
		"parent_id":parent_id,
		"messages":[{
			"fid":"47e5b19d-550d-463f-9126-961b2a982f41",
			"parentId":"52fae2ef-8e35-49a3-b624-9e33db6e6639",
			"childrenIds":["68a724eb-fc2a-4cca-acb9-80aaff4a7da5"],
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
	else
		response_id = None
	
	full_text = ''.join(text)
	return response_id, full_text
		
		
	
	
if login("EMAIL", "PASSWORD"):
	print("successfully loggen in")

new_id = createChat()
if new_id:
	print(f"successfully created new chat. chat_id = {new_id}")
parent_id = None

while True:
	print(parent_id)
	msg = input(" msg> ").strip()
	parent_id, full_text = sendMessage(msg,new_id,parent_id)
	print('\n' + full_text + '\n' + '-' * 100 + '\n')


