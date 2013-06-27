# -*- coding: utf-8 -*-
"""
Created on Sun Apr 07 12:19:00 2013

@author: lurker
"""

import re
import sys
import os
# work for self-defined .css style
# there will be a sample css file addon, especially for math
# used for Latex Wordpress
#   declaration of the usage
#   only work under Windows
if len(sys.argv)<2:
    print "USAGE:",sys.argv[0],"[INPUT FILE]"
    sys.exit()
#   declaration of the convert class
class converter:
    def __init__(self, texpath):
        self.context = True
        # if at the end of file
        self.src = os.path.abspath(texpath)
        if not os.path.exists(self.src):
            self.err('Path %s does not exist.'% self.src)
    def err(self,info):
        print info
        sys.exit()
    def output(self):
        self.targetName = os.path.basename(self.src).split(".")[0]
        # get the filename
        self.targetdir = os.path.abspath(".\%s" % self.targetName)
        if not os.path.exists(self.targetdir):
            os.makedirs(self.targetdir)
        self.targetpath = "%s\%s.html" %(self.targetdir,self.targetName)
        self.targetfile = open(self.targetpath,"w")
        # make a file folder and write into the target file 
    def divider(self):
        self.paragraph = []
        self.athead = True
        self.head = open("%s\head.tex" %(self.targetdir),"w")
        self.processing(self.src)
        
    def processing(self,srcpath):
        srcfile = open(srcpath) 
        while True:
            line = srcfile.readline()
            #if on windows, there are '\r', remove them
            line = line.replace("\r","")
            while line.startswith(' '):
                line = line[1:]
            #remove label and ref
            line = re.sub('\\ref\{eq:[0-9]\}','',line)
            line = re.sub('\\label\{eq:[0-9]\}','',line)
            # if empty line, means new paragraph
            #do nothing
            if line.strip().startswith('%'):
                continue
            #comments
            if len(line) ==0:
                self.context = False
                break
            #end of file
            if self.athead == True:
                # at head part.
                line = line.strip()
                if line.startswith('\\documentclass'):
                    # can be some argumetns later
                    self.athead = False
                    self.head.close()
                    #close the head file, stores in head.tex
                else:
                    self.head.write(line+'\n')
                    #write the head of tex file into head.tex
            else:
                #in the context
                if self.context == True:
                    if line.startswith('\\'):
                        if line.startswith('\\title'):
                            self.title = self.findParentheses(line,srcfile)
                            self.targetfile.write("<h2>%s</h2>\n" %self.removeTag(self.title))
                            #make title more accessible
                        elif line.startswith('\\author'):
                            self.author = self.findParentheses(line,srcfile)
                            self.targetfile.write("<h3>%s</h3>\n" %self.author)
                        elif line.startswith('\\date'):
                            self.date = self.findParentheses(line,srcfile)
                            self.targetfile.write("<h4>%s</h4>\n" %self.date)
                        elif line.startswith('\\section'):
                            self.processSection(self.findParentheses(line,srcfile))
                        elif line.startswith('\\subsection'):
                            self.processSubSection(self.findParentheses(line,srcfile))
                        elif line.startswith('\\subsubsection'):
                            self.processSubSubSection(self.findParentheses(line,srcfile))
                        elif line.startswith('\\begin{tabular}'):
                            self.processTable(line,srcfile)
                        elif line.startswith('\\begin{equation}'):
                            self.processEq(line,srcfile)
                        elif line.startswith('\\begin{enumerate}'):
                            self.processEnum(line,srcfile)
                        elif line.startswith('\\begin{itemize}'):
                            self.processItemize(line,srcfile)
                        elif line.startswith('\\begin{document}'):
                            self.processBeginning(line)
                        elif line.startswith('\\end{document}'):
                            self.processEnding(line)
                        elif line.startswith('\\['):
                            self.processFormula(line,srcfile)
                        elif line.startswith('\\begin{theorem}'):
                            self.processTheorem(line,srcfile)
                        elif line.startswith('\\begin{lemma}'):
                            self.processLemma(line,srcfile)
                        elif line.startswith('\\begin{state}'):
                            self.processState(line,srcfile)
                        elif line.startswith('\\begin{definition}'):
                            self.processDef(line,srcfile)
                        elif line.startswith('\\begin{eqnarray}'):
                            self.processEqn(line,srcfile)
                        elif line.startswith('\\begin{eqnarray*}'):
                            self.processEqnast(line,srcfile)
                        elif line.startswith('\\begin{remark}'):
                            self.processRemark(line,srcfile)
                        else:
                            print 'cmd under construction:', line
                    elif line.startswith('$$'):
                            self.processFormula(line,srcfile)
                    else:
                        self.processText(line)
                        
        srcfile.close()        
     
    def findMatch(self,line,srcfile,forematch,aftermatch):
        #match can be any parentheses and $$, $,\[\],\(\)
        if len(line[len(forematch):])>0 and line[len(forematch):].find(aftermatch)>0:
            return line.split(forematch)[1].split(aftermatch)[0]
        else:
            nextline = srcfile.readline()
            line = line + ' ' + nextline
            while nextline.find(aftermatch)==-1:
                nextline = srcfile.readline()
                line = line + nextline
            line = line.replace('\n','')
            while not line.find('  ')==-1:
                line = line.replace('  ',' ')
                #remove redundant spaces
            return line.split(forematch)[1].split(aftermatch)[0]
            
    def findParentheses(self,line,srcfile):
        return self.findMatch(line,srcfile,'{','}')
            
    def processFormula(self,line,srcfile):
        if line.startswith('$$'):
            nline = self.findMatch(line,srcfile,'$$','$$')
            nline = nline.replace('\\begin{tabular}','\\begin{array}').replace('\\end{tabular}','\\end{array}')
            self.targetfile.write('$$!'+nline +'$$'+'\n')
        else:
            nline = self.findMatch(line,srcfile,'\[','\]')
            nline = nline.replace('\\begin{tabular}','\\begin{array}').replace('\\end{tabular}','\\end{array}')
            self.targetfile.write('\['+nline+'\]'+'\n')
            
    def processEq(self,line,srcfile):
        self.targetfile.write('$$!'+ self.findMatch(line,srcfile,'\\begin{equation}','\\end{equation}')+'$$'+'\n')
     
    def processTable(self,line,srcfile):
        line = self.findMatch(line,srcfile,'\\begin{tabular}','\\end{tabular}')
        self.targetfile.write('$$\\begin{array}'+line+'\\end{array}$$'+'\n')
    
    def processEnum(self,line,srcfile):
        self.targetfile.write("<ol>")
        while True:
            line=srcfile.readline()
            if len(line)<=0:break
            if line.strip().startswith("\end{enumerate}"):break
            if line.startswith("\item "):
                self.targetfile.write("<li>%s</li>" % self.removeTag(line[5:]))
                
        self.targetfile.write("</ol>"+'\n')
        
    def processItemize(self,line,srcfile):
        self.targetfile.write("<ol>")
        while True:
            line=srcfile.readline()
            if len(line)<=0:break
            if line.strip().startswith("\end{itemize}"):break
            if line.startswith("\item "):
                self.targetfile.write("<li>%s</li>" % self.removeTag(line[5:]))
        self.targetfile.write("</ol>"+'\n')
        
    def removeTag(self,line):
        line = line.replace('\$','\#').replace('$','$$').replace('\#',' \$ ')
        #processing math mod
       
        #processing fonts
        return line
        #Need more to do
        
    
    def processBeginning(self,line):
        self.targetfile.write('')
        self.context = True
    
    def processEnding(self,line):
        self.targetfile.write('')
        self.context = False
        self.targetfile.close()
        
    def processText(self,line):
        line = line.replace('\$','\#').replace('$','$$').replace('\#',' \$ ').replace('\n\n','\#\#').replace('\n','').replace('\#\#','\n')
        # avoid removing dollar sign instead of the math mod sign
        # modify tags, like \bf as strong by regex
        # TODO      
        
        self.targetfile.write(line)
        self.context = True
        #need more to do, remove format of text, like \bf,\text
    # section class
    def processSection(self,line):
        self.targetfile.write('<h1>%s</h1>\n'% line)
    
    def processSubSection(self,line):
        self.targetfile.write('<h2>%s</h2>\n'% line)
    
    def processSubSubSection(self,line):
        self.targetfile.write('<h3>%s</h3>\n'% line)     
    
    def processTheorem(self,line,srcfile):
        line = self.findMatch(line,srcfile,'\\begin{theorem}','\\end{theorem}')
        line = self.removeTag(line)
        self.targetfile.write("<blockquote class=\"theorem\">"+'<hr>'+line+"</blockquote>\n")
        
        
    def processLemma(self,line,srcfile):
        line = self.findMatch(line,srcfile,'\\begin{lemma}','\\end{lemma}')
        line = self.removeTag(line)
        self.targetfile.write("<blockquote class=\"lemma\">"+'<hr>'+line+"</blockquote>\n")
        
    def processState(self,line,srcfile):
        line = self.findMatch(line,srcfile,'\\begin{state}','\\end{state}')
        line = self.removeTag(line)
        self.targetfile.write("<blockquote class=\"state\">"+'<hr>'+line+"</blockquote>\n")
        
    def processDef(self,line,srcfile):
        line = self.findMatch(line,srcfile,'\\begin{definition}','\\end{definition}')
        line = self.removeTag(line)
        self.targetfile.write("<blockquote class=\"definition\">"+'<hr>'+line+"</blockquote>\n")
        
    def processEqn(self,line,srcfile):
        line = self.findMatch(line,srcfile,'\\begin{eqnarray}','\\end{eqnarray}')
        line = "$$!\\begin{array}"+line + "\\end{array}$$\n"
        self.targetfile.write(line)
    
    def processEqnast(self,line,srcfile):
        line = self.findMatch(line,srcfile,'\\begin{eqnarray*}','\\end{eqnarray*}')
        line = "$$!\\begin{array}"+line + "\\end{array}$$\n"
        self.targetfile.write(line)
        
    def processRemark(self,line,srcfile):
        line = self.findMatch(line,srcfile,'\\begin{remark}','\\end{remark}')
        line = self.removeTag(line)
        self.targetfile.write("<blockquote class=\"remark\">"+'<hr>'+line+"</blockquote>\n")
        
if __name__=="__main__":
    c=converter(sys.argv[1])
    c.output()
    c.divider()
              
