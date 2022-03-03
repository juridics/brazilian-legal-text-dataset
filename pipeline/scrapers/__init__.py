from .cjf import CjfThesaurusScraper
from .planalto import PlanaltoLawScraper
from .puc import PucEnciclopediaJuridicaScraper
from .stf import StfSumulaScraper, StfIudiciumScraper
from .stj import StjPesquisaProntaScraper
from .pjerj import PjerjPesquisaProntaScrapper
from .fgv import FgvLivrosDigitais

mlm_scrapers = [CjfThesaurusScraper(), PlanaltoLawScraper(), PucEnciclopediaJuridicaScraper(),
                StfSumulaScraper(), StfIudiciumScraper()]


# sts_scrapers = [FgvLivrosDigitais(), PjerjPesquisaProntaScrapper(), StjPesquisaProntaScraper()]
sts_scrapers = [FgvLivrosDigitais()]
