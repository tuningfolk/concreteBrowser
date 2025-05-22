import socket

class URL:
    # http://example.org/index.html 

    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"

        if "/" not in url:
            url = url + "/"
        self.host,url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
        '''
        the URL instance has the host and the path, we can download the web page at that url
        '''

        s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
        # you have the socket
        # now you need the host and a port to connect
        # port depends on the protocol u use, for now 80.

        s.connect((self.host,80))
        # now that we have a connection, we make a request to the other server
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
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
