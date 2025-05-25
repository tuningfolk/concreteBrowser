# concreteBrowser

## Functionalities
- Parse URL
- Send HTTP/1.1 requests
- Send HTTPS
- receive response and display raw source
- open local file using file:///
- open data:text/plain to display content in url
- can handle redirects
- keep-alive to reuse the same socket for repeated requests to a server
    - socket reuse doesn't seem to receive properly with redirects
- HTML parsing(underway)
    - skip tags(for now)
    - parse special characters \&lt;/\&gt;

    

## History
hypertext: text marked up with hyperlinks to other texts.
W3C: World Wide Web Consortium, founded to provide oversight and standards for web features in 1994.


## Downloading Web Pages
#### content-encoding and transfer-encoding
The Content-Encoding header lets the server compress web pages before sending them. Large, text-heavy web pages compress well, and as a result the page loads faster. The browser needs to send an Accept-Encoding header in its request to list the compression algorithms it supports. Transfer-Encoding is similar and also allows the data to be “chunked”, which many servers seem to use together with compression.

---
How would you explain a search engine to someone from mid 20th century?

A) you have tons and tons of information lying around. a search engine knows enough keywords about each of the pages. when you ask for something, it based on what you asked knows what set of keywords to look for. based on this it goes through the tons of pages matching those keywords and gives it back to you.
