import socket
import ssl

from os import listdir
class URL:
    # http://example.org/index.html
    # file:///path/goes/here

    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]
        
        # if file
        if self.scheme == "file":
            assert url[0] == "/"
            self.file = url
            return
        
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
        if self.scheme == "file":
            try:
                f = open(self.file)
                return f.read()
            except:
                f = listdir(self.file)
                return ', '.join(f)+'\n'
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
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
            
        # now that we have a connection, we make a request to the other server
        request = "GET {} HTTP/1.1\r\n".format(self.path)
        
        headers = {}
        headers['Host'] = self.host
        headers['Connection'] = 'close'
        headers['User-Agent'] = 'concrete/1.0'
        
        for key in headers:
            request += "{}: {}\r\n".format(key, headers[key])
        request += "\r\n" #imp to have two \r\n at the end of req, else computer will keep waiting for it
        
        s.send(request.encode("utf-8")) #imp to encode the text to bytes
        
        response = s.makefile("r", encoding="utf8", newline="\r\n") #makefile returns a file-like object containing everybyte we receive from the server. 
        
        # first line is the status line
        # not checking if server's http version same as ours, a lot of misconfigured servers out there that respond in HTTP 1.1 even when u talk to them in HTTP 1.0
        statusline = response.readline() 
        version, status, explanation = statusline.split(" ", 2)
        
        # after the status line comes the headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
            
            # to see whether response was received in an unusual way
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers
            
            content = response.read()
            s.close()
            return content
        
def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        if not in_tag:
            print(c, end="")
        if c == ">":
            in_tag = False
                
def load(url):
    '''
    Loads html page
    
    Parameters:
        url: URL object
    
    '''
    body = url.request()
    show(body)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = URL(sys.argv[1])  
    else:
        url = URL("file:///home/alisahad/projects/repos/concreteBrowser/startup.txt")
    load(url)


