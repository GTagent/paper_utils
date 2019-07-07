#!/usr/bin/python

import sys, re, os, errno, requests, urllib
from bs4 import BeautifulSoup

BASEURL = "http://openaccess.thecvf.com/"
BASEAURL="http://openaccess.thecvf.com/menu.py"

linkre = re.compile('([0-9]+)\.pdf')


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def lencheck(element, length=1):
    if len(element) < length:
        raise RuntimeError("parse error %s" % (str(element)))


def get_year_page(year):
    bpreq = requests.get(BASEAURL)
    if not bpreq:
        raise RuntimeError("could not download %s" % (BASEAURL))
    soup = BeautifulSoup(bpreq.text, 'lxml')
    # print(bpreq.text)
    years = soup.findAll(
        u"a", attrs={u"href": re.compile(r'CVPR%i.*' % (year))})
    # workshop_years = soup.findAll(
    #     u"a", attrs={u"href": re.compile(r'.CVPR.*?%i.*' % (year))})
    if len(years) < 1:
        raise RuntimeError("year %i not found" % (year))
    # print(years)
    # print(workshop_years)
    yearurl = BASEURL + years[0][u"href"]
    yearpage = requests.get(yearurl)
    if not yearpage:
        raise RuntimeError("could not download %s" % (yearurl))
    # print(yearurl)
    # print(yearpage.text)
    workshopurl=BASEURL+years[1][u"href"]
    workshoppage=requests.get(workshopurl)
    if not workshoppage:
        raise RuntimeError("could not download workshop %s"% (yearurl))
    # print(workshopurl)
    # print(workshoppage.text)
    return yearpage.text,workshoppage.text


def get_all_papers_on_yearpage(yearpage):
    soup = BeautifulSoup(yearpage, 'lxml')
    links = soup.findAll(u"a")
    # print(links)
    paperre = re.compile(r'(.*?CVPR_([0-9].*)_paper.*html)')
    # print(links)
    results = []
    for l in links:
        if u"href" in l.attrs:
            ret = paperre.match(l[u"href"])
            if ret:
                results.append(ret.groups())
    # print(results)
    return results


def strip_slashes(x):
    return re.sub(r'/', '', x)


def check_dir_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def nameWorkshop(name):
    return name.split("/")[-1]

def download_pdf_from_paperpage(url, saveDir):
    # paperpage = requests.get(BASEURL + url)
    # if not paperpage:
    #     # raise RuntimeError("could not download %s" % (BASEURL + url))
    #     print("could not download %s" % (BASEURL + url))
    #     return 1 

    fnret = re.search(r'.*?CVPR_[0-9].*_paper', url)
    if not fnret:
        # raise RuntimeError("error parsing paper url '%s'" % (url))
        print("error parsing paper url '%s'" % (url))
        return 1

    pdf_dir = os.path.join(saveDir, 'pdf')
    # bib_dir = os.path.join(saveDir, 'bib')

    check_dir_exists(saveDir)
    check_dir_exists(pdf_dir)
    # check_dir_exists(bib_dir)

    basename = fnret.group(0)
    # basename = nameWorkshop(strip_slashes(basename))
    basename = nameWorkshop(basename)
    pdf_file = basename + ".pdf"
    # bib_file = basename + ".bib"

    pdf_file = os.path.join(pdf_dir, pdf_file)
    # bib_file = os.path.join(bib_dir, bib_file)

    # soup = BeautifulSoup(paperpage.text, 'lxml')
    # pdfurls = soup.findAll(u"meta", attrs={u"name": u"citation_pdf_url"})
    # lencheck(pdfurls)
    # pdfurl = pdfurls[0][u"content"]
    pdfurl=url
    # biburls = soup.findAll(u"a", attrs={u"href": re.compile(r'bibtex$')})
    # lencheck(biburls)
    # biburl = BASEURL + biburls[0][u"href"]
    print(" downloading %s ..." % (basename))
    sys.stdout.flush()
    if not os.path.exists(pdf_file):
        try:
            urllib.request.urlretrieve(pdfurl, pdf_file)
        except Exception as e:
            print('downloading error!')
            return 1
    print("pdf")
    sys.stdout.flush()
    # if not os.path.exists(bib_file):
        # urllib.request.urlretrieve(biburl, bib_file)
    # print("bib.")
    # sys.stdout.flush()
    return 0


def download_single_paper(year, paper_number):
    yearpage = get_year_page(year)
    for url, pn in get_all_papers_on_yearpage(yearpage):
        try:
            pn = int(pn)
        except ValueError:
            raise RuntimeError("error parsing yearpage")
        if pn == paper_number:
            download_pdf_from_paperpage(url)
            return
    raise RuntimeError("paper %i not found" % (paper_number))


def download_all_papers(year, mode='cvpr', dmode="cvpr"):
    if mode == 'cvpr':
        baseDir = 'cvpr'
        check_dir_exists(baseDir)
    yearpage, workshoppage = get_year_page(year)
    if dmode=="all" or dmode=="cvpr":
        fail=[]
        for url, paper_number in get_all_papers_on_yearpage(yearpage):
            year_dir = os.path.join(baseDir, '{}'.format(year))
            check_dir_exists(year_dir)
            # main_dir=os.path.join(year_dir,'main')
            main_dir=year_dir
            check_dir_exists(main_dir)
            status=download_pdf_from_paperpage(url, saveDir=main_dir)
            if status == 1:
                fail.append(url)
        print(fail)
    if dmode=="all" or dmode=="workshop":
        for url, paper_number in get_all_papers_on_yearpage(yearpage):
            year_dir = os.path.join(baseDir, '{}'.format(year))
            download_pdf_from_paperpage(url, saveDir=year_dir)


if __name__ == '__main__':
    # year = 2018
    # download_all_papers(year)

    if len(sys.argv) < 2:
        print >>sys.stderr, \
        """usage: %s <year> [paper_number]
       if no paper number is supplied, all of that year
       will be downloaded""" \
                % (sys.argv[0])
        sys.exit(1)

    paper_number = None
    year = None
    if len(sys.argv) >= 2:
        try:
            year = int(sys.argv[1])
        except ValueError:
            print >> sys.stderr, "could not parse year"
            sys.exit(1)
    if len(sys.argv) >= 3:
        try:
            paper_number = int(sys.argv[2])
        except ValueError:
            print >> sys.stderr, "could not parse paper number"
            sys.exit(1)

    print("Downloading from %i proceedings" % (year))
    if paper_number is not None:
        print("paper no. %i" % (paper_number))
        download_single_paper(year, paper_number)
    else:
        print("all papers")
        download_all_papers(year)
