"""
Reference: 
    Title: "Beautifulsoupでアメリカ国立医学図書館検索サイトから論文タイトルと概要を抽出してみる。"
    URL: https://qiita.com/KAI10102/items/aeb57dd957d94e2bfbf4
    URL: https://www.ncbi.nlm.nih.gov/books/NBK25499/
"""
#!pip3 install beautifulsoup4
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
import time
import datetime
import os


#!pip3 install gensim
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

#!pip3 install spacy
from spacy.lang.en.stop_words import STOP_WORDS


######## Prepare ---------------------------------------------------------------------------

## user-defined parameters
keyword = "atopic dermatitis japanese"
keyword = keyword.replace(" ", "%20")
retmax = 10
"""
retmax:
    Total number of records from the input set to be retrieved, up to a maximum of 10,000. 
    Optionally, for a large set the value of retstart can be iterated while holding retmax constant, 
    thereby downloading the entire set in batches of size retmax.
"""

## fixed parameters
now = str(datetime.datetime.now()).replace(" ", "")
dirName = keyword + "_" + str(retmax) + "_" + now
os.mkdir('./output/' + dirName)
baseURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax={}&term=".format(retmax)
serchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="




######## Define functions ------------------------------------------------------------------------

def get_id_helper(url):
    result = urllib.request.urlopen(url)
    time.sleep(2)
    return result

def get_summary_helper(url):
    result = urllib.request.urlopen(url)
    time.sleep(2)
    return result
  
  
  
def main():
    """ Obtain papers and save them to a file """
    url_id = baseURL + keyword
    result = get_id_helper(url_id)
    soup = BeautifulSoup(result, "html.parser")
    ids = soup.find_all("id")
    
    f = open("./output/" + dirName + "/" + keyword + "_" + now + ".txt","w",encoding="UTF-8")

    for _id in ids:
        serch_url_id = serchURL + _id.text + "&retmode=xml"
        sumresult = get_summary_helper(serch_url_id)
        time.sleep(2)
        summury_soup = BeautifulSoup(sumresult, "html.parser")
        
        title = summury_soup.find("title")
        abstract = summury_soup.find("abstract")
        
        if abstract is None: continue
        
        abstract_text = abstract.text.replace("\n", "")
        
        print("ID:"+_id.text,"TITLE:",title.text)
        header = "ID:"+_id.text+"TITLE:"+title.text
        header = header.replace("\n", "")
        print("ABSTRACT"+abstract_text)
        
        f.write(header)
        f.write(abstract_text)
        f.write("\n")
        
    f.close()

    
    


def recommend(rec_ids):
    """ Obtain recommended papers and save them to a file """
    f = open("./output/" + dirName + "/" + keyword + "_" + "_recommend_" + now + ".txt","w",encoding="UTF-8")
    
    for _id in rec_ids:
        serch_url_id = serchURL + _id + "&retmode=xml"
        sumresult = get_summary_helper(serch_url_id)
        time.sleep(2)
        summury_soup = BeautifulSoup(sumresult, "html.parser")
        
        title = summury_soup.find("title")
        abstract = summury_soup.find("abstract")
        
        if abstract is None: continue
        
        abstract_text = abstract.text
        
        header_id = "ID:"+_id
        header_title = "TITLE:"+title.text
        
        f.write(header_id)
        f.write("\r\n")
        f.write(header_title)
        f.write("\r\n")
        f.write(abstract_text)
        f.write("\r\n\r\n\r\n\r\n\r\n")
        
    f.close()
        
        
######## Obtain papers and save as a file ---------------------------------------------------------------------------

main()



######## Doc2Vec -----------------------------------------------------------------------------

## make a corpus
f = open("./output/" + dirName + "/" + keyword + "_" + now + ".txt","r",encoding="UTF-8")

## create the training data excluding stop words
trainings = [TaggedDocument(words = [w for w in data.split() if w not in STOP_WORDS], tags = [i]) for i,data in enumerate(f)]

## fit a model and save
model = Doc2Vec(documents=trainings, dim=1, vector_size=300, windows=8, min_count=1, workers=4)

## save and load the model
model.save("./output/" + dirName + "/" + "doc2vec_{}.model".format(now))
model = Doc2Vec.load("./output/" + dirName + "/" + "doc2vec_{}.model".format(now))

## show similar docs
model.docvecs.most_similar(0)


## retrieve recommended text ids
rec_ids = []
for result in model.docvecs.most_similar(0):
    print("result", result[0])
    rec_ids.append(trainings[result[0]].words[0].split(":")[1][:-5])

## create recommendation file
recommend(rec_ids)


