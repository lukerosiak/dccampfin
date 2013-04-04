import os
import csv
import logging

from clean import clean_address, clean_name

from dccampfin_settings import years, bulk_dir                                
from process_pdfs import PDFParser     
from process_csf_pdfs import CSFParser     




contribs_headers = ['id','name_clean', 'name', 'address_clean', 'city', 'state', 'zip', 'date', 'amount', 'ytd', 'contribution_type', 'pg', 'contributor_type', 
        'employer_clean', 'employer', 'occupation', 'employer_address_clean', 'employer_city','employer_state','employer_zip', 
        'address1','address2','employer_address1','employer_address2']

expends_headers = ['id', 'name_clean', 'name', 'address_clean', 'address1', 'address2', 'date', 'amount', 
        'purpose', 'employer_clean','employer','occupation','employer_address_clean','employer_address1','employer_address2']


def format_contrib(row):
    row['name_clean'] = clean_name(row['name'])
    row['employer_clean'] = clean_name(row['employer'])
    row['address_clean'] = clean_address(row['address1'])
    row['employer_address_clean'] = clean_address(row['employer_address1'])
    r = []
    for h in contribs_headers:
        if h not in row.keys():
            r.append('')
        else:
            r.append( row[h] )
    return r
        
def format_expend(row):
    row['name_clean'] = clean_name(row['name'])
    row['employer_clean'] = clean_name(row['employer'])
    row['address_clean'] = clean_address(row['address1'])
    row['employer_address_clean'] = clean_address(row['employer_address1'])
    r = []
    for h in expends_headers:
        if h not in row.keys():
            r.append('')
        else:
            r.append( row[h] )
    return r


def parseAll():
    fin = csv.reader( open('output/pdf_index_newest.csv','r') )
    index_headers = fin.next() #filingtype,page,link,cmte,office,period,year,draft
    fcontribs = csv.writer( open('output/detail_contribs.csv','w') )
    fcontribs.writerow( index_headers + contribs_headers )
    fexpends = csv.writer( open('output/detail_expends.csv','w') )
    fexpends.writerow( index_headers + expends_headers )
    os.chdir(bulk_dir)
    for row in fin:
        url = row[2]
        if url.startswith('/pdf_files'): 
            filename = url.split('/')[-1]
            filename = filename[:-3] + 'txt'
            if not os.path.exists(filename):
                logging.debug('%s doesnt exist!' % filename)
                continue
            if row[0]=='csf': 
                o = CSFParser(filename)
            elif row[0]=='campaign': 
                o = PDFParser(filename)
            o.split()
            #o.printlines() #debugging
            for result in o.contribs:
                fcontribs.writerow( row + format_contrib(o.parse_contrib(result)) )
            for result in o.expends:
                fexpends.writerow( row + format_expend(o.parse_expend(result)) )
                    
                    
                                
parseAll()

