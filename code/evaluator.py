from utils import *
from copy import deepcopy as copy
from extractor import Extractor

class Evaluator( Extractor ) :
	def addTrainingSet( self , testfile ) :
		print testfile
		return 'gg'
	
	def loadmodel( self , modelfile ) :
		self.modelfile = modelfile
		print modelfile
		node = { 'parents' : [] , 'childs' : [] }
		self.network = dict( [ ( field , copy( node ) ) for field in self.fields ] )
		with open( modelfile , 'r' ) as f :
			lines = f.readlines()
			for l in lines :
				sp = l[ :-1 ].split( ':' )
				field = sp[ 0 ]
				childs = [ s for s in sp[ 1 ].split( ',' ) if len( s ) > 0 ]
				for ch in childs :
					self.network[ field ][ 'childs' ].append( ch )
					self.network[ ch ][ 'parents' ].append( field )
		#for field in self.fields :
		#	print "%s: %s" % ( field , self.network[ field ][ 'childs' ] )

	def trainmodel( self ) :
		self.probs = dict( [ ( field , {} ) for field in self.fields ] )
		for field in self.network :
			implies = [ field ]
			condition = [ f for f in self.network[ field ][ 'parents' ] ]
			self.calculateprobabilities( implies , condition )

	def testmodel( self ) :
		print 'test'
		return 'gg'
	
	def calculateprobabilities( self , implies , condition ) :
		implies = self.evaluate( implies )
		condition = self.evaluate( condition )
		return 'gg'

	def probability( self , implies , condition ) :
		numerator = copy( implies )
		numerator.extend( condition )
		denominator = condition
		print implies
		print condition
		return 'gg'
	
	def bdeuprior( setfields ) :
		prior = 1.0
		for field in setfields :
			tam = ( len( self.stats[ field ] ) if self.fieldtypes[ field ] == LITERAL_FIELD else 2 )
			prior *= tam
		return prior

	def evaluate( self , field , pos = 0 ) :
		return 'gg'
	
	def loadAndTestModel( self , modelfile ) :
		self.loadmodel( modelfile )
		self.trainmodel()
		self.testmodel()
		return 'gg'
	
if __name__ == "__main__" :
	files = [ 'training.csv' ] 
	sources = [ DEFAULT_DATA_DIR + f for f in files ]
	evaluator = Evaluator( sources , savefilter = True , ommit = [ 'fnlgwt' ] , discretize = True )
	evaluator.addTrainingSet( DEFAULT_DATA_DIR + 'test.csv' )
	models = [ DEFAULT_DATA_DIR + f for f in [ 'model1.txt' , 'model2.txt' , 'model3.txt' ] ]
	for mod in models :
		evaluator.loadAndTestModel( mod )
