import socket
import os
import os.path
import time

PORT = 80
HOST = "localhost"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)
print('Host:', HOST)    
print('Serving on port ', PORT)

def MovePage(filename, connector):
    header = "HTTP/1.1 301 Moved Permanently\n"+"Location: /" + filename
             
    print(header)
    if(filename == "404.html"):
        header = 'HTTP/1.1 404 Not Found\n\n'
        file = open('404.html', 'rb')
        content = file.read()
        file.close()
        respone = header.encode('utf-8') + content
    elif(filename == "files.html"):
        header = 'HTTP/1.1 200 OK\n'
        mimetype = 'text/html'
        header += 'Content-Type: ' + str(mimetype) + '\n\n'
        print('Server response: ', header)
        respone = header.encode('utf-8')
        respone += files_html.encode('utf-8')
    else:
        respone = header.encode('utf-8')
    connector.send(respone)
    connector.close()
def readList(folder_name):
    folder_content = '<!doctype html><html lang="en"><head><title>FILES</title><!-- Required meta tags --><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"><link rel="shortcut icon" href="#"></head><body><style type="text/css">table {border-collapse: collapse;}th{font-size: 20px;color: blue;text-decoration: underline;border-bottom: 1px solid black;vertical-align: bottom;padding: 15px;}td{padding: 5px;}.btn-link {border: none;outline: none;background: none;cursor: pointer;color: #0000EE;padding: 0;text-decoration: underline;font-family: inherit;font-size: inherit;}</style><table><tr><th>Name</th><br><th>Last modified</th><th>Size</th><th>Description</th></tr><tr><form action="/info.html" method="GET"><td></i><i class="fa fa-arrow-left"><input class ="btn-link" type="submit" value="[INFO Page]" /></form></tr>'
    listfile = os.listdir(folder_name)
    for i in listfile:
        dir = folder_name + "/"
        dir = dir + i
        day_mode = os.path.getmtime(dir)
        folder_content += '<td><a href="'+dir+'" download>'+i+'</a></td>'
        day_mode2 = time.localtime(day_mode)
        size = os.path.getsize(dir)
        folder_content += '<td>' + str(day_mode2.tm_year) + '-' + str(day_mode2.tm_mon) + '-' + str(
            day_mode2.tm_mday) + ' ' + str(day_mode2.tm_hour) + ':' + str(day_mode2.tm_min) + '</td>'
        folder_content += '<td>' + str(round(size / 1024, 1)) + 'KB</td></tr>'
    return folder_content

checkPwd = False
while True:
    connector, address = server.accept()
    print('Client:',address[0])
    request = connector.recv(1024).decode('utf-8')
    if (request == ""):
        connector.close()
        continue
    string_list = request.split(' ') 
    method = string_list[0]
    file_request = string_list[1]
    print('Client request: ', method, file_request)
    filename = file_request.split('?')[0]
    filename = filename.lstrip('/')
    if (method == 'GET'):
        if(((filename=='info.html'or filename=='files.html')and checkPwd==False) or filename==''):
            filename = 'index.html'
            MovePage(filename, connector)
            continue
        if (filename == 'index.html'):
            checkPwd = False
        if (filename == 'files.html'):
            files_html = readList('download')
            MovePage(filename, connector)
            continue
    elif (method == 'POST'):
        if (filename == 'info.html'):
            pass_and_user = string_list[-1].split('username=')[1]
            username = pass_and_user.split('&password=')[0]
            password = pass_and_user.split('&password=')[1]
            print('Username: ', username)
            print('Password: ', password)
            if (username == 'admin' and password == 'admin'):
                checkPwd = True
                MovePage(filename, connector)
                continue
            else:
                filename = '404.html'
                checkPwd = False
        else:
            MovePage(filename, connector)
            continue
    else:
        connector.close()
        continue
    try:
        if('download/' in filename):
            header = 'HTTP/1.1 200 OK\n'
            header +='Transfer-Encoding: chunked\n\n'
            connector.send(header.encode('utf-8'))
            file = open(filename,'rb') 
            CHUNK_SIZE = 1024
            chunk = file.read(CHUNK_SIZE)
            while chunk:
                content=b''
                chunkSzHex=hex(len(chunk)).replace("0x","")
                content+=chunkSzHex.encode('utf-8')
                content+=b"""\r\n"""
                content+=chunk
                content+=b"""\r\n"""
                connector.send(content)
                chunk=file.read(CHUNK_SIZE)    
            content+=b"""0\r\n
            \r\n"""
            connector.send(content)
            print('Server response: ',header)
            connector.close()  
            file.close()
            continue
        file = open(filename, 'rb')
        content = file.read()
        file.close()
        if (filename == '404.html'):
            MovePage(filename, connector)
            continue
        else:
            header = 'HTTP/1.1 200 OK\n\n'
    except Exception as e:
        header = 'HTTP/1.1 404 Not Found\n\n'
        file2 = open('404.html', 'r')
        content = file2.read()
        file2.close()
        content = content.encode('utf-8')

    print('Server response: ', header)
    response = header.encode('utf-8')
    response += content
    connector.send(response)
    connector.close()

