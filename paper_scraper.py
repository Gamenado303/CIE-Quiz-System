import requests
from pathlib import Path
import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from pdf2image import convert_from_path
import os
import tabula
#import fitz
from typing import Iterable, Any
from pdfminer.high_level import extract_pages

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
    webpage = response.text.split('\n')[:-15]
    subject = ""
    for line in webpage:
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

def mc_ans_finder(pdf):
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


def mc_questions(pdf, ID):
    url = f"https://papers.gceguide.com/{pdf.category}/{pdf.subject}/{pdf.year}/{pdf.subject_code}_{pdf.season}{pdf.year[-2:]}_qp_{pdf.paper}{pdf.time_zone}.pdf"
    filename = Path("test.pdf")
    response = requests.get(url)
    filename.write_bytes(response.content)
    path = Path('test.pdf').expanduser()
    pages = extract_pages(path)
    qn = [str(i) for i in range(1, 100)]
    qns = {}
    page_num = 0
    question_amount = 0
    for page in pages:
        qns[page_num] = {}
        for textbox in page:
            if textbox.__class__.__name__ == "LTTextBoxHorizontal":
                coords = [int(i) for i in textbox.bbox]
                text = ""
                text = textbox.get_text().strip().split()
                if text and coords[0] < 60:
                    if text[0] in qn:
                        qns[page_num][int(text[0])] = coords
                        question_amount += 1
        page_num += 1
    
    with open("test.pdf", "rb") as in_f:
        input1 = PdfFileReader(in_f)
        page_num = 1
        
        for i in range(1, question_amount+1):
            while i not in qns[page_num]:
                page_num += 1                
            page = input1.getPage(page_num)
            top_right = [595, qns[page_num][i][3]+2]
            if i < question_amount and i+1 in qns[page_num]:
                bot_left = [0, qns[page_num][i+1][3]]
            else:
                bot_left = [0, 50]
            page.mediaBox.lowerLeft = (bot_left[0], bot_left[1])
            page.mediaBox.upperRight = (top_right[0], top_right[1])
            page.cropBox.lowerLeft = (bot_left[0], bot_left[1])
            page.cropBox.upperRight = (top_right[0], top_right[1])
            output = PdfFileWriter()
            output.addPage(page)
            with open(f"{ID}{i}.pdf", "ab") as out_f:
                output.write(out_f)

    os.remove("test.pdf")
    return question_amount

def sa_questions(pdf, ID):
    url = f"https://papers.gceguide.com/{pdf.category}/{pdf.subject}/{pdf.year}/{pdf.subject_code}_{pdf.season}{pdf.year[-2:]}_qp_{pdf.paper}{pdf.time_zone}.pdf"
    filename = Path("test.pdf")
    response = requests.get(url)
    filename.write_bytes(response.content)
    path = Path('test.pdf').expanduser()
    pages = extract_pages(path)
    qn = [str(i) for i in range(1, 100)]
    qns = {}
    page_num = 0
    question_amount = 0
    for page in pages:
        qns[page_num] = {}
        for textbox in page:
            if textbox.__class__.__name__ == "LTTextBoxHorizontal":
                coords = [int(i) for i in textbox.bbox]
                text = ""
                text = textbox.get_text().strip().split()
                if text and coords[0] < 60:
                    if text[0] in qn:
                        qns[page_num][int(text[0])] = coords
                        question_amount += 1
        page_num += 1
    
    with open("test.pdf", "rb") as in_f:
        input1 = PdfFileReader(in_f)
        page_num = 1
        
        for i in range(1, question_amount+1):
            while i not in qns[page_num]:
                page_num += 1                
            page = input1.getPage(page_num)
            top_right = [595, qns[page_num][i][3]+2]
            if i < question_amount and i+1 in qns[page_num]:
                bot_left = [0, qns[page_num][i+1][3]]
            else:
                bot_left = [0, 50]
            page.mediaBox.lowerLeft = (bot_left[0], bot_left[1])
            page.mediaBox.upperRight = (top_right[0], top_right[1])
            page.cropBox.lowerLeft = (bot_left[0], bot_left[1])
            page.cropBox.upperRight = (top_right[0], top_right[1])
            output = PdfFileWriter()
            output.addPage(page)
            with open(f"{ID}{i}.pdf", "ab") as out_f:
                output.write(out_f)

    os.remove("test.pdf")
    return question_amount

    
