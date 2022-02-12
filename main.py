import paper_scraper as ps

def scrape_pdf_paper(category, subject_code, years, mark_scheme=False):
    years = [str(x) for x in years]
    answers = {"A":0, "B":0, "C":0, "D":0}
    for year in years:
        past_paper = ps.PDFPaper(category = category, subject_code = subject_code, year = year)
        past_paper.subject = ps.subject_finder(past_paper)
        paper_count = ps.scan_papers(past_paper)
        for version in paper_count:
            past_paper.season = version[0]
            past_paper.paper = version[1]
            past_paper.time_zone = version[2]
            if past_paper.paper == "1":
                answer = ps.multi_choice_ans_finder(past_paper)
                for i in range(1,len(answer)):
                    answers[answer[i]] += 1
                    
    print(answers)

if __name__ == '__main__':
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    years = [2020]
    scrape_pdf_paper(category="A%20Levels", subject_code="9702", years=years, mark_scheme=True)
