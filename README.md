Parse the PDFs of the District of Columbia's campaign finance disclosures into CSVs for expenditures and contributions. 

The PDFs include more fields than the supplied CSVs, specifically employment information, to detect bundling and conflict of interest, and payment type (money order?? cash??).

To run, install python, pdftotext and BeautifulSoup, modify the path where all the bulk PDFs and their extracted text files will live in dccampfin_settings.py, modify the set of years you want, and then:


python download_pdfs.py

python create_csvs.py


Your output will be two CSVs: output/detail_contribs.csv and output/detail_expends.csv

If you don't want to run this script, those files as generated 4/4/2013 are in the repo.


By Luke Rosiak of The Washington Times. Please credit me if you use this data. No guarantees as to its accuracy--submit a pull request if you see any errors.
