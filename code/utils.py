DATA_DIR = '../data/'
TRAINING_FILE = DATA_DIR + 'training.csv'
TEST_FILE = DATA_DIR + 'test.csv'
MODELS = [ DATA_DIR + x for x in [ 'model1.txt' , 'model2.txt' , 'model3.txt' ] ]

FIELD_DELIMITER = ','

NUMERIC_FIELD = 'numeric'
LITERAL_FIELD = 'literal'

INT_MAX = 200000000000

ESS = 1.0

TRAINING_DATA_PERCENTAGE = 0.65
TEST_DATA_PERCENTAGE = 1 - TRAINING_DATA_PERCENTAGE

GENERATED_DATA = 20000
GEN_TRAINING_FILE = DATA_DIR + 'gentraining_%s'
GEN_TEST_FILE = DATA_DIR + 'gentest_%s'
