from utils import *
from copy import deepcopy as copy
from evaluator import Evaluator
from random import randint
from math import log
import sys

class Learner( Evaluator ) :
	def buildNetwork( self , outfilepath = 'out.txt' ) :
		self.out = open( outfilepath , 'w' )
		network = self.randomSampling()
		self.out.write( "BEST NETWORK:\n" )
		self.printnetwork( network )
	
	# TODO: Test this
	def randomSampling( self ) :
		self.out.write( 'Building network for %s\n' % ','.join( self.sources ) )
		node = { 'parents': [] , 'childs' : [] }
		best_networks = []
		self.entropyvalues = dict( [ ( field , {} ) for field in self.fields ] )
		self.sizevalues = dict( [ ( field , {} ) for field in self.fields ] )
		for k in range( NUM_ORDERING_SAMPLES ) :
			lst_fields = shuffle( self.fields )
			network = dict( [ ( field , copy( node ) ) for field in self.fields ] )
			network[ 'score' ] = 0.0
			self.out.write( "Building network #%s\n" % ( k + 1 ) )
			for i in range( len( lst_fields ) ) :
				field = lst_fields[ i ]
				print "======== Field #%s: %s ========" % ( i , field )
				best_parents = []
				#best_score = self.bic_score( field , best_parents ) # Without parents
				best_score = ( -INT_MAX if i > 0 else self.bic_score( field , best_parents ) )
				for t in range( NUM_GREEDY_RESTARTS ) :
					if i == 0 : break # First field doesn't have parents
					parents = []
					max_num_parents = min( MAX_NUM_PARENTS , i )
					for n in range( max_num_parents ) :
						while True :
							pos = randint( 0 , i - 1 )
							new_parent = lst_fields[ pos ]
							if new_parent not in parents : break
						parents.append( new_parent )
						current = self.bic_score( field , parents )
						if compare( current , best_score ) > 0 :
							print "BEST_SCORE CHANGED"
							best_score = current
							best_parents = copy( parents )
				self.addRelation( network , field , best_parents , best_score )
			# TODO: Remove this later
			self.printnetwork( network )
			best_networks.append( copy( network ) )
		sorted( best_networks , key = lambda netw : netw[ 'score' ] , reverse = True )
		return best_networks[ 0 ]
	
	def addRelation( self , network , field , parents , score ) :
		network[ field ][ 'parents' ] = copy( parents )
		for p in parents : network[ p ][ 'childs' ].append( field )
		network[ 'score' ] += score
	
	# TODO: Test this
	def bic_score( self , xsetfield , ysetfield ) :
		print "Calculating BIC( %s | %s )" % ( xsetfield , ysetfield )
		N = len( self.rows )
		H = self.entropy( xsetfield , ysetfield )
		#print "\tH( %s | %s ) = %s" % ( xsetfield , ysetfield , H )
		S = self.size( xsetfield , ysetfield )
		#print "\tSize( %s | %s ) = %s" % ( xsetfield , ysetfield , S )
		resp = ( -N * H ) + ( log( N ) / 2.0 * S )
		#print "\tBIC( %s | %s ) = %s" % ( xsetfield , ysetfield , resp )
		return resp
	
	# TODO: Test this
	def entropy( self , xsetfield , ysetfield ) :
		field = xsetfield
		cond = self.hashedarray( ysetfield )
		if cond in self.entropyvalues[ field ] : return self.entropyvalues[ field ][ cond ]
		x = self.evaluate( [ xsetfield ] )
		y = self.evaluate( ysetfield )
		N = len( self.rows )
		resp = 0.0
		for xdict in x :
			xkey , xval = xdict.keys()[ 0 ] , xdict.values()[ 0 ]
			for ydict in y :
				ij = copy( ydict )
				ijk = copy( ij )
				ijk[ xkey ] = xval
				Nijk = len( self.query( ijk ) ) + EPSILON
				Nij = len( self.query( ij ) ) + EPSILON
				resp += ( Nijk / N * log( Nijk / Nij ) )
		self.entropyvalues[ field ][ cond ] = -resp
		return -resp

	# TODO: Test this
	def size( self , xsetfield , ysetfield ) :
		field = xsetfield
		cond = self.hashedarray( ysetfield )
		if cond in self.sizevalues[ field ] : return self.sizevalues[ field ][ cond ]
		resp = len( self.evaluate( [ xsetfield ] ) ) - 1
		for field in ysetfield :
			resp *= len( self.evaluate( [ field ] ) )
		self.sizevalues[ field ][ cond ] = resp
		return resp

	def printnetwork( self , network ) :
		self.out.write( "SCORE = %s\n" % network[ 'score' ] )
		for field in self.fields :
			self.out.write( "%s: %s\n" % ( field , ','.join( network[ field ][ 'childs' ] ) ) )

if __name__ == "__main__" :
	if len( sys.argv ) > 1 :
		( training_data , test_data ) = sys.argv[ 1: ]
	test_data = TEST_FILE
	''' SYNTHETIC DATA '''
	for i in range( 1 , 4 ) :
		training_data = DATA_DIR + ( 'gentraining_model%s.txt' ) % i
		learner = Learner( [ training_data ] )
		#learner.addTrainingSet( [ test_data ] )
		output_data = RESULTS_DIR + ( 'gentraining_model%s.txt' ) % i
		learner.buildNetwork( outfilepath = output_data )
	''' REAL DATA '''
	output_data = RESULTS_DIR + 'realdata.txt'
	learner = Learner( [ TRAINING_FILE ] , savefilter = True , ommit = [ 'fnlgwt' ] , discretize = True )
	#learner.addTrainingSet( [ test_data ] )
	learner.buildNetwork( outfilepath = output_data )
