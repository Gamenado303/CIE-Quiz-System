import paper_scraper as ps

def scrape_pdf_paper(category, subject_code, years, mark_scheme=False):
    years = [str(x) for x in years]
    for year in years:
        pp = ps.PDFPaper(category = category, subject_code = subject_code, year = year)
        pp.subject = ps.subject_finder(pp)
        paper_count = ps.scan_papers(pp)
        for version in paper_count:
            pp.season = version[0]
            pp.paper = version[1]
            pp.time_zone = version[2]
            if pp.paper == "1" and pp.season == "w" and pp.time_zone == "3":
                print(ps.start_mc_paper(pp))
                

if __name__ == '__main__':
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    years = [2020]
    scrape_pdf_paper(category="A%20Levels", subject_code="9702", years=years, mark_scheme=True)
