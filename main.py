import urllib2
import re
from bs4 import BeautifulSoup

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


class spider(object):

    def __init__(self, query="page rank"):
        self.res = query
        self.url = 'https://scholar.google.ca/scholar?hl=en&btnG=&as_sdt=1%2C5&as_sdtp=&'
        pause = re.compile(r'[\s\t\,\.\'\"\;\:]+')
        query = "q=" + reduce(lambda a, b: a.lower() + '+' + b.lower(), re.split(pause, query) )
        self.url += query
        #print self.url

        #user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        #Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36'
        headers = { 'User-Agent' : user_agent }

        try:
            request = urllib2.Request(self.url,headers = headers)
            response = urllib2.urlopen(request)
            content = response.read().decode('utf-8')
            self.soup = BeautifulSoup(content, 'html.parser')
            cache = { "url" : self.url , "context" : str(self.soup) , "download" : False}

        except urllib2.URLError, e:
            if hasattr(e,"code"):
                print e.code
            if hasattr(e,"reason"):
                print e.reason
            exit(1)

    def getCitedNumber(self):
        cited =  self.soup.find_all('div', 'gs_ri')
        pattern = re.compile(r'<div class="gs_fl">(.*?)</div>')
        pattern1 = re.compile(r'>Cited by (.*?)<')
        for each in  cited:
            #print(each)
            #print '#'
            res = re.findall(pattern, str(each))[0]
            return int(re.findall(pattern1,res)[0])
            break

    def getDownloadUrl(self):
        download =  self.soup.find_all('div', 'gs_md_wp gs_ttss')
        pattern = re.compile(r'href="(.*?)"')

        for each in  download:
            #print each
            #print "Download address: " + self.res
            return re.findall(pattern,str(each))[0]
            break #Only need to find the first one

class miningPDF(object):
    def __init__(self,url):
        self.url = url

    def downloadPDF(self):
        type = self.url.split('.')[-1]
        if type.lower() != "pdf":
            print "this link is not a pdf document"
            return
        f = urllib2.urlopen(self.url)

        with open("temp.pdf", "wb") as code:
            code.write(f.read())
            print "pdf download success"

    def extractPDF(self):
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.converter import TextConverter
        from pdfminer.layout import LAParams
        from pdfminer.pdfpage import PDFPage
        from cStringIO import StringIO

        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = file("temp.pdf", 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()
        fp.close()
        device.close()
        retstr.close()
        text = text[text.rfind("References"):]

        return text

def main():
    print "Please input query:"
    query = "page rank"
    a = spider(query)
    print "This article is cited by : ",
    number = a.getCitedNumber()
    print number
    print "PDF download address : ",
    url = a.getDownloadUrl()
    print url
    b = miningPDF(url)
    print "-----------start downloading PDF--------------"
    b.downloadPDF()
    print "-------------start mining PDF-----------------"
    print b.extractPDF()


if __name__ == "__main__":
    main()
