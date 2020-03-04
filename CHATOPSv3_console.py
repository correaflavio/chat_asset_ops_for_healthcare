import requests
import json
from webexteamssdk import WebexTeamsAPI


# CHAT BOT v3.0.0
# Integracao Cisco Operations Insights & Webex Teams & CMX
# (c) 2019 
# Flavio Correa
# Joao Peixoto
# Sergio Polizer
# Daniel Vicentini

# infobot
api = WebexTeamsAPI(access_token='')

#########################################################
## FUNCOES


def CriaWebhook():

	# Cria Webhook para receber msg
	
	# Site
	webhook_url="https://enmg7zrdqz1p.x.pipedream.net/"
	
	api.webhooks.create("chatops", webhook_url,"messages","created")

	return

def webexME():
	# detalhes sobre mim
	data = api.people.me()
	return data

def WebexRoomCreate(name):

	# Cria Sala Webex e retorna ID da sala
	api.rooms.create(name)

	# Encontra ID da sala para devolver
	novasala = getwebexRoomID(name)

	return novasala

def WebexRoomDel(name):

	#Remove sala Webex
	api.rooms.delete(name)

	return

def WebexIncUser(sala,mail):

	#Inclui usuario como membro da sala, criando sala caso nao exista
	salaaincluir=getwebexRoomID(sala)

	# Cria sala caso esta nao exista
	if salaaincluir == None:
		salaaincluir = WebexRoomCreate(sala)

	useraincluir=getwebexUserID(mail)

	# inclui usuario caso id encontrado
	if useraincluir !=None:
			#executa a operacao
			api.memberships.create(salaaincluir,useraincluir)

	return

def webexUser(mail):
	# pesquisa ID do usuário e retorna MSG
	usuario = api.people.list(email=mail)
	user=None

	for inter in usuario:
		user = inter.id

	if user !=None:
		resultado = "Usuario "+str(mail)+" ID e' "+user
	else:
		resultado = "Nenhum Usuario encontrado para "+str(mail)

	return resultado

def getwebexUserID(mail):
	# pesquisa ID do usuário; retorna vazio se nao encontrado
	usuario = api.people.list(email=mail)
	user=None

	for x in usuario:
		user = x.id

	if user !=None:
		resultado = user
	
	return resultado


def webexRoomsList():
	# lista salas que pertenco
	rooms=api.rooms.list()
	resultado = ""

	for room in rooms:
		resultado = resultado + "Sala " + str(room.title) + " ID: " + str(room.id)+ "\n"

	return resultado



def getwebexRoomID(sala):

	# Retorna ID da Sala; retorna vazio se nao encontrado
	# Salas que pertenco
	rooms=api.rooms.list()
	salawebex = None

	# for para encontrar ID da sala determinada

	for room in rooms:
		if sala in room.title:
	  		salawebex = room
	  		break

			
	# mandando uma mensagem para a Sala caso encontrada:s
	if salawebex != None:
		resultado = (str(salawebex.id))
	else:
		resultado = salawebex
		
	return resultado

def getwebexMsg(msgID):
	
	# Retorna lista com o texto da mensagem informada, ID da sala e pessoa

	mensagem=api.messages.get(msgID)
				
	return mensagem.text,mensagem.roomId,mensagem.personEmail

def webexmsgRoom(sala,msg):

	# Manda msg para 1 sala especifica
	# salas onde estou
	rooms=api.rooms.list()
	salawebex = None

	salawebex = getwebexRoomID(sala)
			
	# mandando uma mensagem para a Sala caso encontrada:
	if salawebex != None:
		api.messages.create(salawebex,None,None,msg)

	return

def webexmsgAll(msg):
	# mensagem em todas as salas que estou
	#
	rooms=api.rooms.list()

	for room in rooms:
		api.messages.create(room.id,None,None,msg)
	
	return


def OpiCategorySearch(textosearch):

	# Faz uma pesquisa no Operation Insights por Categorias existentes

	# Parte 1 - pede Token para o OPI
	url = "https://opinsights.cisco.com/api/am/v1/auth/license/accesstoken"
	headers = {'Content-type': "application/json" , 'Authorization':'JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRJZCI6MjExLCJ0eXBlIjoiODQzMDc0YjAtMzIwYS0xMWU4LTg0YTctMzkzZWNiNTViY2Q5IiwidXNlck5hbWUiOiJmbGNvcnJlYUBjaXNjby5jb20iLCJpYXQiOjE1NTA4NjI5NTQsImp0aSI6IjQ2YjRiNTIwLTM2ZDYtMTFlOS04OTRmLTI3YTM3MDQ2NWExNCJ9.sNEnOPr45NXNRgx9AyEqU4x9xrt8ra-miRSX2rfH9K4'   }

	# response = valor HTTP (nao usado ainda) e conteudo e' o conteudo de fato, covertendo em json
	response = requests.request("GET", url, headers=headers)
	conteudo=json.loads(response.content)
	# resultado do token
	token='JWT ' + str(conteudo['token'])

	# Parte 2 - Consulta assets usando o Token
	url = "https://opinsights.cisco.com/api/am/v1/entities/access/categories"
	headers = {     'Content-type': "application/json" , 'Authorization': ''+token  }

	# response = valor HTTP (nao usado ainda) e conteudo e' o conteudo de fato, covertendo em json
	response = requests.request("GET", url, headers=headers)
	Jdata=json.loads(response.content)

	# Laco que Faz a pesquisa baseado no grupo do dispositivo da base acima

	# Permite procurar tudo caso esta keyword seja usada
	if textosearch == "tudo":
		textosearch = ""

	resultado = ""
	
	count = 0

	for items in Jdata:

	  msg=""

	  if textosearch in str(items['department']['name']).lower() or textosearch in str(items['name']).lower():
           
		   #constroi saida de texto
			 msg=msg+str("Nome:"+str(items['name'])+". Departamento: "+str(items['department']['name'])+"\n")
			 count=count+1
			 resultado = resultado + msg
		
	resultado = resultado + "\n"+str(count)+" Categorias Encontradas"	

	return resultado


def OpiAssetDetail(textosearch):
	
	# Pesquisa detalhes de um asset

	# Parte 1 - pede Token para o OPI
	url = "https://opinsights.cisco.com/api/am/v1/auth/license/accesstoken"
	headers = {'Content-type': "application/json" , 'Authorization':'JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRJZCI6MjExLCJ0eXBlIjoiODQzMDc0YjAtMzIwYS0xMWU4LTg0YTctMzkzZWNiNTViY2Q5IiwidXNlck5hbWUiOiJmbGNvcnJlYUBjaXNjby5jb20iLCJpYXQiOjE1NTA4NjI5NTQsImp0aSI6IjQ2YjRiNTIwLTM2ZDYtMTFlOS04OTRmLTI3YTM3MDQ2NWExNCJ9.sNEnOPr45NXNRgx9AyEqU4x9xrt8ra-miRSX2rfH9K4'   }

	# response = valor HTTP (nao usado ainda) e conteudo e' o conteudo de fato, covertendo em json
	response = requests.request("GET", url, headers=headers)
	conteudo=json.loads(response.content)
	# resultado do token
	token='JWT ' + str(conteudo['token'])

	# Parte 2 - Consulta assets usando o Token
	url = "https://opinsights.cisco.com/api/am/v1/entities/access/assets"
	headers = {     'Content-type': "application/json" , 'Authorization': ''+token  }

	# response = valor HTTP (nao usado ainda) e conteudo e' o conteudo de fato, covertendo em json
	response = requests.request("GET", url, headers=headers)
	Jdata=json.loads(response.content)


	# Laco que Faz a pesquisa baseado no grupo do dispositivo da base acima

	# Permite procurar tudo caso esta keyword seja usada
	
	msg="Nenhum resultado encontrado"

	for items in Jdata:	
		 
		if textosearch in str(items['serial']).lower():

			msg=""		
			# Caso positivo encontrado monta a resposta
			msg=msg+str("Asset:"+str(items['serial'])+"\n")	
			msg=msg+str("Serial: "+str(items['tags'][0]['serial'])+"\n")
			msg=msg+str("Tipo: "+str(items['tags'][0]['type'])+"\n")
			msg=msg+str("Categoria: "+str(items['category']['name'])+"\n")
			try:
			 zona=str(items['location']['zones'][0]['name'])
			 msg=msg+str("Local: Sala "+str(zona)+"\n")
			except:
			 pass
			 msg=msg+str("Local não encontrado\n")		
			
	resultado=str(msg)			 

	return resultado



def OpiFindAssets(textosearch):
	# Faz uma pesquisa no Operation Insights

	# Parte 1 - pede Token para o OPI
	url = "https://opinsights.cisco.com/api/am/v1/auth/license/accesstoken"
	headers = {'Content-type': "application/json" , 'Authorization':'JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRJZCI6MjExLCJ0eXBlIjoiODQzMDc0YjAtMzIwYS0xMWU4LTg0YTctMzkzZWNiNTViY2Q5IiwidXNlck5hbWUiOiJmbGNvcnJlYUBjaXNjby5jb20iLCJpYXQiOjE1NTA4NjI5NTQsImp0aSI6IjQ2YjRiNTIwLTM2ZDYtMTFlOS04OTRmLTI3YTM3MDQ2NWExNCJ9.sNEnOPr45NXNRgx9AyEqU4x9xrt8ra-miRSX2rfH9K4'   }

	# response = valor HTTP (nao usado ainda) e conteudo e' o conteudo de fato, covertendo em json
	response = requests.request("GET", url, headers=headers)
	conteudo=json.loads(response.content)
	# resultado do token
	token='JWT ' + str(conteudo['token'])

	# Parte 2 - Consulta assets usando o Token
	url = "https://opinsights.cisco.com/api/am/v1/entities/access/assets"
	headers = {     'Content-type': "application/json" , 'Authorization': ''+token  }

	# response = valor HTTP (nao usado ainda) e conteudo e' o conteudo de fato, covertendo em json
	response = requests.request("GET", url, headers=headers)
	Jdata=json.loads(response.content)


	# Laco que Faz a pesquisa baseado no grupo do dispositivo da base acima

	# Permite procurar tudo caso esta keyword seja usada
	if textosearch == "tudo":
		textosearch = ""

	resultado = ""
	
	count = 0

	for items in Jdata:

		msg=""
		 
		if textosearch in str(items['tags'][0]['type']).lower() or textosearch in str(items['category']['name']).lower() or textosearch in str(items['serial']).lower():
		
			count = count +1
						
			# Caso encontrado monta a resposta
			msg=msg+str(str(count)+")Asset:"+str(items['serial'])+" Categoria: "+str(items['category']['name'])+" . ")	
			
			try:
			 zona=str(items['location']['zones'][0]['name'])
			 msg=msg+str("Local: Sala "+str(zona)+"\n")
			except:

			 pass
			 msg=msg+str("Local não encontrado\n")		
			

		
		resultado = resultado + str(msg)

		
	resultado = resultado + "\n"+str(count)+" Assets Encontrados"	

	return resultado




#########################################################
#### CODIGO COMECA AQUI	

# Exemplos:
# Envia mensagem para a primeira sala que tiver o texto ASIC, e Texto e' a msg
# webexmsgRoom('ASIC','Texto')
#====
# Envia msg para todas as salas
# webexmsgAll ('Ola a todos')
#====
# user=webexME()
# webexmsgRoom('ASIC','ID:'+str(user.id))
#====
# pesquisa e apresenta no CMD
# msg  = procura('PACIEN')
# print (msg)
#====
# pesquisa pessoa
#webexmsgRoom('CHATOPS',webexUser('nhaca@nhaca.com'))
#====
# get pessoa e get sala retornas os IDs
#user = getwebexUserID('dvicenti@cisco.com')
#room = getwebexRoomID('CHATOPS')
#====
## Codigo exemplo de aviso, criando a sala e o usuario
#usuario = 'dvicenti@cisco.com'
#novasala = 'CHAT COM '+str(usuario)
#====
# Cria sala e inclui user
#WebexIncUser(novasala,usuario)
#webexmsgRoom(novasala,"Ola "+str(usuario))
#====
# exemplo de aviso
#webexmsgRoom(novasala,"Aviso: " + str(procura('MACA')+" fora de compliance"))
#====
# list salas que pertenco
# salas = webexRoomsList()
# print (salas)
#====
# Cria e deleta sala
#x=WebexRoomCreate("sala teste")
#print (x)
#z=getwebexRoomID("sala teste")
#WebexRoomDel(z)

### LOGICA DAQUI PARA BAIXO

#CriaWebhook()


# Teste 1.0 de Perguntas e respostas
box=""
print("exit para sair. help para comandos de usuario. help+ para comandos Webex")
while box !="exit":
	box=input(">")

	# Converte input para minusculas
	box=box.lower()

	# Splita parametros
	sp=box.split(" ")
	box=sp[0]

	# chamadas de acordo com os parametros
	if box == "help":
		msg="Chatops box 1.0\nComandos disponiveis:\nhelp: esta ajuda\nhelp+: ajuda Webex\nprocura <tudo ou nome>: Procurar Asset\nprintwebex <sala>: envia ultima mensagem no Webex\nexit: sai"
		print (msg)

	if box == "help+":
		msg="Comandos disponiveis:\nuserid <email>: Identifica ID do usuario\nroomid <nome da sala>: Identifica ID da sala\nnovasala <email>: Cria uma sala nova com usuario\nremovesala: Remove sala\nsalas: lista salas que pertenco\n"
		msg=msg+("webhook_create <nome> <url>: cria webhook\nwebhook_del <name>: apaga webhooks com este nome\nwebhook_clean: lista webhooks autuais, apagando os desativos\n")
		msg=msg+("procura <nome ou tudo>: procura onde está o asset\nprocura_categoria <nome ou tudo>: lista categorias do OPI\nasset <nome>: mostra detalhes do asset\n")
		print (msg)

	# chama funcao para procurar OPI somente se ouver 2 parametros
	if box == "procura" and len(sp)>1:
		asset=sp[1]
		msg = OpiFindAssets(asset)
		print (msg)

	# chama funcao para procurar OPI somente se ouver 2 parametros
	if box == "procura_categoria" and len(sp)>1:
		categoria=sp[1]
		msg = OpiCategorySearch(categoria)
		print (msg)

	# chama funcao para procurar OPI somente se ouver 2 parametros
	if box == "asset" and len(sp)>1:
		asset=sp[1]
		msg = OpiAssetDetail(asset)
		print (msg)


	if box == "printwebex":
		sala = input('qual o nome da sala? (todo ou parte):')
		webexmsgRoom(sala,msg)

	# chamada funcao se ouver no minimo 2 parametros
	if box == "userid" and len(sp)>1:
		email=sp[1]
		msg = webexUser(email)
		print (msg)

	# chamada funcao se ouver no minimo 2 parametros
	if box == "roomid" and len(sp)>2:
		sala=sp[1]
		msg = getwebexRoomID(sala)
		print ("ID da sala: " +str(sala)+":"+str(msg))

	# chamada funcao se ouver no minimo 2 parametros
	if box == "novasala" and len(sp)>1:
		email=sp[1]
		novasala=input ('qual o nome da sala?:')
		WebexIncUser(novasala,email)
		webexmsgRoom(novasala,"ola' "+str(email))

	if box == "removesala":
		nome_sala=input('qual o nome da sala?:')
		WebexRoomDel(getwebexRoomID(nome_sala))

	if box =="salas":
		msg = webexRoomsList()
		print (msg)

	# cleaning de webhooks
	# lista webhooks, e apaga os desativados
	if box =="webhook_clean":
		x = api.webhooks.list()
		print ("lista de webhooks:")
		count = 0
		for b in x:

			print ("id: " + str(b.id))
			print ("nome: "+str(b.name))
			print ("status: "+str(b.status))
			# Limpa webhooks desativados
			if (b.status)=='disabled':
				print ("apagando webhook "+str(b.name)+"...")
				api.webhooks.delete(b.id)
			if (b.status)=="active":
				count = count + 1

		print (str(count)+" webhooks ativos")

	# apaga todos os webhooks com <nome> caso nome seja informado
	if box =="webhook_del" and len(sp)>1:
		count = 0
		nome=sp[1]
		x = api.webhooks.list()
		print ("lista de webhooks:")
		count = 0
		for b in x:

			# Limpa webhooks desativados
			if (b.name)==nome:
				print ("apagando webhook... ")
				api.webhooks.delete(b.id)
				count = count + 1
		
		print (str(count)+" webhooks apagados")
					
	# Cria novo webhook para nova sala e nova mensagem
	if box =="webhook_create" and len(sp)>2:
		msgname=sp[1]
		roomname=msgname+"-new"
		webhook_url=sp[2]
		print ("Criando Webhook para mensagens criadas: "+str(msgname))
		api.webhooks.create(msgname, webhook_url,"messages","created")
		print ("Criando Webhook para mensagens criadas: "+str(roomname))
		api.webhooks.create(roomname, webhook_url,"rooms","created")

	if box =="msg":
		# teste com 1 mensage criada
		print(getwebexMsg('Y2lzY29zcGFyazovL3VzL01FU1NBR0UvMWViMmRmNzAtMzk2NS0xMWU5LTg2NmMtYmZmZmQ5NTY5OGVj'))
		
