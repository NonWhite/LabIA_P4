from utils import *
from copy import deepcopy as copy
from math import log
from extractor import Extractor
import sys
import os.path
from random import randint as random

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
		print "Calculating P( %s | %s )" % ( xsetfield , ysetfield )
		implies = self.evaluate( xsetfield )
		condition = self.evaluate( ysetfield )
		self.cont = 0
		for xdict in implies :
			xkey = xdict.keys()[ 0 ] # Supose it only has one field in X
			xval = xdict.values()[ 0 ]
			if xval not in self.probs[ xkey ] : self.probs[ xkey ][ xval ] = {}
			if not condition :
				self.conditional_prob( xdict , {} )
				continue
			for y in condition :
				self.conditional_prob( xdict , y )
		print "CONT = %s" % self.cont

	def conditional_prob( self , x , y ) :
		xkey , xval = x.keys()[ 0 ] , x.values()[ 0 ]
		if str( y ) in self.probs[ xkey ][ xval ] : return self.probs[ xkey ][ xval ][ str( y ) ]
		self.cont += 1
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
		self.probs[ xkey ][ xval ][ str( y ) ] = pnum / pden
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
		return self.testmodel()
	
	# TODO: Generate data
	def generateData( self , modelname ) :
		modelname = os.path.basename( modelname )
		rows_to_generate = int( GENERATED_DATA * TRAINING_DATA_PERCENTAGE )
		rows = [ dict( [ ( field , '' ) for field in self.fields ] ) ] * rows_to_generate
		order_fields = sorted( self.fields , key = lambda field: len( self.network[ field ][ 'parents' ] ) )
		for field in order_fields :
			implies = self.evaluate( [ field ] )
			condition = self.evaluate( self.network[ field ][ 'parents' ] )
			for xdict in implies :
				if not condition : condition = [ {} ]
				for y in condition :
					prob = self.conditional_prob( xdict , y )
					values_to_put = prob * rows_to_generate
					cont = 0
			
		with open( GEN_TRAINING_FILE % modelname , 'w' ) as f :
			for x in range( rows_to_generate ) :
				continue
		rows_to_generate = int( GENERATED_DATA * TEST_DATA_PERCENTAGE )
		with open( GEN_TEST_FILE % modelname , 'w' ) as f :
			for x in range( rows_to_generate ) :
				continue
	
if __name__ == "__main__" :
	training_data = TRAINING_FILE
	test_data = TEST_FILE
	models = MODELS
	if len( sys.argv ) > 1 :
		( training_data , test_data ) = sys.argv[ 1: ]

	evaluator = Evaluator( [ training_data ] , savefilter = True , ommit = [ 'fnlgwt' ] , discretize = True )
	evaluator.addTrainingSet( [ test_data ] )
	for mod in models :
		evaluator.loadAndTestModel( mod )
		evaluator.generateData( mod )
