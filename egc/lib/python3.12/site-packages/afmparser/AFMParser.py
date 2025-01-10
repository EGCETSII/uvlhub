# Generated from afmparser/AFM.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,48,327,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,1,0,1,0,3,0,61,8,0,1,0,3,0,64,8,0,1,1,1,1,5,
        1,68,8,1,10,1,12,1,71,9,1,1,2,1,2,1,2,4,2,76,8,2,11,2,12,2,77,1,
        2,1,2,1,3,3,3,83,8,3,1,3,1,3,3,3,87,8,3,1,3,1,3,3,3,91,8,3,1,4,3,
        4,94,8,4,1,4,1,4,3,4,98,8,4,1,5,3,5,101,8,5,1,5,1,5,1,5,1,5,3,5,
        107,8,5,1,6,1,6,3,6,111,8,6,1,7,1,7,1,7,1,7,1,7,1,7,1,8,3,8,120,
        8,8,1,8,1,8,3,8,124,8,8,1,8,1,8,4,8,128,8,8,11,8,12,8,129,1,8,1,
        8,1,9,1,9,5,9,136,8,9,10,9,12,9,139,9,9,1,10,1,10,3,10,143,8,10,
        1,10,1,10,3,10,147,8,10,1,10,1,10,3,10,151,8,10,1,10,1,10,3,10,155,
        8,10,1,10,1,10,3,10,159,8,10,1,10,1,10,3,10,163,8,10,1,10,1,10,1,
        10,1,11,1,11,1,11,1,11,1,12,1,12,3,12,174,8,12,1,13,1,13,1,13,1,
        13,5,13,180,8,13,10,13,12,13,183,9,13,1,13,1,13,1,14,3,14,188,8,
        14,1,14,1,14,3,14,192,8,14,1,14,5,14,195,8,14,10,14,12,14,198,9,
        14,1,15,1,15,1,15,3,15,203,8,15,1,15,1,15,3,15,207,8,15,1,15,1,15,
        1,15,1,16,1,16,1,17,1,17,1,18,1,18,1,19,1,19,5,19,220,8,19,10,19,
        12,19,223,9,19,1,20,1,20,3,20,227,8,20,1,21,3,21,230,8,21,1,21,1,
        21,3,21,234,8,21,1,21,1,21,3,21,238,8,21,1,21,5,21,241,8,21,10,21,
        12,21,244,9,21,1,21,3,21,247,8,21,1,21,1,21,3,21,251,8,21,1,22,3,
        22,254,8,22,1,22,1,22,3,22,258,8,22,1,22,1,22,3,22,262,8,22,1,23,
        1,23,3,23,266,8,23,1,23,1,23,1,23,1,23,3,23,272,8,23,1,23,1,23,1,
        23,3,23,277,8,23,1,23,1,23,3,23,281,8,23,1,23,3,23,284,8,23,3,23,
        286,8,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,
        1,23,1,23,1,23,1,23,1,23,1,23,1,23,5,23,306,8,23,10,23,12,23,309,
        9,23,1,24,1,24,1,25,1,25,1,26,1,26,1,27,1,27,1,28,1,28,1,28,3,28,
        322,8,28,1,28,3,28,325,8,28,1,28,0,1,46,29,0,2,4,6,8,10,12,14,16,
        18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,0,5,
        1,0,42,46,1,0,31,34,1,0,15,21,1,0,35,40,1,0,44,45,352,0,58,1,0,0,
        0,2,65,1,0,0,0,4,72,1,0,0,0,6,82,1,0,0,0,8,93,1,0,0,0,10,100,1,0,
        0,0,12,110,1,0,0,0,14,112,1,0,0,0,16,119,1,0,0,0,18,133,1,0,0,0,
        20,140,1,0,0,0,22,167,1,0,0,0,24,173,1,0,0,0,26,175,1,0,0,0,28,187,
        1,0,0,0,30,199,1,0,0,0,32,211,1,0,0,0,34,213,1,0,0,0,36,215,1,0,
        0,0,38,217,1,0,0,0,40,226,1,0,0,0,42,229,1,0,0,0,44,253,1,0,0,0,
        46,285,1,0,0,0,48,310,1,0,0,0,50,312,1,0,0,0,52,314,1,0,0,0,54,316,
        1,0,0,0,56,324,1,0,0,0,58,60,3,2,1,0,59,61,3,18,9,0,60,59,1,0,0,
        0,60,61,1,0,0,0,61,63,1,0,0,0,62,64,3,38,19,0,63,62,1,0,0,0,63,64,
        1,0,0,0,64,1,1,0,0,0,65,69,5,1,0,0,66,68,3,4,2,0,67,66,1,0,0,0,68,
        71,1,0,0,0,69,67,1,0,0,0,69,70,1,0,0,0,70,3,1,0,0,0,71,69,1,0,0,
        0,72,75,3,6,3,0,73,76,3,12,6,0,74,76,3,16,8,0,75,73,1,0,0,0,75,74,
        1,0,0,0,76,77,1,0,0,0,77,75,1,0,0,0,77,78,1,0,0,0,78,79,1,0,0,0,
        79,80,5,2,0,0,80,5,1,0,0,0,81,83,5,47,0,0,82,81,1,0,0,0,82,83,1,
        0,0,0,83,84,1,0,0,0,84,86,5,43,0,0,85,87,5,47,0,0,86,85,1,0,0,0,
        86,87,1,0,0,0,87,88,1,0,0,0,88,90,5,3,0,0,89,91,5,47,0,0,90,89,1,
        0,0,0,90,91,1,0,0,0,91,7,1,0,0,0,92,94,5,47,0,0,93,92,1,0,0,0,93,
        94,1,0,0,0,94,95,1,0,0,0,95,97,5,43,0,0,96,98,5,47,0,0,97,96,1,0,
        0,0,97,98,1,0,0,0,98,9,1,0,0,0,99,101,5,47,0,0,100,99,1,0,0,0,100,
        101,1,0,0,0,101,102,1,0,0,0,102,103,5,4,0,0,103,104,5,43,0,0,104,
        106,5,5,0,0,105,107,5,47,0,0,106,105,1,0,0,0,106,107,1,0,0,0,107,
        11,1,0,0,0,108,111,3,8,4,0,109,111,3,10,5,0,110,108,1,0,0,0,110,
        109,1,0,0,0,111,13,1,0,0,0,112,113,5,4,0,0,113,114,5,44,0,0,114,
        115,5,6,0,0,115,116,5,44,0,0,116,117,5,5,0,0,117,15,1,0,0,0,118,
        120,5,47,0,0,119,118,1,0,0,0,119,120,1,0,0,0,120,121,1,0,0,0,121,
        123,3,14,7,0,122,124,5,47,0,0,123,122,1,0,0,0,123,124,1,0,0,0,124,
        125,1,0,0,0,125,127,5,7,0,0,126,128,3,8,4,0,127,126,1,0,0,0,128,
        129,1,0,0,0,129,127,1,0,0,0,129,130,1,0,0,0,130,131,1,0,0,0,131,
        132,5,8,0,0,132,17,1,0,0,0,133,137,5,9,0,0,134,136,3,20,10,0,135,
        134,1,0,0,0,136,139,1,0,0,0,137,135,1,0,0,0,137,138,1,0,0,0,138,
        19,1,0,0,0,139,137,1,0,0,0,140,142,3,22,11,0,141,143,5,47,0,0,142,
        141,1,0,0,0,142,143,1,0,0,0,143,144,1,0,0,0,144,146,5,3,0,0,145,
        147,5,47,0,0,146,145,1,0,0,0,146,147,1,0,0,0,147,148,1,0,0,0,148,
        150,3,24,12,0,149,151,5,47,0,0,150,149,1,0,0,0,150,151,1,0,0,0,151,
        152,1,0,0,0,152,154,5,6,0,0,153,155,5,47,0,0,154,153,1,0,0,0,154,
        155,1,0,0,0,155,156,1,0,0,0,156,158,3,32,16,0,157,159,5,47,0,0,158,
        157,1,0,0,0,158,159,1,0,0,0,159,160,1,0,0,0,160,162,5,6,0,0,161,
        163,5,47,0,0,162,161,1,0,0,0,162,163,1,0,0,0,163,164,1,0,0,0,164,
        165,3,34,17,0,165,166,5,2,0,0,166,21,1,0,0,0,167,168,5,43,0,0,168,
        169,5,10,0,0,169,170,5,42,0,0,170,23,1,0,0,0,171,174,3,26,13,0,172,
        174,3,28,14,0,173,171,1,0,0,0,173,172,1,0,0,0,174,25,1,0,0,0,175,
        176,5,4,0,0,176,181,3,36,18,0,177,178,5,6,0,0,178,180,3,36,18,0,
        179,177,1,0,0,0,180,183,1,0,0,0,181,179,1,0,0,0,181,182,1,0,0,0,
        182,184,1,0,0,0,183,181,1,0,0,0,184,185,5,5,0,0,185,27,1,0,0,0,186,
        188,5,47,0,0,187,186,1,0,0,0,187,188,1,0,0,0,188,189,1,0,0,0,189,
        191,5,41,0,0,190,192,5,47,0,0,191,190,1,0,0,0,191,192,1,0,0,0,192,
        196,1,0,0,0,193,195,3,30,15,0,194,193,1,0,0,0,195,198,1,0,0,0,196,
        194,1,0,0,0,196,197,1,0,0,0,197,29,1,0,0,0,198,196,1,0,0,0,199,200,
        5,4,0,0,200,202,5,44,0,0,201,203,5,47,0,0,202,201,1,0,0,0,202,203,
        1,0,0,0,203,204,1,0,0,0,204,206,5,11,0,0,205,207,5,47,0,0,206,205,
        1,0,0,0,206,207,1,0,0,0,207,208,1,0,0,0,208,209,5,44,0,0,209,210,
        5,5,0,0,210,31,1,0,0,0,211,212,3,36,18,0,212,33,1,0,0,0,213,214,
        3,36,18,0,214,35,1,0,0,0,215,216,7,0,0,0,216,37,1,0,0,0,217,221,
        5,12,0,0,218,220,3,40,20,0,219,218,1,0,0,0,220,223,1,0,0,0,221,219,
        1,0,0,0,221,222,1,0,0,0,222,39,1,0,0,0,223,221,1,0,0,0,224,227,3,
        42,21,0,225,227,3,44,22,0,226,224,1,0,0,0,226,225,1,0,0,0,227,41,
        1,0,0,0,228,230,5,47,0,0,229,228,1,0,0,0,229,230,1,0,0,0,230,231,
        1,0,0,0,231,233,5,43,0,0,232,234,5,47,0,0,233,232,1,0,0,0,233,234,
        1,0,0,0,234,235,1,0,0,0,235,237,5,7,0,0,236,238,5,47,0,0,237,236,
        1,0,0,0,237,238,1,0,0,0,238,242,1,0,0,0,239,241,3,44,22,0,240,239,
        1,0,0,0,241,244,1,0,0,0,242,240,1,0,0,0,242,243,1,0,0,0,243,246,
        1,0,0,0,244,242,1,0,0,0,245,247,5,47,0,0,246,245,1,0,0,0,246,247,
        1,0,0,0,247,248,1,0,0,0,248,250,5,8,0,0,249,251,5,47,0,0,250,249,
        1,0,0,0,250,251,1,0,0,0,251,43,1,0,0,0,252,254,5,47,0,0,253,252,
        1,0,0,0,253,254,1,0,0,0,254,255,1,0,0,0,255,257,3,46,23,0,256,258,
        5,47,0,0,257,256,1,0,0,0,257,258,1,0,0,0,258,259,1,0,0,0,259,261,
        5,2,0,0,260,262,5,47,0,0,261,260,1,0,0,0,261,262,1,0,0,0,262,45,
        1,0,0,0,263,265,6,23,-1,0,264,266,5,47,0,0,265,264,1,0,0,0,265,266,
        1,0,0,0,266,267,1,0,0,0,267,268,5,13,0,0,268,269,3,46,23,0,269,271,
        5,14,0,0,270,272,5,47,0,0,271,270,1,0,0,0,271,272,1,0,0,0,272,286,
        1,0,0,0,273,274,5,30,0,0,274,286,3,46,23,5,275,277,5,47,0,0,276,
        275,1,0,0,0,276,277,1,0,0,0,277,280,1,0,0,0,278,281,3,56,28,0,279,
        281,3,54,27,0,280,278,1,0,0,0,280,279,1,0,0,0,281,283,1,0,0,0,282,
        284,5,47,0,0,283,282,1,0,0,0,283,284,1,0,0,0,284,286,1,0,0,0,285,
        263,1,0,0,0,285,273,1,0,0,0,285,276,1,0,0,0,286,307,1,0,0,0,287,
        288,10,7,0,0,288,289,3,50,25,0,289,290,3,46,23,8,290,306,1,0,0,0,
        291,292,10,6,0,0,292,293,3,52,26,0,293,294,3,46,23,7,294,306,1,0,
        0,0,295,296,10,4,0,0,296,297,5,28,0,0,297,306,3,46,23,5,298,299,
        10,3,0,0,299,300,5,29,0,0,300,306,3,46,23,4,301,302,10,2,0,0,302,
        303,3,48,24,0,303,304,3,46,23,3,304,306,1,0,0,0,305,287,1,0,0,0,
        305,291,1,0,0,0,305,295,1,0,0,0,305,298,1,0,0,0,305,301,1,0,0,0,
        306,309,1,0,0,0,307,305,1,0,0,0,307,308,1,0,0,0,308,47,1,0,0,0,309,
        307,1,0,0,0,310,311,7,1,0,0,311,49,1,0,0,0,312,313,7,2,0,0,313,51,
        1,0,0,0,314,315,7,3,0,0,315,53,1,0,0,0,316,317,7,4,0,0,317,55,1,
        0,0,0,318,321,5,43,0,0,319,320,5,10,0,0,320,322,5,42,0,0,321,319,
        1,0,0,0,321,322,1,0,0,0,322,325,1,0,0,0,323,325,5,42,0,0,324,318,
        1,0,0,0,324,323,1,0,0,0,325,57,1,0,0,0,51,60,63,69,75,77,82,86,90,
        93,97,100,106,110,119,123,129,137,142,146,150,154,158,162,173,181,
        187,191,196,202,206,221,226,229,233,237,242,246,250,253,257,261,
        265,271,276,280,283,285,305,307,321,324
    ]

class AFMParser ( Parser ):

    grammarFileName = "AFM.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'%Relationships'", "';'", "':'", "'['", 
                     "']'", "','", "'{'", "'}'", "'%Attributes'", "'.'", 
                     "'to'", "'%Constraints'", "'('", "')'", "'+'", "'-'", 
                     "'*'", "'/'", "'%'", "'^'", "'='", "'abs'", "'max'", 
                     "'min'", "'cos'", "'sin'", "'sum'", "'AND'", "'OR'", 
                     "'NOT'", "'IFF'", "'IMPLIES'", "'REQUIRES'", "'EXCLUDES'", 
                     "'>'", "'<'", "'>='", "'<='", "'=='", "'!='", "'Integer'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "ADD", "SUB", 
                      "MULT", "DIV", "MOD", "POW", "ASIG", "ABS", "MAX", 
                      "MIN", "COS", "SIN", "SUM", "AND", "OR", "NOT", "IFF", 
                      "IMPLIES", "REQUIRES", "EXCLUDES", "HIGHER_THAN", 
                      "LOWER_THAN", "HIGHER_EQUAL_THAN", "LOWER_EQUAL_THAN", 
                      "EQUAL", "DISTINCT", "INTEGER", "LOWERCASE", "WORD", 
                      "INT", "DOUBLE", "STRING", "SPACE", "WS" ]

    RULE_feature_model = 0
    RULE_relationships_block = 1
    RULE_relationship_spec = 2
    RULE_init_spec = 3
    RULE_obligatory_spec = 4
    RULE_optional_spec = 5
    RULE_non_cardinal_spec = 6
    RULE_cardinality = 7
    RULE_cardinal_spec = 8
    RULE_attributes_block = 9
    RULE_attribute_spec = 10
    RULE_attribute_name = 11
    RULE_attribute_domain = 12
    RULE_discrete_domain_spec = 13
    RULE_range_domain_spec = 14
    RULE_domain_range = 15
    RULE_attribute_default_value = 16
    RULE_attribute_null_value = 17
    RULE_value_spec = 18
    RULE_constraints_block = 19
    RULE_constraint_spec = 20
    RULE_brackets_spec = 21
    RULE_simple_spec = 22
    RULE_expression = 23
    RULE_logical_operator = 24
    RULE_arithmetic_operator = 25
    RULE_relational_operator = 26
    RULE_number = 27
    RULE_variable = 28

    ruleNames =  [ "feature_model", "relationships_block", "relationship_spec", 
                   "init_spec", "obligatory_spec", "optional_spec", "non_cardinal_spec", 
                   "cardinality", "cardinal_spec", "attributes_block", "attribute_spec", 
                   "attribute_name", "attribute_domain", "discrete_domain_spec", 
                   "range_domain_spec", "domain_range", "attribute_default_value", 
                   "attribute_null_value", "value_spec", "constraints_block", 
                   "constraint_spec", "brackets_spec", "simple_spec", "expression", 
                   "logical_operator", "arithmetic_operator", "relational_operator", 
                   "number", "variable" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    ADD=15
    SUB=16
    MULT=17
    DIV=18
    MOD=19
    POW=20
    ASIG=21
    ABS=22
    MAX=23
    MIN=24
    COS=25
    SIN=26
    SUM=27
    AND=28
    OR=29
    NOT=30
    IFF=31
    IMPLIES=32
    REQUIRES=33
    EXCLUDES=34
    HIGHER_THAN=35
    LOWER_THAN=36
    HIGHER_EQUAL_THAN=37
    LOWER_EQUAL_THAN=38
    EQUAL=39
    DISTINCT=40
    INTEGER=41
    LOWERCASE=42
    WORD=43
    INT=44
    DOUBLE=45
    STRING=46
    SPACE=47
    WS=48

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Feature_modelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def relationships_block(self):
            return self.getTypedRuleContext(AFMParser.Relationships_blockContext,0)


        def attributes_block(self):
            return self.getTypedRuleContext(AFMParser.Attributes_blockContext,0)


        def constraints_block(self):
            return self.getTypedRuleContext(AFMParser.Constraints_blockContext,0)


        def getRuleIndex(self):
            return AFMParser.RULE_feature_model

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFeature_model" ):
                listener.enterFeature_model(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFeature_model" ):
                listener.exitFeature_model(self)




    def feature_model(self):

        localctx = AFMParser.Feature_modelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_feature_model)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 58
            self.relationships_block()
            self.state = 60
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==9:
                self.state = 59
                self.attributes_block()


            self.state = 63
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 62
                self.constraints_block()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Relationships_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def relationship_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Relationship_specContext)
            else:
                return self.getTypedRuleContext(AFMParser.Relationship_specContext,i)


        def getRuleIndex(self):
            return AFMParser.RULE_relationships_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationships_block" ):
                listener.enterRelationships_block(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationships_block" ):
                listener.exitRelationships_block(self)




    def relationships_block(self):

        localctx = AFMParser.Relationships_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_relationships_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            self.match(AFMParser.T__0)
            self.state = 69
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==43 or _la==47:
                self.state = 66
                self.relationship_spec()
                self.state = 71
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Relationship_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def init_spec(self):
            return self.getTypedRuleContext(AFMParser.Init_specContext,0)


        def non_cardinal_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Non_cardinal_specContext)
            else:
                return self.getTypedRuleContext(AFMParser.Non_cardinal_specContext,i)


        def cardinal_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Cardinal_specContext)
            else:
                return self.getTypedRuleContext(AFMParser.Cardinal_specContext,i)


        def getRuleIndex(self):
            return AFMParser.RULE_relationship_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationship_spec" ):
                listener.enterRelationship_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationship_spec" ):
                listener.exitRelationship_spec(self)




    def relationship_spec(self):

        localctx = AFMParser.Relationship_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_relationship_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.init_spec()
            self.state = 75 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 75
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
                if la_ == 1:
                    self.state = 73
                    self.non_cardinal_spec()
                    pass

                elif la_ == 2:
                    self.state = 74
                    self.cardinal_spec()
                    pass


                self.state = 77 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 149533581377552) != 0)):
                    break

            self.state = 79
            self.match(AFMParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Init_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(AFMParser.WORD, 0)

        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def getRuleIndex(self):
            return AFMParser.RULE_init_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInit_spec" ):
                listener.enterInit_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInit_spec" ):
                listener.exitInit_spec(self)




    def init_spec(self):

        localctx = AFMParser.Init_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_init_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 82
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 81
                self.match(AFMParser.SPACE)


            self.state = 84
            self.match(AFMParser.WORD)
            self.state = 86
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 85
                self.match(AFMParser.SPACE)


            self.state = 88
            self.match(AFMParser.T__2)
            self.state = 90
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.state = 89
                self.match(AFMParser.SPACE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Obligatory_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(AFMParser.WORD, 0)

        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def getRuleIndex(self):
            return AFMParser.RULE_obligatory_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterObligatory_spec" ):
                listener.enterObligatory_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitObligatory_spec" ):
                listener.exitObligatory_spec(self)




    def obligatory_spec(self):

        localctx = AFMParser.Obligatory_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_obligatory_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 92
                self.match(AFMParser.SPACE)


            self.state = 95
            self.match(AFMParser.WORD)
            self.state = 97
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.state = 96
                self.match(AFMParser.SPACE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Optional_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(AFMParser.WORD, 0)

        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def getRuleIndex(self):
            return AFMParser.RULE_optional_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOptional_spec" ):
                listener.enterOptional_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOptional_spec" ):
                listener.exitOptional_spec(self)




    def optional_spec(self):

        localctx = AFMParser.Optional_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_optional_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 100
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 99
                self.match(AFMParser.SPACE)


            self.state = 102
            self.match(AFMParser.T__3)
            self.state = 103
            self.match(AFMParser.WORD)
            self.state = 104
            self.match(AFMParser.T__4)
            self.state = 106
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                self.state = 105
                self.match(AFMParser.SPACE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Non_cardinal_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def obligatory_spec(self):
            return self.getTypedRuleContext(AFMParser.Obligatory_specContext,0)


        def optional_spec(self):
            return self.getTypedRuleContext(AFMParser.Optional_specContext,0)


        def getRuleIndex(self):
            return AFMParser.RULE_non_cardinal_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNon_cardinal_spec" ):
                listener.enterNon_cardinal_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNon_cardinal_spec" ):
                listener.exitNon_cardinal_spec(self)




    def non_cardinal_spec(self):

        localctx = AFMParser.Non_cardinal_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_non_cardinal_spec)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 110
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,12,self._ctx)
            if la_ == 1:
                self.state = 108
                self.obligatory_spec()
                pass

            elif la_ == 2:
                self.state = 109
                self.optional_spec()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CardinalityContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.INT)
            else:
                return self.getToken(AFMParser.INT, i)

        def getRuleIndex(self):
            return AFMParser.RULE_cardinality

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCardinality" ):
                listener.enterCardinality(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCardinality" ):
                listener.exitCardinality(self)




    def cardinality(self):

        localctx = AFMParser.CardinalityContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_cardinality)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 112
            self.match(AFMParser.T__3)
            self.state = 113
            self.match(AFMParser.INT)
            self.state = 114
            self.match(AFMParser.T__5)
            self.state = 115
            self.match(AFMParser.INT)
            self.state = 116
            self.match(AFMParser.T__4)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Cardinal_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def cardinality(self):
            return self.getTypedRuleContext(AFMParser.CardinalityContext,0)


        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def obligatory_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Obligatory_specContext)
            else:
                return self.getTypedRuleContext(AFMParser.Obligatory_specContext,i)


        def getRuleIndex(self):
            return AFMParser.RULE_cardinal_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCardinal_spec" ):
                listener.enterCardinal_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCardinal_spec" ):
                listener.exitCardinal_spec(self)




    def cardinal_spec(self):

        localctx = AFMParser.Cardinal_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_cardinal_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 119
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 118
                self.match(AFMParser.SPACE)


            self.state = 121
            self.cardinality()
            self.state = 123
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 122
                self.match(AFMParser.SPACE)


            self.state = 125
            self.match(AFMParser.T__6)
            self.state = 127 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 126
                self.obligatory_spec()
                self.state = 129 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==43 or _la==47):
                    break

            self.state = 131
            self.match(AFMParser.T__7)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Attributes_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attribute_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Attribute_specContext)
            else:
                return self.getTypedRuleContext(AFMParser.Attribute_specContext,i)


        def getRuleIndex(self):
            return AFMParser.RULE_attributes_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttributes_block" ):
                listener.enterAttributes_block(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttributes_block" ):
                listener.exitAttributes_block(self)




    def attributes_block(self):

        localctx = AFMParser.Attributes_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_attributes_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 133
            self.match(AFMParser.T__8)
            self.state = 137
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==43:
                self.state = 134
                self.attribute_spec()
                self.state = 139
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Attribute_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attribute_name(self):
            return self.getTypedRuleContext(AFMParser.Attribute_nameContext,0)


        def attribute_domain(self):
            return self.getTypedRuleContext(AFMParser.Attribute_domainContext,0)


        def attribute_default_value(self):
            return self.getTypedRuleContext(AFMParser.Attribute_default_valueContext,0)


        def attribute_null_value(self):
            return self.getTypedRuleContext(AFMParser.Attribute_null_valueContext,0)


        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def getRuleIndex(self):
            return AFMParser.RULE_attribute_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttribute_spec" ):
                listener.enterAttribute_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttribute_spec" ):
                listener.exitAttribute_spec(self)




    def attribute_spec(self):

        localctx = AFMParser.Attribute_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_attribute_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 140
            self.attribute_name()
            self.state = 142
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 141
                self.match(AFMParser.SPACE)


            self.state = 144
            self.match(AFMParser.T__2)
            self.state = 146
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,18,self._ctx)
            if la_ == 1:
                self.state = 145
                self.match(AFMParser.SPACE)


            self.state = 148
            self.attribute_domain()
            self.state = 150
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 149
                self.match(AFMParser.SPACE)


            self.state = 152
            self.match(AFMParser.T__5)
            self.state = 154
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 153
                self.match(AFMParser.SPACE)


            self.state = 156
            self.attribute_default_value()
            self.state = 158
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 157
                self.match(AFMParser.SPACE)


            self.state = 160
            self.match(AFMParser.T__5)
            self.state = 162
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 161
                self.match(AFMParser.SPACE)


            self.state = 164
            self.attribute_null_value()
            self.state = 165
            self.match(AFMParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Attribute_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(AFMParser.WORD, 0)

        def LOWERCASE(self):
            return self.getToken(AFMParser.LOWERCASE, 0)

        def getRuleIndex(self):
            return AFMParser.RULE_attribute_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttribute_name" ):
                listener.enterAttribute_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttribute_name" ):
                listener.exitAttribute_name(self)




    def attribute_name(self):

        localctx = AFMParser.Attribute_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_attribute_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 167
            self.match(AFMParser.WORD)
            self.state = 168
            self.match(AFMParser.T__9)
            self.state = 169
            self.match(AFMParser.LOWERCASE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Attribute_domainContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def discrete_domain_spec(self):
            return self.getTypedRuleContext(AFMParser.Discrete_domain_specContext,0)


        def range_domain_spec(self):
            return self.getTypedRuleContext(AFMParser.Range_domain_specContext,0)


        def getRuleIndex(self):
            return AFMParser.RULE_attribute_domain

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttribute_domain" ):
                listener.enterAttribute_domain(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttribute_domain" ):
                listener.exitAttribute_domain(self)




    def attribute_domain(self):

        localctx = AFMParser.Attribute_domainContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_attribute_domain)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 173
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4]:
                self.state = 171
                self.discrete_domain_spec()
                pass
            elif token in [41, 47]:
                self.state = 172
                self.range_domain_spec()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Discrete_domain_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Value_specContext)
            else:
                return self.getTypedRuleContext(AFMParser.Value_specContext,i)


        def getRuleIndex(self):
            return AFMParser.RULE_discrete_domain_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDiscrete_domain_spec" ):
                listener.enterDiscrete_domain_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDiscrete_domain_spec" ):
                listener.exitDiscrete_domain_spec(self)




    def discrete_domain_spec(self):

        localctx = AFMParser.Discrete_domain_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_discrete_domain_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 175
            self.match(AFMParser.T__3)
            self.state = 176
            self.value_spec()
            self.state = 181
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 177
                self.match(AFMParser.T__5)
                self.state = 178
                self.value_spec()
                self.state = 183
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 184
            self.match(AFMParser.T__4)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Range_domain_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INTEGER(self):
            return self.getToken(AFMParser.INTEGER, 0)

        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def domain_range(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Domain_rangeContext)
            else:
                return self.getTypedRuleContext(AFMParser.Domain_rangeContext,i)


        def getRuleIndex(self):
            return AFMParser.RULE_range_domain_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRange_domain_spec" ):
                listener.enterRange_domain_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRange_domain_spec" ):
                listener.exitRange_domain_spec(self)




    def range_domain_spec(self):

        localctx = AFMParser.Range_domain_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_range_domain_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 187
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 186
                self.match(AFMParser.SPACE)


            self.state = 189
            self.match(AFMParser.INTEGER)
            self.state = 191
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,26,self._ctx)
            if la_ == 1:
                self.state = 190
                self.match(AFMParser.SPACE)


            self.state = 196
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 193
                self.domain_range()
                self.state = 198
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Domain_rangeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.INT)
            else:
                return self.getToken(AFMParser.INT, i)

        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def getRuleIndex(self):
            return AFMParser.RULE_domain_range

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDomain_range" ):
                listener.enterDomain_range(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDomain_range" ):
                listener.exitDomain_range(self)




    def domain_range(self):

        localctx = AFMParser.Domain_rangeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_domain_range)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 199
            self.match(AFMParser.T__3)
            self.state = 200
            self.match(AFMParser.INT)
            self.state = 202
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 201
                self.match(AFMParser.SPACE)


            self.state = 204
            self.match(AFMParser.T__10)
            self.state = 206
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 205
                self.match(AFMParser.SPACE)


            self.state = 208
            self.match(AFMParser.INT)
            self.state = 209
            self.match(AFMParser.T__4)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Attribute_default_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value_spec(self):
            return self.getTypedRuleContext(AFMParser.Value_specContext,0)


        def getRuleIndex(self):
            return AFMParser.RULE_attribute_default_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttribute_default_value" ):
                listener.enterAttribute_default_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttribute_default_value" ):
                listener.exitAttribute_default_value(self)




    def attribute_default_value(self):

        localctx = AFMParser.Attribute_default_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_attribute_default_value)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 211
            self.value_spec()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Attribute_null_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value_spec(self):
            return self.getTypedRuleContext(AFMParser.Value_specContext,0)


        def getRuleIndex(self):
            return AFMParser.RULE_attribute_null_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttribute_null_value" ):
                listener.enterAttribute_null_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttribute_null_value" ):
                listener.exitAttribute_null_value(self)




    def attribute_null_value(self):

        localctx = AFMParser.Attribute_null_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_attribute_null_value)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 213
            self.value_spec()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Value_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(AFMParser.WORD, 0)

        def LOWERCASE(self):
            return self.getToken(AFMParser.LOWERCASE, 0)

        def INT(self):
            return self.getToken(AFMParser.INT, 0)

        def DOUBLE(self):
            return self.getToken(AFMParser.DOUBLE, 0)

        def STRING(self):
            return self.getToken(AFMParser.STRING, 0)

        def getRuleIndex(self):
            return AFMParser.RULE_value_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_spec" ):
                listener.enterValue_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_spec" ):
                listener.exitValue_spec(self)




    def value_spec(self):

        localctx = AFMParser.Value_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_value_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 215
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 136339441844224) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Constraints_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def constraint_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Constraint_specContext)
            else:
                return self.getTypedRuleContext(AFMParser.Constraint_specContext,i)


        def getRuleIndex(self):
            return AFMParser.RULE_constraints_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConstraints_block" ):
                listener.enterConstraints_block(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConstraints_block" ):
                listener.exitConstraints_block(self)




    def constraints_block(self):

        localctx = AFMParser.Constraints_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_constraints_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 217
            self.match(AFMParser.T__11)
            self.state = 221
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 206709259771904) != 0):
                self.state = 218
                self.constraint_spec()
                self.state = 223
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Constraint_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def brackets_spec(self):
            return self.getTypedRuleContext(AFMParser.Brackets_specContext,0)


        def simple_spec(self):
            return self.getTypedRuleContext(AFMParser.Simple_specContext,0)


        def getRuleIndex(self):
            return AFMParser.RULE_constraint_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConstraint_spec" ):
                listener.enterConstraint_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConstraint_spec" ):
                listener.exitConstraint_spec(self)




    def constraint_spec(self):

        localctx = AFMParser.Constraint_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_constraint_spec)
        try:
            self.state = 226
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,31,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 224
                self.brackets_spec()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 225
                self.simple_spec()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Brackets_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(AFMParser.WORD, 0)

        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def simple_spec(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.Simple_specContext)
            else:
                return self.getTypedRuleContext(AFMParser.Simple_specContext,i)


        def getRuleIndex(self):
            return AFMParser.RULE_brackets_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBrackets_spec" ):
                listener.enterBrackets_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBrackets_spec" ):
                listener.exitBrackets_spec(self)




    def brackets_spec(self):

        localctx = AFMParser.Brackets_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_brackets_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 229
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 228
                self.match(AFMParser.SPACE)


            self.state = 231
            self.match(AFMParser.WORD)
            self.state = 233
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 232
                self.match(AFMParser.SPACE)


            self.state = 235
            self.match(AFMParser.T__6)
            self.state = 237
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,34,self._ctx)
            if la_ == 1:
                self.state = 236
                self.match(AFMParser.SPACE)


            self.state = 242
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,35,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 239
                    self.simple_spec() 
                self.state = 244
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,35,self._ctx)

            self.state = 246
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 245
                self.match(AFMParser.SPACE)


            self.state = 248
            self.match(AFMParser.T__7)
            self.state = 250
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,37,self._ctx)
            if la_ == 1:
                self.state = 249
                self.match(AFMParser.SPACE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Simple_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(AFMParser.ExpressionContext,0)


        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def getRuleIndex(self):
            return AFMParser.RULE_simple_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSimple_spec" ):
                listener.enterSimple_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSimple_spec" ):
                listener.exitSimple_spec(self)




    def simple_spec(self):

        localctx = AFMParser.Simple_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_simple_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 253
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,38,self._ctx)
            if la_ == 1:
                self.state = 252
                self.match(AFMParser.SPACE)


            self.state = 255
            self.expression(0)
            self.state = 257
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 256
                self.match(AFMParser.SPACE)


            self.state = 259
            self.match(AFMParser.T__1)
            self.state = 261
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,40,self._ctx)
            if la_ == 1:
                self.state = 260
                self.match(AFMParser.SPACE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return AFMParser.RULE_expression

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class ArithmeticExpContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AFMParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AFMParser.ExpressionContext,i)

        def arithmetic_operator(self):
            return self.getTypedRuleContext(AFMParser.Arithmetic_operatorContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArithmeticExp" ):
                listener.enterArithmeticExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArithmeticExp" ):
                listener.exitArithmeticExp(self)


    class AndExpContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AFMParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AFMParser.ExpressionContext,i)

        def AND(self):
            return self.getToken(AFMParser.AND, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAndExp" ):
                listener.enterAndExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAndExp" ):
                listener.exitAndExp(self)


    class ParenthesisExpContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AFMParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(AFMParser.ExpressionContext,0)

        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParenthesisExp" ):
                listener.enterParenthesisExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParenthesisExp" ):
                listener.exitParenthesisExp(self)


    class RelationalExpContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AFMParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AFMParser.ExpressionContext,i)

        def relational_operator(self):
            return self.getTypedRuleContext(AFMParser.Relational_operatorContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationalExp" ):
                listener.enterRelationalExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationalExp" ):
                listener.exitRelationalExp(self)


    class OrExpContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AFMParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AFMParser.ExpressionContext,i)

        def OR(self):
            return self.getToken(AFMParser.OR, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrExp" ):
                listener.enterOrExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrExp" ):
                listener.exitOrExp(self)


    class AtomContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AFMParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def variable(self):
            return self.getTypedRuleContext(AFMParser.VariableContext,0)

        def number(self):
            return self.getTypedRuleContext(AFMParser.NumberContext,0)

        def SPACE(self, i:int=None):
            if i is None:
                return self.getTokens(AFMParser.SPACE)
            else:
                return self.getToken(AFMParser.SPACE, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAtom" ):
                listener.enterAtom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAtom" ):
                listener.exitAtom(self)


    class LogicalExpContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AFMParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AFMParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AFMParser.ExpressionContext,i)

        def logical_operator(self):
            return self.getTypedRuleContext(AFMParser.Logical_operatorContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalExp" ):
                listener.enterLogicalExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalExp" ):
                listener.exitLogicalExp(self)


    class NotExpContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AFMParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NOT(self):
            return self.getToken(AFMParser.NOT, 0)
        def expression(self):
            return self.getTypedRuleContext(AFMParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNotExp" ):
                listener.enterNotExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNotExp" ):
                listener.exitNotExp(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = AFMParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 46
        self.enterRecursionRule(localctx, 46, self.RULE_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 285
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,46,self._ctx)
            if la_ == 1:
                localctx = AFMParser.ParenthesisExpContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 265
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==47:
                    self.state = 264
                    self.match(AFMParser.SPACE)


                self.state = 267
                self.match(AFMParser.T__12)
                self.state = 268
                self.expression(0)
                self.state = 269
                self.match(AFMParser.T__13)
                self.state = 271
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,42,self._ctx)
                if la_ == 1:
                    self.state = 270
                    self.match(AFMParser.SPACE)


                pass

            elif la_ == 2:
                localctx = AFMParser.NotExpContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 273
                self.match(AFMParser.NOT)
                self.state = 274
                self.expression(5)
                pass

            elif la_ == 3:
                localctx = AFMParser.AtomContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 276
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==47:
                    self.state = 275
                    self.match(AFMParser.SPACE)


                self.state = 280
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [42, 43]:
                    self.state = 278
                    self.variable()
                    pass
                elif token in [44, 45]:
                    self.state = 279
                    self.number()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 283
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,45,self._ctx)
                if la_ == 1:
                    self.state = 282
                    self.match(AFMParser.SPACE)


                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 307
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,48,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 305
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,47,self._ctx)
                    if la_ == 1:
                        localctx = AFMParser.ArithmeticExpContext(self, AFMParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 287
                        if not self.precpred(self._ctx, 7):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 7)")
                        self.state = 288
                        self.arithmetic_operator()
                        self.state = 289
                        self.expression(8)
                        pass

                    elif la_ == 2:
                        localctx = AFMParser.RelationalExpContext(self, AFMParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 291
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 292
                        self.relational_operator()
                        self.state = 293
                        self.expression(7)
                        pass

                    elif la_ == 3:
                        localctx = AFMParser.AndExpContext(self, AFMParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 295
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 296
                        self.match(AFMParser.AND)
                        self.state = 297
                        self.expression(5)
                        pass

                    elif la_ == 4:
                        localctx = AFMParser.OrExpContext(self, AFMParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 298
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 299
                        self.match(AFMParser.OR)
                        self.state = 300
                        self.expression(4)
                        pass

                    elif la_ == 5:
                        localctx = AFMParser.LogicalExpContext(self, AFMParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 301
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 302
                        self.logical_operator()
                        self.state = 303
                        self.expression(3)
                        pass

             
                self.state = 309
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,48,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class Logical_operatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IFF(self):
            return self.getToken(AFMParser.IFF, 0)

        def IMPLIES(self):
            return self.getToken(AFMParser.IMPLIES, 0)

        def REQUIRES(self):
            return self.getToken(AFMParser.REQUIRES, 0)

        def EXCLUDES(self):
            return self.getToken(AFMParser.EXCLUDES, 0)

        def getRuleIndex(self):
            return AFMParser.RULE_logical_operator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogical_operator" ):
                listener.enterLogical_operator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogical_operator" ):
                listener.exitLogical_operator(self)




    def logical_operator(self):

        localctx = AFMParser.Logical_operatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_logical_operator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 310
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 32212254720) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Arithmetic_operatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ADD(self):
            return self.getToken(AFMParser.ADD, 0)

        def SUB(self):
            return self.getToken(AFMParser.SUB, 0)

        def MULT(self):
            return self.getToken(AFMParser.MULT, 0)

        def DIV(self):
            return self.getToken(AFMParser.DIV, 0)

        def MOD(self):
            return self.getToken(AFMParser.MOD, 0)

        def POW(self):
            return self.getToken(AFMParser.POW, 0)

        def ASIG(self):
            return self.getToken(AFMParser.ASIG, 0)

        def getRuleIndex(self):
            return AFMParser.RULE_arithmetic_operator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArithmetic_operator" ):
                listener.enterArithmetic_operator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArithmetic_operator" ):
                listener.exitArithmetic_operator(self)




    def arithmetic_operator(self):

        localctx = AFMParser.Arithmetic_operatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_arithmetic_operator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 312
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 4161536) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Relational_operatorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def HIGHER_THAN(self):
            return self.getToken(AFMParser.HIGHER_THAN, 0)

        def LOWER_THAN(self):
            return self.getToken(AFMParser.LOWER_THAN, 0)

        def HIGHER_EQUAL_THAN(self):
            return self.getToken(AFMParser.HIGHER_EQUAL_THAN, 0)

        def LOWER_EQUAL_THAN(self):
            return self.getToken(AFMParser.LOWER_EQUAL_THAN, 0)

        def EQUAL(self):
            return self.getToken(AFMParser.EQUAL, 0)

        def DISTINCT(self):
            return self.getToken(AFMParser.DISTINCT, 0)

        def getRuleIndex(self):
            return AFMParser.RULE_relational_operator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelational_operator" ):
                listener.enterRelational_operator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelational_operator" ):
                listener.exitRelational_operator(self)




    def relational_operator(self):

        localctx = AFMParser.Relational_operatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_relational_operator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 314
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 2164663517184) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(AFMParser.INT, 0)

        def DOUBLE(self):
            return self.getToken(AFMParser.DOUBLE, 0)

        def getRuleIndex(self):
            return AFMParser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)




    def number(self):

        localctx = AFMParser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 316
            _la = self._input.LA(1)
            if not(_la==44 or _la==45):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(AFMParser.WORD, 0)

        def LOWERCASE(self):
            return self.getToken(AFMParser.LOWERCASE, 0)

        def getRuleIndex(self):
            return AFMParser.RULE_variable

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariable" ):
                listener.enterVariable(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariable" ):
                listener.exitVariable(self)




    def variable(self):

        localctx = AFMParser.VariableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_variable)
        try:
            self.state = 324
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [43]:
                self.enterOuterAlt(localctx, 1)
                self.state = 318
                self.match(AFMParser.WORD)
                self.state = 321
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,49,self._ctx)
                if la_ == 1:
                    self.state = 319
                    self.match(AFMParser.T__9)
                    self.state = 320
                    self.match(AFMParser.LOWERCASE)


                pass
            elif token in [42]:
                self.enterOuterAlt(localctx, 2)
                self.state = 323
                self.match(AFMParser.LOWERCASE)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[23] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 7)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 2)
         




