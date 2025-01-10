# Generated from afmparser/AFM.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .AFMParser import AFMParser
else:
    from AFMParser import AFMParser

# This class defines a complete listener for a parse tree produced by AFMParser.
class AFMListener(ParseTreeListener):

    # Enter a parse tree produced by AFMParser#feature_model.
    def enterFeature_model(self, ctx:AFMParser.Feature_modelContext):
        pass

    # Exit a parse tree produced by AFMParser#feature_model.
    def exitFeature_model(self, ctx:AFMParser.Feature_modelContext):
        pass


    # Enter a parse tree produced by AFMParser#relationships_block.
    def enterRelationships_block(self, ctx:AFMParser.Relationships_blockContext):
        pass

    # Exit a parse tree produced by AFMParser#relationships_block.
    def exitRelationships_block(self, ctx:AFMParser.Relationships_blockContext):
        pass


    # Enter a parse tree produced by AFMParser#relationship_spec.
    def enterRelationship_spec(self, ctx:AFMParser.Relationship_specContext):
        pass

    # Exit a parse tree produced by AFMParser#relationship_spec.
    def exitRelationship_spec(self, ctx:AFMParser.Relationship_specContext):
        pass


    # Enter a parse tree produced by AFMParser#init_spec.
    def enterInit_spec(self, ctx:AFMParser.Init_specContext):
        pass

    # Exit a parse tree produced by AFMParser#init_spec.
    def exitInit_spec(self, ctx:AFMParser.Init_specContext):
        pass


    # Enter a parse tree produced by AFMParser#obligatory_spec.
    def enterObligatory_spec(self, ctx:AFMParser.Obligatory_specContext):
        pass

    # Exit a parse tree produced by AFMParser#obligatory_spec.
    def exitObligatory_spec(self, ctx:AFMParser.Obligatory_specContext):
        pass


    # Enter a parse tree produced by AFMParser#optional_spec.
    def enterOptional_spec(self, ctx:AFMParser.Optional_specContext):
        pass

    # Exit a parse tree produced by AFMParser#optional_spec.
    def exitOptional_spec(self, ctx:AFMParser.Optional_specContext):
        pass


    # Enter a parse tree produced by AFMParser#non_cardinal_spec.
    def enterNon_cardinal_spec(self, ctx:AFMParser.Non_cardinal_specContext):
        pass

    # Exit a parse tree produced by AFMParser#non_cardinal_spec.
    def exitNon_cardinal_spec(self, ctx:AFMParser.Non_cardinal_specContext):
        pass


    # Enter a parse tree produced by AFMParser#cardinality.
    def enterCardinality(self, ctx:AFMParser.CardinalityContext):
        pass

    # Exit a parse tree produced by AFMParser#cardinality.
    def exitCardinality(self, ctx:AFMParser.CardinalityContext):
        pass


    # Enter a parse tree produced by AFMParser#cardinal_spec.
    def enterCardinal_spec(self, ctx:AFMParser.Cardinal_specContext):
        pass

    # Exit a parse tree produced by AFMParser#cardinal_spec.
    def exitCardinal_spec(self, ctx:AFMParser.Cardinal_specContext):
        pass


    # Enter a parse tree produced by AFMParser#attributes_block.
    def enterAttributes_block(self, ctx:AFMParser.Attributes_blockContext):
        pass

    # Exit a parse tree produced by AFMParser#attributes_block.
    def exitAttributes_block(self, ctx:AFMParser.Attributes_blockContext):
        pass


    # Enter a parse tree produced by AFMParser#attribute_spec.
    def enterAttribute_spec(self, ctx:AFMParser.Attribute_specContext):
        pass

    # Exit a parse tree produced by AFMParser#attribute_spec.
    def exitAttribute_spec(self, ctx:AFMParser.Attribute_specContext):
        pass


    # Enter a parse tree produced by AFMParser#attribute_name.
    def enterAttribute_name(self, ctx:AFMParser.Attribute_nameContext):
        pass

    # Exit a parse tree produced by AFMParser#attribute_name.
    def exitAttribute_name(self, ctx:AFMParser.Attribute_nameContext):
        pass


    # Enter a parse tree produced by AFMParser#attribute_domain.
    def enterAttribute_domain(self, ctx:AFMParser.Attribute_domainContext):
        pass

    # Exit a parse tree produced by AFMParser#attribute_domain.
    def exitAttribute_domain(self, ctx:AFMParser.Attribute_domainContext):
        pass


    # Enter a parse tree produced by AFMParser#discrete_domain_spec.
    def enterDiscrete_domain_spec(self, ctx:AFMParser.Discrete_domain_specContext):
        pass

    # Exit a parse tree produced by AFMParser#discrete_domain_spec.
    def exitDiscrete_domain_spec(self, ctx:AFMParser.Discrete_domain_specContext):
        pass


    # Enter a parse tree produced by AFMParser#range_domain_spec.
    def enterRange_domain_spec(self, ctx:AFMParser.Range_domain_specContext):
        pass

    # Exit a parse tree produced by AFMParser#range_domain_spec.
    def exitRange_domain_spec(self, ctx:AFMParser.Range_domain_specContext):
        pass


    # Enter a parse tree produced by AFMParser#domain_range.
    def enterDomain_range(self, ctx:AFMParser.Domain_rangeContext):
        pass

    # Exit a parse tree produced by AFMParser#domain_range.
    def exitDomain_range(self, ctx:AFMParser.Domain_rangeContext):
        pass


    # Enter a parse tree produced by AFMParser#attribute_default_value.
    def enterAttribute_default_value(self, ctx:AFMParser.Attribute_default_valueContext):
        pass

    # Exit a parse tree produced by AFMParser#attribute_default_value.
    def exitAttribute_default_value(self, ctx:AFMParser.Attribute_default_valueContext):
        pass


    # Enter a parse tree produced by AFMParser#attribute_null_value.
    def enterAttribute_null_value(self, ctx:AFMParser.Attribute_null_valueContext):
        pass

    # Exit a parse tree produced by AFMParser#attribute_null_value.
    def exitAttribute_null_value(self, ctx:AFMParser.Attribute_null_valueContext):
        pass


    # Enter a parse tree produced by AFMParser#value_spec.
    def enterValue_spec(self, ctx:AFMParser.Value_specContext):
        pass

    # Exit a parse tree produced by AFMParser#value_spec.
    def exitValue_spec(self, ctx:AFMParser.Value_specContext):
        pass


    # Enter a parse tree produced by AFMParser#constraints_block.
    def enterConstraints_block(self, ctx:AFMParser.Constraints_blockContext):
        pass

    # Exit a parse tree produced by AFMParser#constraints_block.
    def exitConstraints_block(self, ctx:AFMParser.Constraints_blockContext):
        pass


    # Enter a parse tree produced by AFMParser#constraint_spec.
    def enterConstraint_spec(self, ctx:AFMParser.Constraint_specContext):
        pass

    # Exit a parse tree produced by AFMParser#constraint_spec.
    def exitConstraint_spec(self, ctx:AFMParser.Constraint_specContext):
        pass


    # Enter a parse tree produced by AFMParser#brackets_spec.
    def enterBrackets_spec(self, ctx:AFMParser.Brackets_specContext):
        pass

    # Exit a parse tree produced by AFMParser#brackets_spec.
    def exitBrackets_spec(self, ctx:AFMParser.Brackets_specContext):
        pass


    # Enter a parse tree produced by AFMParser#simple_spec.
    def enterSimple_spec(self, ctx:AFMParser.Simple_specContext):
        pass

    # Exit a parse tree produced by AFMParser#simple_spec.
    def exitSimple_spec(self, ctx:AFMParser.Simple_specContext):
        pass


    # Enter a parse tree produced by AFMParser#arithmeticExp.
    def enterArithmeticExp(self, ctx:AFMParser.ArithmeticExpContext):
        pass

    # Exit a parse tree produced by AFMParser#arithmeticExp.
    def exitArithmeticExp(self, ctx:AFMParser.ArithmeticExpContext):
        pass


    # Enter a parse tree produced by AFMParser#andExp.
    def enterAndExp(self, ctx:AFMParser.AndExpContext):
        pass

    # Exit a parse tree produced by AFMParser#andExp.
    def exitAndExp(self, ctx:AFMParser.AndExpContext):
        pass


    # Enter a parse tree produced by AFMParser#parenthesisExp.
    def enterParenthesisExp(self, ctx:AFMParser.ParenthesisExpContext):
        pass

    # Exit a parse tree produced by AFMParser#parenthesisExp.
    def exitParenthesisExp(self, ctx:AFMParser.ParenthesisExpContext):
        pass


    # Enter a parse tree produced by AFMParser#relationalExp.
    def enterRelationalExp(self, ctx:AFMParser.RelationalExpContext):
        pass

    # Exit a parse tree produced by AFMParser#relationalExp.
    def exitRelationalExp(self, ctx:AFMParser.RelationalExpContext):
        pass


    # Enter a parse tree produced by AFMParser#orExp.
    def enterOrExp(self, ctx:AFMParser.OrExpContext):
        pass

    # Exit a parse tree produced by AFMParser#orExp.
    def exitOrExp(self, ctx:AFMParser.OrExpContext):
        pass


    # Enter a parse tree produced by AFMParser#atom.
    def enterAtom(self, ctx:AFMParser.AtomContext):
        pass

    # Exit a parse tree produced by AFMParser#atom.
    def exitAtom(self, ctx:AFMParser.AtomContext):
        pass


    # Enter a parse tree produced by AFMParser#logicalExp.
    def enterLogicalExp(self, ctx:AFMParser.LogicalExpContext):
        pass

    # Exit a parse tree produced by AFMParser#logicalExp.
    def exitLogicalExp(self, ctx:AFMParser.LogicalExpContext):
        pass


    # Enter a parse tree produced by AFMParser#notExp.
    def enterNotExp(self, ctx:AFMParser.NotExpContext):
        pass

    # Exit a parse tree produced by AFMParser#notExp.
    def exitNotExp(self, ctx:AFMParser.NotExpContext):
        pass


    # Enter a parse tree produced by AFMParser#logical_operator.
    def enterLogical_operator(self, ctx:AFMParser.Logical_operatorContext):
        pass

    # Exit a parse tree produced by AFMParser#logical_operator.
    def exitLogical_operator(self, ctx:AFMParser.Logical_operatorContext):
        pass


    # Enter a parse tree produced by AFMParser#arithmetic_operator.
    def enterArithmetic_operator(self, ctx:AFMParser.Arithmetic_operatorContext):
        pass

    # Exit a parse tree produced by AFMParser#arithmetic_operator.
    def exitArithmetic_operator(self, ctx:AFMParser.Arithmetic_operatorContext):
        pass


    # Enter a parse tree produced by AFMParser#relational_operator.
    def enterRelational_operator(self, ctx:AFMParser.Relational_operatorContext):
        pass

    # Exit a parse tree produced by AFMParser#relational_operator.
    def exitRelational_operator(self, ctx:AFMParser.Relational_operatorContext):
        pass


    # Enter a parse tree produced by AFMParser#number.
    def enterNumber(self, ctx:AFMParser.NumberContext):
        pass

    # Exit a parse tree produced by AFMParser#number.
    def exitNumber(self, ctx:AFMParser.NumberContext):
        pass


    # Enter a parse tree produced by AFMParser#variable.
    def enterVariable(self, ctx:AFMParser.VariableContext):
        pass

    # Exit a parse tree produced by AFMParser#variable.
    def exitVariable(self, ctx:AFMParser.VariableContext):
        pass



del AFMParser