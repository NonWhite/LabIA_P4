from utils import *
from copy import deepcopy as copy
from evaluator import Evaluator
from random import randint
from math import log
import sys

class Learner( Evaluator ) :
	def buildNetwork( self ) :
		network = self.randomSampling()
		print "BEST NETWORK:"
		print "SCORE = %s" % network[ 'score' ]
		for field in self.fields : print "%s: %s" % ( field , ','.join( network[ field ][ 'childs' ] ) )
	
	# TODO: Test this
	def randomSampling( self ) :
		print 'Building network for %s' % ','.join( self.sources )
		node = { 'parents': [] , 'childs' : [] }
		best_networks = []
		for k in range( NUM_ORDERING_SAMPLES ) :
			lst_fields = shuffle( self.fields )
			network = dict( [ ( field , copy( node ) ) for field in self.fields ] )
			network[ 'score' ] = 0.0
			print "Building network #%s" % ( k + 1 )
			for i in range( len( lst_fields ) ) :
				field = lst_fields[ i ]
				best_parents = []
				best_score = self.bic_score( field , best_parents ) # Without parents
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
							best_score = current
							best_parents = copy( parents )
				self.addRelation( network , field , best_parents , best_score )
			# TODO: Remove this later
			print "\tSCORE = %s" % network[ 'score' ]
			for field in self.fields :
				print "\t%s: %s" % ( field , ','.join( network[ field ][ 'childs' ] ) )
			best_networks.append( copy( network ) )
		sorted( best_networks , key = lambda netw : netw[ 'score' ] , reverse = True )
		return best_networks[ 0 ]
	
	def addRelation( self , network , field , parents , score ) :
		network[ field ][ 'parents' ] = copy( parents )
		for p in parents : network[ p ][ 'childs' ].append( field )
		network[ 'score' ] += score
	
	# TODO: Test this
	def bic_score( self , xsetfield , ysetfield ) :
		N = len( self.rows )
		H = self.entropy( xsetfield , ysetfield )
		S = self.size( xsetfield , ysetfield )
		resp = -N * H - log( N ) / 2.0 * S
		return resp
	
	# TODO: Test this
	def entropy( self , xsetfield , ysetfield ) :
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
		return -resp

	# TODO: Test this
	def size( self , xsetfield , ysetfield ) :
		resp = len( self.evaluate( [ xsetfield ] ) ) - 1
		for field in ysetfield :
			resp *= len( self.evaluate( [ field ] ) )
		return resp

if __name__ == "__main__" :
	if len( sys.argv ) > 1 :
		( training_data , test_data ) = sys.argv[ 1: ]
	test_data = TEST_FILE
	for i in range( 1 , 4 ) :
		training_data = DATA_DIR + ( 'gentraining_model%s.txt' ) % i
		learner = Learner( [ training_data ] )
		learner.addTrainingSet( [ test_data ] )
		learner.buildNetwork()
