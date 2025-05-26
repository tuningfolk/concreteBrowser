import socket
import ssl

from os import listdir

hosts = {} # maps hostnames to their unclosed sockets
num_redirects = 0
MAX_REDIRECTS = 5

class URL:
    # http://example.org/index.html
    # file:///path/goes/here
    # data:[<media-type>], <data>
    #   <media-type> default text/plain
    #   data:text/plain, hello world!
    #   data:text/html, <b>hello world!</b>
    

    def __init__(self, url):
        self.scheme = None
        self.file = None
        self.content = None
        self.host = None
        self.path = None
        self.port = None

        self.scheme, url = url.split(":", 1)
        assert self.scheme in ["http", "https", "file","data"]
        
        # if file
        if self.scheme == "file":
            assert url[0] == "/"
            self.file = url
            return
        elif self.scheme == "data":
            media_type, content = url.split(",", 1)
            
            # render plaintext same as html for now 
            assert media_type in ["text/plain","text/html"]
            self.content = content
            return
        
        assert url[:2] == "//"
        url = url[2:]
        if "/" not in url:
            url = url + "/"
        self.host,url = url.split("/", 1)
        self.path = "/" + url
            
        hostsplit = self.host.split(":")
        assert len(hostsplit) <= 2
        if len(hostsplit) == 2:
            self.port = int(hostsplit[1])
            self.host = hostsplit[0]
        elif self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
    def request(self):
        '''
        the URL instance has the host and the path, we can download the web page at that url
        '''
        global num_redirects
        if self.scheme == "file":
            try:
                f = open(self.file)
                return f.read()
            except:
                f = listdir(self.file)
                return ', '.join(f)+'\n'
        elif self.scheme == "data":
            return self.content
        if (self.host,self.port) not in hosts:
            s = socket.socket(
                    family=socket.AF_INET,
                    type=socket.SOCK_STREAM,
                    proto=socket.IPPROTO_TCP,
            )
            # you have the socket
            # now you need the host and a port to connect

            s.connect((self.host,self.port))
            if self.scheme == "https":
                #to encrypt connection, you use this function to create a context ctx and use that context to wrap the socket
        #print("content size: ", len(content.encode("utf8")))
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
            hosts[(self.host, self.port)] = s
        else:
            s = hosts[(self.host, self.port)]
        # now that we have a connection, we make a request to the other server
        request = "GET {} HTTP/1.1\r\n".format(self.path)
        
        headers = {}
        headers['Host'] = self.host
        headers['Connection'] = 'keep-alive'
        headers['User-Agent'] = 'concrete/1.0'

        for key in headers:
            request += "{}: {}\r\n".format(key, headers[key])
        request += "\r\n" #imp to have two \r\n at the end of req, else computer will keep waiting for it
        
        s.send(request.encode("utf-8")) #imp to encode the text to bytes
        
        #r instead of rb should work right?
        response = s.makefile("r", encoding="utf8", newline="\r\n") #makefile returns a file-like object containing everybyte we receive from the server. 
        

        # first line is the status line
        # not checking if server's http version same as ours, a lot of misconfigured servers out there that respond in HTTP 1.1 even when u talk to them in HTTP 1.0
        statusline = response.readline()
        
        try:
            version, status, explanation = statusline.split(" ", 2)
        except:
            print("Error: Wrong status line: ",response.read())
            del hosts[(self.host, self.port)]
            return self.request()
        
        # after the status line comes the headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        
        # Redirect!
        if 300<=int(status)<=399:
            if num_redirects > MAX_REDIRECTS:
                    return b'<html>too many redirects</html>'
            num_redirects += 1
            location = response_headers['location']
            print("redirect to location: ", location)
            # Same host, same scheme, different path
            if location[0] == "/":
                self.path = location
                return self.request()
            else:
                url = URL(location)
                return url.request()
        else:
            num_redirects = 0
        

        # to see whether response was received in an unusual way
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        # assert 'content-length' in response_headers
        if 'content_length' not in response_headers:
            content = response.read()
        else:
            content_length_bytes = int(response_headers['content-length'])
            content = response.read(content_length_bytes)
        # s.close()
        return content
        
def show(body):
    in_tag = False
    less_than = "&lt;"
    greater_than = "&gt;"
    amper_string = ""
    
    for c in body:
        if in_tag:
            if c == ">": in_tag = False
        elif c == "<":
            in_tag = True
        elif amper_string + c in ["&","&l","&lt","&lt;","&g","&gt","&gt;"]:
            amper_string += c
            if amper_string == less_than:
                print("<", end="")
                amper_string = ""
            elif amper_string == greater_than:
                print(">", end="")
                amper_string = ""
        elif amper_string!="":
            print(amper_string, end="")
            amper_string = ""
        else:
            print(c,end="")
    
    if amper_string!="":
        print(amper_string, end="")
             
                
def load(url):
    '''
    Loads html page
    
    Parameters:
        url: URL object
    
    '''
    body = url.request()
    #view_source(body)
    show(body)

def view_source(body):
    print(body)

import time

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = URL(sys.argv[1])  
    else:
        url = URL("file:///home/alisahad/projects/repos/concreteBrowser/startup.txt")
    start_time = time.time()
    load(url)
    print("Request time: ", time.time()-start_time)
    load(url)




