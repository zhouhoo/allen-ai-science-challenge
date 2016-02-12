"""
pylucene corpus indexing
"""

import lucene, io, os
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader, IndexReader
from org.apache.lucene.store import SimpleFSDirectory, RAMDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher, Query, ScoreDoc, TopScoreDocCollector
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search.similarities import BM25Similarity

# global variables
# initialize lucene
lucene.initVM()
version = Version.LUCENE_CURRENT  # set lucene version
analyzer = StandardAnalyzer()
index_path = "..\\data\\index\\"
index = SimpleFSDirectory(File(index_path))  # todo
hitsPerPageQ = 20  # keep top 10


def check_lucene_index():
    """

    :return:
    """
    if os.listdir(index_path) == []:
        c_path = "..\\data\\corpus"
        lucene_index(c_path)


def addDoc(w, doc_name, text, file_name):
    """
    add single doc to the index
    :param writer:
    :param doc_name:
    :param text:
    :return:
    """
    doc = Document()
    # TextField: sequence of terms: tokenized
    doc.add(TextField("text", text, Field.Store.YES))
    # StringField: character strings with all punctuation, spacing, and case preserved.
    doc.add(TextField('doc_name', doc_name, Field.Store.YES))
    doc.add(StringField('corpus_name', file_name, Field.Store.YES))
    w.addDocument(doc)


def lucene_index(corpus_main_path):
    """

    :param version:
    :return:
    """
    config = IndexWriterConfig(version, analyzer)
    writer = IndexWriter(index, config)
    for f_name in os.listdir(corpus_main_path):
        document_names, texts = read_file(f_name)
        # add 1 corpus at a time
        for d, t in zip(document_names, texts):
            addDoc(writer, d, t, f_name)
    writer.close()


# todo: add filter : file name
def lucene_retriever(q_string, use_BM25=True):
    """

    :param index:
    :param v:
    :return:
    """
    # escape special characters via escape function
    query = QueryParser(version, 'text', analyzer).parse(QueryParser.escape(q_string))
    # search

    reader = IndexReader.open(index)
    searcher = IndexSearcher(reader)

    if use_BM25:
        searcher.setSimilarity(BM25Similarity(k1=1.5, b=0.75))
        #print "Search query: \"{}\" Similarity: BM25".format(q_string)
    #else:
        #print "Search query: \"{}\" Similarity: Default".format(q_string)
    collector = TopScoreDocCollector.create(hitsPerPageQ, True)
    searcher.search(query, collector)
    hs = collector.topDocs().scoreDocs  # hists

    def sorted_doc(hists):
        """return sorted document+score by score"""

        def doc_score(hists):
            """return doc_name & score"""
            for h in hists:
                docID = h.doc
                doc = searcher.doc(docID)
                file_name = doc.get("corpus_name")
                doc_name = doc.get("doc_name")
                text = doc.get("text")
                score = h.score
                yield (file_name, doc_name, score, text)
        return sorted(doc_score(hists), key=lambda tup: tup[2], reverse=True)
    results = sorted_doc(hs)
    reader.close()
    return results


def read_file(f_name):
    """

    :param path:
    :return: python list: document_names, texts
    """
    doc_names, tes = [], []
    path = "..\\data\\corpus\\"+f_name
    with io.open(path, mode='r', encoding='utf-8') as f:
        if f_name in ["Wikipedia-20160210171947.xml.txt", "wiki_summary.txt", "wiki_content.txt", "virginia_SOL20Study20Guide.filtered.noquestions.docids.txt", "CK12_Biology.txt.clean", "CK12_chemistry.txt.clean", "CK12_Earth_Science.txt.clean", "CK12_Life_Science.txt.clean","CK-12-Biology-Advanced-Concepts.txt.clean", "CK-12-Biology-Concepts.txt.clean", "CK-12-Biology-Concepts_b.txt.clean", "CK-12-Chemistry-Concepts-Intermediate.txt.clean", "CK-12-Earth-Science-Concepts-For-High-School.txt.clean", "CK-12-Earth-Science-Concepts-For-Middle-School.txt.clean", "CK-12-Life-Science-Concepts-For-Middle-School.txt.clean", "CK-12-Physical-Science-Concepts-For-Middle-School.txt.clean", "CK-12-Physics-Concepts-Intermediate.txt.clean"]:
            #["wiki_summary", "wiki_content", "virginia_SOL20Study20Guide.filtered.noquestions.docids.txt", "CK12_Biology.txt.clean", "CK12_chemistry.txt.clean", "CK12_Earth_Science.txt.clean", "CK12_Life_Science.txt.clean","CK-12-Biology-Advanced-Concepts.txt.clean", "CK-12-Biology-Concepts.txt.clean", "CK-12-Biology-Concepts_b.txt.clean", "CK-12-Chemistry-Concepts-Intermediate.txt.clean", "CK-12-Earth-Science-Concepts-For-High-School.txt.clean", "CK-12-Earth-Science-Concepts-For-Middle-School.txt.clean", "CK-12-Life-Science-Concepts-For-Middle-School.txt.clean", "CK-12-Physical-Science-Concepts-For-Middle-School.txt.clean", "CK-12-Physics-Concepts-Intermediate.txt.clean"]
            # "simplewiki.xml.txt"
            # format: tree.nodes [tab] text \n
            # format: title [tab] text \n
            for line in f:
                line = line.split("\t")
                doc_names.append(line[0])
                tes.append(line[1].strip())
        elif f_name in []:
            #"virginia_SOL_flashcards-science5.filtered.txt"
            # format: text \n
            i = 0
            for line in f:
                dn = "doc"+str(i)
                doc_names.append(dn)
                tes.append(line.strip())
                i += 1
        elif f_name in ["simpleWiktionary-defs-apr30.txt"]:
            # format: word [tab] part of speech [tab] text
            i = 0
            for line in f:
                line = line.split("\t")
                dn = "doc" + str(i)
                doc_names.append(dn)
                tes.append(line[0] + " " + line[1] + " " + line[2].strip())
                i += 1
        elif f_name in ["Science_Dictionary_for_Kids_book_filtered.txt"]:
            # format: word
            #         [tab] explanation
            for line in f:
                if line[0] != "\t":
                    word = line.strip()
                    doc_names.append(word)
                else:
                    explanation = line.strip()
                    tes.append(word + " " + explanation)
    return doc_names, tes





# tree type data
# http://stackoverflow.com/questions/9970193/how-to-store-tree-data-in-a-lucene-solr-elasticsearch-index-or-a-nosql-db