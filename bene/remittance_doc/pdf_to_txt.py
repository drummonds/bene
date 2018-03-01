"""
Generic PDF to Text converter which works for Fenwick PDF's.

Asummes the file is name.pdf and so the output file is name.txt
"""
from django.core.files import File
from django.core.files.storage import default_storage as storage
import io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


def pdf_to_text(path_name, file_name):
    """path_name directory path file_name = filename"""
        # file_root = f[:-4]+'.txt'
        # filename = FILE_ROOT.child(file_root)
        # if not isfile(filename):
        #     cmd = ('c:/anaconda3/scripts/pdf2txt.py -F0.9 -L0.1 ' +\
        #           '"\\\\slf-nas-lon\\office\\Accounts\\Fenwick\\{}"'.format(f))
        #     text = str(subprocess.check_output("c:/anaconda3/python.exe " + cmd, shell=True), 'utf-8')
        #     with open(filename,'w') as this_file:
        #         this_file.write(text)
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    with storage.open(path_name + '/' + file_name, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                      password=password, caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)
        text = retstr.getvalue()

    with storage.open(path_name + '/'  + file_name[:-4] + '.txt', 'w') as f:
        myfile = File(f)
        myfile.write(text)

    device.close()
    retstr.close()


