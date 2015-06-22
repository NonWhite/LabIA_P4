from utils import *
from copy import deepcopy as copy
from evaluator import Evaluator
import sys

class Learner( Evaluator ) :
	def buildNetwork( self , useRandomSampling ) :
		print self.sources
		if useRandomSampling :
			self.randomSampling()
	
	# TODO: Implements this
	def randomSampling( self ) :
		for k in range( NUM_SAMPLES ) :
			lst_fields = shuffle( self.fields )
			for i in range( len( lst_fields ) ) :
				continue
		print 'RANDOM SAMPLING'

	# TODO: Implement this
	def greedySearch( self ) :
		print 'GREEDY SEARCH'
	
if __name__ == "__main__" :
	training_data = DATA_DIR + 'gentraining_model1.txt'
	test_data = TEST_FILE
	if len( sys.argv ) > 1 :
		( training_data , test_data ) = sys.argv[ 1: ]

	learner = Learner( [ training_data ] )
	learner.addTrainingSet( [ test_data ] )
	learner.buildNetwork( useRandomSampling = True )
	learner.buildNetwork( useRandomSampling = False )
