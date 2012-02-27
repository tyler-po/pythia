'''
Created on 29 Jan 2012

@author: george
'''
import nltk, tools.utils
from database.warehouse import WarehouseServer

class Cluster(object):
    '''
    This is a structure responsible for representing a cluster after the 
    clustering has been performed. This class is used by the clusterers.
    '''
    def __init__(self, id, document_dict, top_patterns = None):
        '''
        Id specifies the id of this cluster and document_dict 
        is a dictionary storing all the relevant documents for this
        cluster.
        '''
        self.id = id
        self.document_dict = document_dict
        self.top_patterns = top_patterns
        self.locations = []
        self.persons = []
        self.users = []
        
    def get_documents(self):
        '''
        Returns a dictionary of the documents in the cluster.
        '''
        return self.document_dict
    
    def get_most_frequent_terms(self, N=5):
        '''
        Returns the top N occuring terms in this cluster.
        '''
        if self.top_patterns != None:
            return self.top_patterns
        else:
            corpus = nltk.TextCollection([document.tokens for document in self.document_dict.values()])
            return nltk.FreqDist(corpus).items()[:N]     
    
    def get_size(self):
        '''
        The size of the cluster is defined by the number of its documents.
        '''   
        return len(self.document_dict.keys())
    
    def analyse(self):
        '''
        Analyses the cluster to extract meta-information such as 
        locations, persons, users and relations.
        '''
        text_collection = []
        for document in self.document_dict.values():
            raw = nltk.WordPunctTokenizer().tokenize(document.raw)
            for token in raw:
                if token not in nltk.corpus.stopwords.words('english') and token not in tools.utils.ignorewords:
                    text_collection.append(token)
        tagged_corpus = nltk.pos_tag(text_collection)

        for chunk in nltk.ne_chunk(tagged_corpus): 
            if hasattr(chunk, 'node'):    
                if chunk.node == 'GPE':
                    self.locations.append(' '.join(c[0] for c in chunk.leaves()))
                elif chunk.node == 'PERSON':
                    self.persons.append(' '.join(c[0] for c in chunk.leaves()))
        
    def get_locations(self, N=1):
        '''
        Returns the top N locations mentioned in the docs in this cluster.
        '''
        corpus = nltk.text.TextCollection([self.locations])
        return nltk.FreqDist(corpus).items()[:N]
    
    def get_persons(self, N=1):
        '''
        Returns the top N persons mentioned in the docs in this cluster.
        '''
        corpus = nltk.text.TextCollection([self.persons])
        return nltk.FreqDist(corpus).items()[:N]
    
    def get_authors(self):
        '''
        Returns the authors of the documents that appear in this cluster.
        '''
        ws = WarehouseServer()
        authors = set(ws.get_document_authors(self.document_dict.keys()))
        return list(authors)
    
    def get_relations(self):
        '''
        Returns the main relations detected in this cluster
        '''
        pass
    
    def get_sentiment(self):
        '''
        Returns the sentiment of the cluster
        '''
        pass
        
    def get_collocations(self, n=2, N=5):
        '''
        Returns the top collocations of the cluster corpus 
        based on Jaccard index. The collocations correspond 
        to n-grams and more specifically we limited the options
        to bigrams (n=2) and trigrams (n=3) ( n defaults to 2 ). 
        '''
        corpus = nltk.TextCollection([document.tokens for document in self.document_dict.values()])
        finder = nltk.BigramCollocationFinder.from_words(corpus)
        scorer = nltk.metrics.BigramAssocMeasures.jaccard
        #finder.apply_freq_filter(3)
        finder.apply_word_filter(lambda w:w in nltk.corpus.stopwords.words('english'))
        collocations = finder.nbest(scorer, N)
        
        #print "Cluster",self.id,"collocations:"
        #for collocation in collocations:
            #print ' '.join(str(i) for i in collocation)

class Bicluster(object):
    '''
    A bicluster class. 
    '''
    
    def __init__(self, vector, left=None, right=None, similarity=0.0, id=None):
        '''
        Constructs a bicluster
        '''
        #AbstractClusterer.__init__(self)
        self.left = left
        self.right = right
        self.vector = vector
        self.similarity = similarity
        self.id = id 
        
    def get_height(self):
        '''
        Returns the height of a cluster. Endpoints have a height of 1 and 
        then all other points have height equal to the sum of all their branches.
        '''    
        if self.left == None and self.right == None:
            return 1
        
        return self.left.get_height() + self.right.get_height()
        
    def get_depth(self):
        '''
        Returns the depth of the error.
        '''
        if self.left == None and self.right == None:
            return 0 
        
        return max(self.left.get_depth(), self.right.get_depth()) + self.similarity

    def print_it(self, labels=None, n=0):
        '''
        This method outputs the clusters in a human readable form.
        '''
        # For each new cluster have a small indentation to make it look hierarchical  
        for i in range(n): 
            print ' ',
        if self.id<0:
            # This is a branch
            print '->'
        else:
            # This is an root node
            if labels==None: print self.id
            else: print labels[self.id]
            
        # Recursively traverse the left and right branches
        if self.left!=None: 
            self.left.print_it(labels=labels,n=n+1)
        if self.right!=None: 
            self.right.print_it(labels=labels,n=n+1)