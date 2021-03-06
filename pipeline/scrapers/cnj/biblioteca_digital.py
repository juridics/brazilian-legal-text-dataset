import logging
import os.path

import requests
from bs4 import BeautifulSoup
from nltk import tokenize

from pipeline.utils import PathUtil, DirectoryUtil, TextUtil, WorkProgress

MAIN_URL = 'https://bibliotecadigital.cnj.jus.br/jspui/browse?'
DOC_PER_PAGE = 100
URLS = []
ORDER_BY = 'ASC'
SORT_BY = 1
SEARCH_TYPE = 'title'
OUTPUT_DIRECTORY_PATH = 'output'
BOOKS_DIRECTORY_PATH = 'books'


class CnjBibliotecaDigitalScraper:
    def __init__(self):
        self.total_page = TotalPage()
        self.search_page = SearchPage()
        self.document_page = DocumentPage()
        self.download_page = DownloadPage()
        self.progess = WorkProgress()
        self.directory_util = DirectoryUtil(OUTPUT_DIRECTORY_PATH)
        self.total = None
        self.current_page = 0
        self.count_page = None
        self.current_content = None
        self.current_filepath = None

    def execute(self):
        self.progess.show('Starting Scrapper CNJ Digital Library execution')
        self.__get_total_found()
        self.progess.show(f'{self.total} books found in {self.count_page} search pages')
        self.__get_urls_from_pages()
        self.__create_temporary_directory()
        self.__download_docs()
        logging.info('Scrapper CNJ Digital Library Digital was successfully completed')

    def __get_total_found(self):
        self.total = self.total_page.execute()
        self.count_page = (self.total // DOC_PER_PAGE) + 1

    def __has_next_page(self):
        return self.current_page < self.count_page

    def __increment_page(self):
        self.current_page += 1

    def __get_urls_from_pages(self):
        self.progess.start(len(self.count_page))
        while self.__has_next_page():
            self.progess.step(f'Starting search on page {self.current_page + 1}')
            self.search_page.execute(self.current_page)
            self.__increment_page()

    def __create_temporary_directory(self):
        if self.directory_util.is_there_directory(BOOKS_DIRECTORY_PATH) is False:
            self.directory_util.create_directory(BOOKS_DIRECTORY_PATH)

    def __download_docs(self):
        self.progess.step('Starting downlaod of digital books found')
        for document in URLS:
            download_url = self.document_page.execute(document['url'])
            if download_url.endswith('.pdf'):
                self.__set_current_file_attributes(download_url, document['titulo'])
                self.__download_file()

    def __set_current_file_attributes(self, url, filename):
        self.current_content = self.download_page.execute(url)
        self.current_filepath = f'{OUTPUT_DIRECTORY_PATH}/{BOOKS_DIRECTORY_PATH}/{filename}.pdf'

    def __download_file(self, ):
        filepath = os.path.join(self.current_filepath)
        directory_to_export = PathUtil.build_path(filepath)
        with open(directory_to_export, 'wb') as file:
            file.write(self.current_content)


class TotalPage:
    def __init__(self):
        self.parser = CnjTotalHtmlParser()
        self.total_found = None

    def execute(self):
        self.__make_request()
        return self.total_found

    def __make_request(self):
        complete_url = f'{MAIN_URL}type={SEARCH_TYPE}&sort_by={SORT_BY}&order={ORDER_BY}&rpp={DOC_PER_PAGE}&etal=0&null=&offset=0'
        response = requests.get(complete_url)
        self.total_found = self.parser.execute(response)


class SearchPage:
    def __init__(self):
        self.parser = CnjSearchHtmlParser()
        self.url = None
        self.urls_found = None

    def execute(self, current_page):
        self.__update_url(current_page)
        self.__make_request()
        self.__append_urls_to_main_list()

    def __update_url(self, current_page):
        offset = current_page * DOC_PER_PAGE
        self.url = f'{MAIN_URL}type={SEARCH_TYPE}&sort_by={SORT_BY}&order={ORDER_BY}&rpp={DOC_PER_PAGE}&etal=0&null=&offset={offset}'

    def __make_request(self):
        response = requests.get(self.url)
        self.urls_found = self.parser.execute(response)

    def __append_urls_to_main_list(self):
        for url in self.urls_found:
            URLS.append(url)


class DocumentPage:
    def __init__(self):
        self.parser = CnjDocumentHtmlParser()
        self.parsed_url = None

    def execute(self, url):
        self.__make_request(url)
        return self.parsed_url

    def __make_request(self, url):
        response = requests.get(url)
        self.parsed_url = self.parser.execute(response)


class DownloadPage:
    def __init__(self):
        self.content = None

    def execute(self, url):
        self.__make_requests(url)
        return self.content

    def __make_requests(self, url):
        self.content = requests.get(url).content


class CnjTotalHtmlParser:
    def __init__(self):
        self.html = None
        self.total = None

    def execute(self, response):
        self.html = BeautifulSoup(response.text, 'html.parser')
        self.__get_total_from_html()
        return int(self.total)

    def __get_total_from_html(self):
        self.total = self.html.find('div', {'class': 'panel-footer text-center'}).text
        self.__remove_alphabetic_charsets()

    def __remove_alphabetic_charsets(self):
        self.total = tokenize.word_tokenize(self.total)
        new_numbers = []
        for splited_word in self.total:
            if splited_word.isdigit() is True:
                new_numbers.append(splited_word)
        self.total = new_numbers[-1]


class CnjSearchHtmlParser:
    def __init__(self):
        self.html = None
        self.main_url = 'https://bibliotecadigital.cnj.jus.br'

    def execute(self, response):
        self.html = BeautifulSoup(response.text, 'html.parser')
        return self.__get_urls_from_page()

    def __get_urls_from_page(self):
        urls = []
        docs_table = self.html.find('table', {'class': 'table'})
        for index, document in enumerate(docs_table.findAll('tr')):
            if index != 0:
                doc_info = document.find('td', {'headers': 't2'})
                doc_title = TextUtil.slugify(doc_info.text)
                doc_url = doc_info.find('a')['href']
                urls.append({
                    'titulo': doc_title,
                    'url': self.main_url + doc_url
                })
        return urls


class CnjDocumentHtmlParser:
    def __init__(self):
        self.html = None
        self.main_url = 'https://bibliotecadigital.cnj.jus.br'

    def execute(self, response):
        self.html = BeautifulSoup(response.text, 'html.parser')
        return self.__get_download_url_from_page()

    def __get_download_url_from_page(self):
        table_container = self.html.find('table', {'class': 'table panel-body'})
        download_btn = table_container.find('a', {'class': 'btn btn-primary'})['href']
        return self.main_url + download_btn
