import re
import os
import csv
import logging

from dccampfin_settings import years, bulk_dir

logging.basicConfig(filename='errors.log',filemode='w',level=logging.WARNING)


re_head1 = re.compile(r"(\d{1,4})\. Full Name, Mailing Address and Zip Code .*")
re_head2 = re.compile(r"\s+Expenditure This Period\s*")

re_money = re.compile(r"\$([\d,]+\.\d{2})")
re_date = re.compile(r"(\d{2}/\d{2}/\d{4})")
                
col1_begin, col1_end = (0,54)
col2_begin, col2_end = (55,81)
                

class PDFParser():     

    def __init__(self,filename):     
        self.filename = filename            
        self.contribs = []
        self.expends = []      
                

    def split(self):            
        
        schedule = ""
        status = -1
        lines = []
        
        fin = open(self.filename,'r')
        for line in fin:
            
            if line.find("SCHEDULE B")>=0:
                schedule = "EXPENDS"
            elif line.find("SCHEDULE A")>=0:
                schedule = "CONTRIBS"
            elif line.find("SCHEDULE C")>=0 or line.find("SCHEDULE D")>=0 or line.find("SCHEDULE E")>=0:
                schedule = ""
                
            if schedule=="CONTRIBS":

                if len(lines)==10:
                    self.contribs.append(lines)
                    lines = []
                    status = -2
                                
                match_head1 = re_head1.match(line)
                if match_head1:
                    status = 0
                    if len(lines):
                        self.contribs.append(lines)
                        lines = []

                if status>=0:
                    lines.append(line)
                    status+=1
                                                                
               
            elif schedule=="EXPENDS":
                
                if len(lines)==15:
                    self.expends.append(lines)
                    lines = []
                    status = -2

                match_head1 = re_head1.match(line)
                if match_head1:
                    status = 0
                    if len(lines):
                        self.expends.append(lines)
                    lines = []
                        
                if status>=0:
                    lines.append(line)
                    status+=1

                

    def printlines(self): #for testing purposes
        fout = open('contribs.txt','a')
        fout.write(self.filename)
        for i,s in enumerate(self.contribs):
            fout.write('\n%s--------------------------------------------------\n' % i)
            fout.write(str(self.parse_contrib(s)))
            fout.write('\n')
            for line in s:
                fout.write('%s' % line)

        fout = open('expends.txt','a')
        fout.write(self.filename)
        for i,s in enumerate(self.expends):
            fout.write('\n%s--------------------------------------------------\n' % i)
            fout.write(str(self.parse_expend(s)))
            for line in s:
                fout.write('%s' % line)




    def parse_contrib(self,lines):            

        data = {'id':'', 'name': '', 'date': '', 'amount': '', 'contribution_type': '', 'pg': '', 
            'contributor_type': '', 'state': '', 'city': '','zip': '',
            'employer': '', 'occupation': '', 'employer_state': '', 'employer_city': '','employer_zip': '','ytd': '' }
        
        if re_head1.match(lines[0]):
            data['id'] = re_head1.match(lines[0]).groups()[0]
        
        for i,line in enumerate(lines):            
                
            if re_money.search(line):
                amount = re_money.search(line).groups()[0]
                if data['amount']!='':
                    data['ytd'] = amount
                else:
                    data['amount'] = amount
            if re_date.search(line):
                data['date'] = re_date.search(line).groups()[0]
                
            status = i
            
            if status==1:
                data['name'] = line[col1_begin:col1_end].strip()
                data['employer'] = line[col2_begin:col2_end].strip()
            if status==2:
                data['address1'] = line[col1_begin:col1_end].strip() 
                data['employer_address1'] = line[col2_begin:col2_end].strip() 
            if status==3:
                data['address2'] = line[col1_begin:col1_end].strip() 
                data['employer_address2'] = line[col2_begin:col2_end].strip()  
                pieces = data['address2'].split()
                if len(pieces)>2:
                    data['zip'] = pieces[-1]
                    data['state'] = pieces[-2]
                    data['city'] = " ".join(pieces[:-2])
                pieces = data['employer_address2'].split()
                if len(pieces)>2:
                    data['employer_zip'] = pieces[-1]
                    data['employer_state'] = pieces[-2]
                    data['employer_city'] = " ".join(pieces[:-2])

            if "Contributor Type" in line:
                data['contributor_type'] = lines[i+1][col1_begin:col1_end].strip()
            if "Occupation" in line:
                if len(lines)==(i+1):
                    data['occupation']='**PROBLEM**'
                else:
                    data['occupation'] = lines[i+1][col2_begin:col2_end].strip()
            if "Receipt For" in line:
                if len(lines)==(i+1):
                    data['pg']='**PROBLEM**'
                else:
                    data['pg'] = lines[i+1][col1_begin:col1_end].strip()
            if "Contribution Type" in line:
                if len(lines)==(i+1):
                    data['contribution_type']='**PROBLEM**'
                else:
                 data['contribution_type'] = lines[i+1][col2_begin:col2_end].strip()
                                    
                
        return data


    def parse_expend(self,lines):
                      
        data = {'id':'', 'name': '', 'date': '', 'amount': '', 'contribution_type': '', 'pg': '', 
            'purpose': '', 'state': '', 'city': '','zip': '',
            'employer': '', 'occupation': '', 'employer_state': '', 'employer_city': '','employer_zip': '' }
                        
        if re_head1.match(lines[0]):
            data['id'] = re_head1.match(lines[0]).groups()[0]

        for i,line in enumerate(lines):            

            if re_money.search(line):
                amount = re_money.search(line).groups()[0]
                data['amount'] = amount
            if re_date.search(line):
                data['date'] = re_date.search(line).groups()[0]

            status = i
    
        for i,line in enumerate(lines):            
                
            if re_money.search(line):
                data['amount'] = re_money.search(line).groups()[0]
            if re_date.search(line):
                data['date'] = re_date.search(line).groups()[0]
                
            status = i
            
            if status==1:
                data['name'] = line[col1_begin:col1_end].strip()
                data['employer'] = line[col2_begin:col2_end].strip()
            if status==2:
                data['address1'] = line[col1_begin:col1_end].strip() 
                data['employer_address1'] = line[col2_begin:col2_end].strip() 
            if status==3:
                data['address2'] = line[col1_begin:col1_end].strip() 
                data['employer_address2'] = line[col2_begin:col2_end].strip()  
                pieces = data['address2'].split()
                if len(pieces)>2:
                    data['zip'] = pieces[-1]
                    data['state'] = pieces[-2]
                    data['city'] = " ".join(pieces[:-2])
                pieces = data['employer_address2'].split()
                if len(pieces)>2:
                    data['employer_zip'] = pieces[-1]
                    data['employer_state'] = pieces[-2]
                    data['employer_city'] = " ".join(pieces[:-2])

            if "Purpose of Expenditure" in line:
                if len(lines)==(i+1):
                    data['purpose']='**PROBLEM**'
                else:            
                    data['purpose'] = lines[i+1][col1_begin:col1_end].strip()
            if "Occupation" in line:
                if len(lines)==(i+1):
                    data['occupation']='**PROBLEM**'
                else:
                    data['occupation'] = lines[i+1][col2_begin:col2_end].strip()
            if "Expenditure For" in line:
                if len(lines)==(i+1):
                    data['pg']='**PROBLEM**'
                else:
                    data['pg'] = lines[i+1][col1_begin:col1_end].strip()                                    
                
        return data





"""
12. Full Name, Mailing Address and Zip Code                Name and Address of Employer                        Date          Amount of Each
  William Norwind                                          Venable LLP                                                       Contribution This
  406 5th Street SE                                        575 7th Street NW                                                 Period
  Washington DC 20003                                      Washington DC 20004
                                                                                                             10/14/2011              $150.00
  Contributor Type                                         Occupation
  Individual                                               Attorney
  Receipt For                                              Contribution Type                                Aggregate Year-To-date
  Primary Election                                         CH                                               $150.00
 
 
 
           
31. Full Name, Mailing Address and Zip Code                Name and Address of Employer                 Date           Amount of Each
Katherine Stocks                                           Self                                                        Expenditure 
829 Quincy Street NW                                       829 Quincy Street NW                       11/14/2011                            $2,750.00
Washington DC 20011                                        Washington DC 20011

Purpose of Expenditure                                     Occupation
 Consultant                                                 Consultant


Expenditure For:
Primary Election
"""
      
