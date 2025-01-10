from antlr4 import CommonTokenStream, FileStream
from afmparser.AFMLexer import AFMLexer
from afmparser.AFMParser import AFMParser


def get_tree(argv):
    input_stream = FileStream(argv)
    lexer = AFMLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = AFMParser(stream)
    tree = parser.feature_model()
    return tree
