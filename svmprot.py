import sys
import io
import urllib.request as req
from urllib.parse import urlparse

sys.stdout = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

base = "http://bidd2.nus.edu.sg/cgi-bin/svmprot/svmprot.cgi"
email = "luaniel@naver.com"
SVM = "ON"
sequence = "Hello"
job = "test"

url = base+"?sequence="+sequence+"&email="+email+"&SVM="+SVM+"&job="+job

openUrl = req.urlopen(url)

