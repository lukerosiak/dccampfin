import re
import csv

plain_re = re.compile(r'([\w\s]+)') #get rid of punctuation
ignore = [' corp',' llc',' inc',' co']
replace = [' suite ', ' ste ']
streets = {' street':' st',' avenue':' av',' ave':' av',' drive':' dr',' boulevard':' blvd',' court':' ct',' place':' pl',' road':' rd'}

def clean_address(s):
	s = s.lower()
	s = ' '.join(re.findall(plain_re,s))
	for word in ignore:
		if s.endswith(word):
			s = s.replace(word,'')
	for word in replace:
		s = s.replace(word,' ')
	for key in streets.keys():
		if key in s: s = s.replace(key,streets[key])
	s = re.sub(r'\s+', ' ', s).strip()
	return s
    
    
def clean_name(s):
    s = s.lower()
    s = ' '.join(re.findall(plain_re,s))
    s = s.replace(' And ',' ')
    s = re.sub(r'\s+', ' ', s).strip()
    titles = ['The ', 'Sen ', 'Rep ', 'Congressman ', 'Congresswoman ', 'Senator ', 'Representative ', 'Hon ', 'Honorable ','Us ', 'Cong ','U S ','United States ','Leadership Pac Of ','Leadership Pac - ', 'Mr ','Mrs ','Ms ','Friends of ']
    for title in titles:
        if s.startswith(title):
            s = s[len(title):]
    suffixes = [x.lower() for x in [' PAC',' Committee',' Cmte',' Campaign',' LLC',' LP',' Co',' Company',' Corp',' Inc']]
    for suffix in suffixes:
        if s.endswith(suffix):
            s = s[:-len(suffix)]     
            
    #change last, first to first last        
    pieces = s.split(', ')
    if len(pieces)==2 and pieces[1].upper() not in ['JR','SS','II','III','IV','INC']:
        s = pieces[1] + ' ' + pieces[0]        
            
    return s
    
