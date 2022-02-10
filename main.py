import paper_scraper as ps

def scrape_pdf_paper(category, subject_code, years, mark_scheme=False):
    years = [str(x) for x in years]
    seasons = ["summer"]
    time_zones = ["1"]
    past_paper = ps.PDFPaper(category=category, subject_code=subject_code, year=years[0])
    past_paper.subject = ps.subject_finder(past_paper)
    print(past_paper.subject)
    past_paper.paper_count = ps.scan_papers(past_paper)
    ps.multi_choice_ans_finder()


if __name__ == '__main__':
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    years = [2015]
    scrape_pdf_paper(category="A%20Levels", subject_code="9702", years=[2020], mark_scheme=True)
