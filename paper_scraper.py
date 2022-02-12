import requests
from pathlib import Path
import PyPDF2
import os
import tabula

class PDFPaper(object):
    def __init__(self, category="", subject_code="", year="", season="", time_zone="", paper=""):
        self.category = category  # "A Levels", "Cambridge IGCSE"
        self.subject = ""
        self.subject_code = subject_code
        self.year = year
        self.season = season  # "summer", "winter"
        self.paper = paper
        self.time_zone = time_zone

def subject_finder(pdf):
    session = requests.Session()
    response = session.get(f"https://papers.gceguide.com/{pdf.category}/", headers={'User-Agw': 'Mozilla/5.0'})
    webpage = response.text
    for line in webpage.split('\n'):
        if pdf.subject_code in line:
            subject = line
            index = subject.find(pdf.subject_code)
            for x in range(100):
                if subject[index-x] == "'":
                    lb = index-x
                    break
            subject = subject[:index + 5]
            subject = subject[lb+1:]
            subject = subject.replace(" ", "%20")
            return subject

def scan_papers(pdf):
    if not(pdf.category and pdf.subject and pdf.year):
        print("Not enough info")
        return
    session = requests.Session()
    link = f"https://papers.gceguide.com/{pdf.category}/{pdf.subject}/{pdf.year}/"
    webpage = session.get(link, headers={'User-Agent': 'Mozilla/5.0'}).text
    paper_count = set()
    webpage = webpage.split("'")
    for x in range(len(webpage)-1, -1, -1): # removing those which arent .pdfs or qps
        if len(webpage[x]) > 10:
            if webpage[x][-3:] != "pdf" or webpage[x][-9] != "q":
                webpage.remove(webpage[x])
        else:
            webpage.remove(webpage[x])

    for paper in webpage:
        version = ""
        if ("s" in paper):
            version += "s"
        elif ("w" in paper):
            version += "w"
        elif ("m" in paper):
            version += "m"
        version += paper[-6:-4]
        paper_count.add(version)

    paper_count = list(paper_count)
    return paper_count

def multi_choice_ans_finder(pdf):
    if not(pdf.category and pdf.subject and pdf.year and pdf.season and pdf.time_zone and pdf.paper):
        print("Not enough info")
        return

    url = f"https://papers.gceguide.com/{pdf.category}/{pdf.subject}/{pdf.year}/{pdf.subject_code}_{pdf.season}{pdf.year[-2:]}_ms_{pdf.paper}{pdf.time_zone}.pdf"
    filename = Path("test.pdf")
    response = requests.get(url)
    filename.write_bytes(response.content)
    file = open('test.pdf', 'rb')       
    fileReader = PyPDF2.PdfFileReader(file)
    text = ""
    for x in range(1, fileReader.numPages):
        pageObj = fileReader.getPage(x)
        text += pageObj.extractText()
        
    file.close()
    os.remove("test.pdf")
    
    ANS = "ABCD"
    answers = {}
    question_num = "1"
    blacklist = ["\n", "Cambridge", "International", "AS", pdf.subject_code]
    for x in blacklist:
        text = text.replace(x, "")

    if int(pdf.year) < 2017:
        old = True
    else:
        old = False
    while len(text) > 4:
        indexs = []
        for x in ANS:
            if old:
                index = text.find(" "+question_num+" "+x)
                if index > -1:
                    index += 1
                indexs.append(index)
            else: indexs.append(text.find(question_num+" "+x))
        
        while -1 in indexs:
            indexs.remove(-1)
        indexs.sort()
        if indexs:
            index = indexs[0]
        else:
            break
        
        answers[int(text[index:index+len(question_num)])] = text[index+len(question_num)+1]

        question_num = str(int(question_num)+1)
        if not old:
            text = text[index:]

    return answers

def scrape_paper(self):
    filename = Path('test.pdf')
    url = self.link
    response = requests.get(url)
    filename.write_bytes(response.content)
    file = open('test.pdf', 'rb')
    fileReader = PyPDF2.PdfFileReader(file)
    for x in range(fileReader.numPages):
        pageObj = fileReader.getPage(x)
        print(pageObj.extractText())
        print("-"*100)
    file.close()




