import urllib2
import re
import csv
import os
from BeautifulSoup import BeautifulSoup

from dccampfin_settings import years, bulk_dir

re_maxpages = re.compile(r"Page (\d+) of (\d+)")

types = {'campaign': 'PCC', 'csf': 'CSS'}

def getpage(soup):
    #* Committee to Elect Yvette M. Alexander | Alexander, Yvette | 1 | January 31st Report | 2010 | Original
    results = []
    
    table = soup.findAll('table')[6]
    for row in table.findAll('tr')[1:]:
        cells = row.findAll('td')
        try:
            link = cells[0].div.font.a['href']
            cmte = cells[0].div.font.a.string
            office = cells[1].text
            period = cells[3].text
            year = cells[4].text
            draft = cells[5].text
        except:
            continue
        results.append( (link,cmte,office,period,year,draft) )
        
    return results


def createindex(fout,filingtype):
    
    code = types[filingtype]
    
    for year in years:
        maxpages = 1
        page = 1
        while page <= maxpages:
            url = "http://ocf.dc.gov/imaging/SearchResult_new.asp?fType=%s&fYear=%s&whichpage=%s" % (code,year,page)
            print url
            html = urllib2.urlopen(url).read()
            if re_maxpages.search(html):
                maxpages = int(re_maxpages.search(html).groups()[1])
            else:
                print "no match"
            soup = BeautifulSoup(html)
            results = getpage(soup)
            for result in results:
                row = [ filingtype, page ] + list(result)
                fout.writerow( row )
            page = page+1


def markamendments():
    headers = ['filingtype','page','link','cmte','office','period','year','draft']
    periods = {}
    fin = csv.DictReader( open('pdf_index.csv','r') )
    fout = csv.writer( open('pdf_index_newest.csv','w') )
    fout.writerow(headers)
    for row in fin: 
        filehash = (row['cmte'],row['period'],row['year'])
        if filehash not in periods.keys():
            periods[filehash] = []
        periods[filehash].append( (row['draft'], row) )
    
    for filehash in periods.keys():
        entries = periods[filehash]
        entries.sort( key = lambda a: a[0], reverse=True)
        if len(entries)>1: #'original' will be first, so use the maximum amendment, which is second
            use = entries[1][1]
        else:
            use = entries[0][1]
        fout.writerow( [use[header] for header in headers] )    
            
            
def download():
    fin = csv.DictReader( open('pdf_index_newest.csv','r') )
    os.chdir(bulk_dir)
    existing = os.listdir('.')
    for row in fin:
        url = row['link']
        filename = url.split('/')[-1]
        if url.startswith('/pdf_files'): #there's a text layer to extract
            if filename not in existing:
                url = 'http://ocf.dc.gov' + url
                os.system("wget %s" % url)
                os.system("pdftotext %s -layout" % filename)




fout = csv.writer( open('output/pdf_index.csv','w') )
fout.writerow(['filingtype','page','link','cmte','office','period','year','draft'])
createindex(fout,'campaign')    #create pdf_index.csv listing each candidate's quarterly reports
createindex(fout,'csf')    #create pdf_index.csv listing each candidate's quarterly reports
markamendments() #create pdf_index_newest.csv, with only reports that are not superceded by an amendment
download() #download each of those and create a corresponding text file



"""
	<tr bgcolor="#E1ECF2">
                      
                      <td height="3" align=left> 
                      
                      
                      <div align="left">
                      <font face="Arial, Helvetica, sans-serif" size="2" color="#000000"> 
                          
								<font face="Arial, Helvetica, sans-serif" size="2" color="red">*</font>
								  	<a href='/pdf_files/EFS_generated/CSS_07_243_3768_O_0_1.pdf' class=red target="_blank">Councilmember Muriel Bowser Constituent Service Fund</a> 
									
                          </font></div>
							</td>
                          
                      
                      <td height="3" > <div align="left"><font face="Arial, Helvetica, sans-serif" size="2" color="#000000"> 
							Bowser, Muriel
                         
                          
                          </font></div></td>
                      
                      <td height="3" > <div align="left"><font face="Arial, Helvetica, sans-serif" size="2" color="#000000"> 
                          1
                          </font></div></td>
                      <td height="3" > <div align="left"><font face="Arial, Helvetica, sans-serif" size="2" color="#000000"> 
                          July 1st Report</font></div></td>
                      
                      <td height="3"  colspan="-2"> <div align="left"><font face="Arial, Helvetica, sans-serif" size="2" color="#000000"> 
                          2007</font></div></td>
					
						<td><font face="Arial, Helvetica, sans-serif" size="2">
							Original
							</font>
						</td>
					

                    </tr>
"""
