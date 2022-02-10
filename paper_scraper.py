import requests
from pathlib import Path
import PyPDF2
import os
import tabula

class PDFPaper(object):
    def __init__(self, category="", subject_code="", year="", season="", time_zone="", paper="", mark_scheme=False):
        self.category = category  # "A Levels", "Cambridge IGCSE"
        self.subject_code = subject_code
        self.subject = ""
        self.year = year
        self.season = season  # "summer", "winter"
        self.time_zone = time_zone
        self.paper = paper
        self.mark_scheme = mark_scheme
        self.paper_count = ""

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

def multi_choice_ans_finder():
    file = open('test.pdf', 'rb')
    pdf = PyPDF2.PdfFileReader(file)
    text = ""
    ANS = "ABCD"
    answers = {}
    for x in range(1,pdf.numPages):
        pageObj = pdf.getPage(x)
        text += pageObj.extractText()
    file.close()
    
    while not (text[0] == "1" and text[2] in ANS):
        text = text[1:]

    answers[1] = text[2]
    text = text[5:]
    question_num = "2"
    while text[len(question_num)+1] in ANS:
        answers[int(text[:len(question_num)])] = text[len(question_num)+1]
        text = text[len(question_num)+4:]
        question_num = str(int(question_num)+1)
    
    while not (text[:2] == question_num and text[3] in ANS):
        text = text[1:]

    while len(text) > 2 and text[len(question_num)+1] in ANS:
        answers[int(text[:len(question_num)])] = text[len(question_num)+1]
        text = text[len(question_num)+4:]
        question_num = str(int(question_num)+1)

    print(answers)
    for x in range(1, 41):
        print(x, answers[x])

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




