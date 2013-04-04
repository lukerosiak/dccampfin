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
                                

class CSFParser():     

    def __init__(self,filename):     
        self.filename = filename            
        self.contribs = []
        self.expends = []      
        
        self.col1_begin, self.col1_end = (0,54)
        self.col2_begin, self.col2_end = (55,91)
        

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

                if len(lines)==11 or line.startswith('Full Name of Citizen'):
                    if len(lines):
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
                                                                
               
            elif schedule=="EXPENDS" or line.startswith('Full Name of Citizen'):
                
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
        fout = open('csfcontribs.txt','a')
        fout.write(self.filename)
        for i,s in enumerate(self.contribs):
            fout.write('\n%s--------------------------------------------------\n' % i)
            fout.write(str(self.parse_contrib(s)))
            fout.write('\n')
            for line in s:
                fout.write('%s' % line)

        fout = open('csfexpends.txt','a')
        fout.write(self.filename)
        for i,s in enumerate(self.expends):
            fout.write('\n%s--------------------------------------------------\n' % i)
            fout.write(str(self.parse_expend(s)))
            for line in s:
                fout.write('%s' % line)




    def parse_contrib(self,lines):            

        data = {'id':'', 'name': '', 'date': '', 'amount': '', 'contribution_type': '', 'pg': '', 
            'contributor_type': '', 'state': '', 'city': '','zip': '',
            'employer': '', 'occupation': '', 'employer_state': '', 'employer_city': '','employer_zip': '','ytd': '',
            'employer_address1':'','employer_address2':'' }
        
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
                data['name'] = line[self.col1_begin:self.col1_end].strip()
            if status==2:
                data['address1'] = line[self.col1_begin:self.col1_end].strip() 
            if status==3:
                data['address2'] = line[self.col1_begin:self.col1_end].strip() 
                pieces = data['address2'].split()
                if len(pieces)>2:
                    data['zip'] = pieces[-1]
                    data['state'] = pieces[-2]
                    data['city'] = " ".join(pieces[:-2])

            if "Contributor Type" in line:
                data['contributor_type'] = lines[i+1][self.col1_begin:self.col1_end].strip()
            if "Contribution Type" in line:
                if len(lines)==(i+1):
                    data['contribution_type']='**PROBLEM**'
                else:
                 data['contribution_type'] = lines[i+1][self.col2_begin:self.col2_end].strip()

            if "Name of the Employer" in line:
                if len(lines)<=(i+3):
                    data['employer']='**PROBLEM**'
                else:
                    data['employer'] = lines[i+1][self.col2_begin:self.col2_end].strip()
                    data['employer_address1'] = lines[i+2][self.col2_begin:self.col2_end].strip() 
                    data['employer_address2'] = lines[i+3][self.col2_begin:self.col2_end].strip()  
                    pieces = data['employer_address2'].split()
                    if len(pieces)>2:
                        data['employer_zip'] = pieces[-1]
                        data['employer_state'] = pieces[-2]
                        data['employer_city'] = " ".join(pieces[:-2])
                        
            if "Occupation" in line:
                if len(lines)==(i+1):
                    data['occupation']='**PROBLEM**'
                else:
                    data['occupation'] = lines[i+1][self.col2_begin:self.col2_end].strip()
                                    
                
        return data


    def parse_expend(self,lines):
                      
        data = {'id':'', 'name': '', 'date': '', 'amount': '', 'contribution_type': '', 'pg': '', 
            'purpose': '', 'state': '', 'city': '','zip': '',
            'employer': '', 'occupation': '', 'employer_state': '', 'employer_city': '','employer_zip': '' }
                        
        if re_head1.match(lines[0]):
            data['id'] = re_head1.match(lines[0]).groups()[0]
    
        for i,line in enumerate(lines):            
                
            if re_money.search(line):
                data['amount'] = re_money.search(line).groups()[0]
            if re_date.search(line):
                data['date'] = re_date.search(line).groups()[0]
                
            status = i
            
            if status==1:
                data['name'] = line[self.col1_begin:self.col1_end].strip()
                data['employer'] = line[self.col2_begin:self.col2_end].strip()
            if status==2:
                data['address1'] = line[self.col1_begin:self.col1_end].strip() 
                data['employer_address1'] = line[self.col2_begin:self.col2_end].strip() 
            if status==3:
                data['address2'] = line[self.col1_begin:self.col1_end].strip() 
                pieces = data['address2'].split()
                if len(pieces)>2:
                    data['zip'] = pieces[-1]
                    data['state'] = pieces[-2]
                    data['city'] = " ".join(pieces[:-2])

            if not re_head1.match(line) and lines[i][self.col2_begin:self.col2_end].strip()!='':
                data['purpose'] += lines[i][self.col2_begin:self.col2_end].strip() + ' '
                
        return data





"""
1. Full Name, Mailing Address and Zip Code               Contribution Type                                     Date           Amount of Each
    CoStar Group, Inc                                    Check                                                                Receipt This Period
    1331 L Street, NW
    Washington DC 20005
                                                                                                            09/11/2012                     $500.00
Contributor Type
    Corporation
                                                                                                                             Aggregate Year-To-Date
                                                                                                                                           $500.00
42. Full Name, Mailing Address and Zip Code              Contribution Type                                     Date          Amount of Each
    Virginia Ali                                         Check                                                               Receipt This Period
    8345 E. Beach Dr. NW
    Washington DC 20012                                  Name of the Employer
                                                         Ben's Chili Bowl                                   04/06/2011                     $100.00
Contributor Type
    Individual                                           Washington DC
                                                         Occupation                                                      Aggregate Year-To-Date
                                                         Owner                                                                             $100.00




3. Full Name, Mailing Address and Zip Code                        Purpose of Expenditure                Date             Amount of Each
                                                                                                                         Expenditure This Period
Washington Gas                                                    utility asst - Richy
P O Box 830036                                                    Alexander
Baltimore MD 21283                                                                                   09/19/2012                          $100.00

"""
      
