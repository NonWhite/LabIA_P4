from utils import *
from copy import deepcopy as copy
from math import log
from extractor import Extractor

class Evaluator( Extractor ) :
	def addTrainingSet( self , testfile ) :
		testdata = Extractor( testfile , ommit = self.ommitedfields )
		print "Adding test rows from %s" % testfile
		try :
			self.testdata.extend( testdata.rows )
		except :
			self.testdata = []
			self.testdata.extend( testdata.rows )
		print "TEST ROWS = %s" % len( self.testdata )
	
	def loadmodel( self , modelfile ) :
		self.modelfile = modelfile
		print "Loading model from %s" % modelfile
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
		# TODO: Get a topological order
		for field in self.network :
			xi = [ field ]
			pa_xi = [ f for f in self.network[ field ][ 'parents' ] ]
			self.calculateprobabilities( xi , pa_xi )

	# DATA LOG_LIKELIHODD
	def testmodel( self ) :
		print "Testing model with test data"
		loglikelihood = 0.0
		for row in self.testdata :
			for field in self.fields :
				xi = { field: row[ field ] }
				pa_xi = dict( [ ( pai , row[ pai ] ) for pai in self.network[ field ][ 'parents' ] ] )
				prob = self.conditional_prob( xi , pa_xi )
				loglikelihood += log( prob )
		print "Data Log-Likelihood = %s" % loglikelihood
		return loglikelihood
	
	def calculateprobabilities( self , xsetfield , ysetfield ) :
		implies = self.evaluate( xsetfield )
		condition = self.evaluate( ysetfield )
		print "Calculating P( %s | %s )" % ( xsetfield , ysetfield )
		self.cont = 0
		for xdict in implies :
			xkey = xdict.keys()[ 0 ] # Supose it only has one field in X
			xval = xdict[ xkey ] 
			if xval not in self.probs[ xkey ] : self.probs[ xkey ][ xval ] = {}
			if not condition :
				self.probs[ xkey ][ xval ][ str( {} ) ] = self.conditional_prob( xdict , {} )
				#self.probs[ xkey ][ xval ].append( [ [] , self.conditional_prob( xdict , {} ) ] )
				continue
			for y in condition :
				self.probs[ xkey ][ xval ][ str( y ) ] = self.conditional_prob( xdict , y )
				#self.probs[ xkey ][ xval ].append( [ y , self.conditional_prob( xdict , y ) ] )
		print "CONT = %s" % self.cont

	def conditional_prob( self , x , y ) :
		xkey , xval = x.keys()[ 0 ] , x[ x.keys()[ 0 ] ]
		if str( y ) in self.probs[ xkey ][ xval ] : return self.probs[ xkey ][ xval ][ str( y ) ]
		self.cont +=1
		numerator = copy( x )
		for key in y : numerator[ key ] = y[ key ]
		denominator = y
		if not denominator :
			pnum = len( self.query( numerator ) )
			pden = len( self.rows )
		else :
			pnum = len( self.query( numerator ) ) + self.bdeuprior( numerator )
			pden = len( self.query( denominator ) ) + self.bdeuprior( denominator )
		pnum = float( pnum )
		pden = float( pden )
		return pnum / pden
	
	def query( self , filters ) :
		resp = []
		for row in self.rows :
			if all( item in row.items() for item in filters.items() ) :
				resp.append( row )
		return resp
	
	def bdeuprior( self , setfields ) :
		prior = 1.0
		for field in setfields :
			tam = ( len( self.stats[ field ] ) if self.fieldtypes[ field ] == LITERAL_FIELD else 2 )
			prior *= tam
		return ESS / prior

	def evaluate( self , setfields , pos = 0 ) :
		if pos == len( setfields ) : return []
		field = setfields[ pos ]
		if self.fieldtypes[ field ] == NUMERIC_FIELD :
			values = [ 0 , 1 ]
		else :
			values = self.stats[ field ].keys()
		resp = []
		for x in values :
			node = { field: x }
			nxt = self.evaluate( setfields , pos + 1 )
			if not nxt :
				resp.append( copy( node ) )
				continue
			for r in nxt :
				r[ field ] = x
				resp.append( r )
		return resp
	
	def loadAndTestModel( self , modelfile ) :
		self.loadmodel( modelfile )
		self.trainmodel()
		self.testmodel()
	
if __name__ == "__main__" :
	files = [ 'training.csv' ] 
	sources = [ DEFAULT_DATA_DIR + f for f in files ]
	evaluator = Evaluator( sources , savefilter = True , ommit = [ 'fnlgwt' ] , discretize = True )
	evaluator.addTrainingSet( [ DEFAULT_DATA_DIR + 'test.csv' ] )
	models = [ DEFAULT_DATA_DIR + f for f in [ 'model1.txt' , 'model2.txt' , 'model3.txt' ] ]
	for mod in models :
		evaluator.loadAndTestModel( mod )
