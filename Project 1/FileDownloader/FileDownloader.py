from socket import *
import sys
import os

serverPort = 80

def sendRequestsInBody(body):
    for i in body.splitlines():
        pass

def createSocket(serverName, serverPort):
    return socket(AF_INET, SOCK_STREAM)

def splitLink(link):
    return link.split("/", 1)

# Create request message
def createGETrequestMessage(directory, serverName):
    return "GET /%s HTTP/1.1\r\nHost:%s\r\n\r\n" % (directory, serverName)

def createHEADrequestMessage(directory, serverName):
    return "HEAD /%s HTTP/1.1\r\nHost: %s\r\n\r\n" % (directory, serverName)

def getBody(message):
    lines = []
    for line in message.splitlines():
        if "www" in line:
            lines.append(line)
    return lines

def getBodyX(head, get):
    return get[len(head):]

def prepareSocket(server_name, request_mes):
    clientSocket = createSocket(server_name, serverPort)
    clientSocket.connect((server_name, serverPort))
    clientSocket.send(request_mes.encode())
    return clientSocket

def download_files(links, upper_endpoint, lower_endpoint):
    responseList = []
    
    for link in links:
        link_data = splitLink(link)
        requestMessageHead = createHEADrequestMessage(link_data[1], link_data[0])
        requestMessageGet = createGETrequestMessage(link_data[1], link_data[0])

        clientSocket = prepareSocket(link_data[0], requestMessageHead)

        responseHead = ""
        while True:
            resp_part = clientSocket.recv(4096)
            if resp_part == b'':
                break
            responseHead += resp_part.decode()
        
        clientSocket.close()

        clientSocket = prepareSocket(link_data[0], requestMessageGet)

        responseGet = ""
        while True:
            resp_part = clientSocket.recv(4096)
            if resp_part == b'':
                break
            responseGet += resp_part.decode()

        print(link_data)
        if "200 OK" in responseHead.splitlines()[0]:
            responseList.append([link, responseHead])
            print(responseGet)
            body = getBodyX(responseHead, responseGet)
            if upper_endpoint != -1 or lower_endpoint != -1:
                if len(body) < lower_endpoint:
                    print("ERROR: The requested file is not requested since the size of the file is smaller than lower endpoint!")
                else:
                    pass
            else:
                save_file(link_data[1], body)  
        else:
            print("ERROR: The requested file (%s) is not found in the server!\r\n" % link + responseHead.splitlines()[0] + "\r\n\r\n")
        clientSocket.close()

    return responseList

def save_file(file_name, body):
    file_name = file_name.replace("/", "")
    f = open(os.path.join(os.getcwd(), file_name), 'w')
    f.write(body)
    f.close()

index_file = ""
endpoints = ""
upper_endpoint = -1
lower_endpoint = -1

for i, arg in enumerate(sys.argv):
    # Index 0 is FileDownloader.py So we start at 1
    if i == 1:
        index_file = arg
    elif i == 2:
        endpoints = arg
        endpoints = endpoints.split("-")
        lower_endpoint = int(endpoints[0])
        upper_endpoint = int(endpoints[1])

index_file = splitLink(index_file)

# Specify server name and server port
serverName = index_file[0]
directory = index_file[1]

# Create client socket
requestMessage = createGETrequestMessage(directory, serverName)
clientSocket = prepareSocket(serverName, requestMessage)
print(requestMessage)

# Send the request
clientSocket.send(requestMessage.encode())

response = clientSocket.recv(4096)

decoded_response = response.decode()

print(decoded_response)

clientSocket.close()

file_count = -1
if "200 OK" in decoded_response.splitlines()[0]:
    file_count = decoded_response.count("www")
    print("There are %d file URLs in the index file.\r\n\r\n" % file_count)
else:
    print("ERROR: The index file is not found!\r\n" + decoded_response.splitlines()[0])
    sys.exit(1)

links = getBody(decoded_response)
responseList = download_files(links, upper_endpoint, lower_endpoint)
