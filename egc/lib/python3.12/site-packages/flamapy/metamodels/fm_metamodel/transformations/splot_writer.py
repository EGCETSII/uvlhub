from flamapy.core.transformations import ModelToText
from flamapy.metamodels.fm_metamodel.models import (
    FeatureModel,
    Feature,
    Constraint
)

TAB = '\t'


class SPLOTWriter(ModelToText):

    @staticmethod
    def get_destination_extension() -> str:
        return 'sxfm'

    def __init__(self, path: str, source_model: FeatureModel) -> None:
        self.path = path
        self.source_model = source_model

    def transform(self) -> str:
        splot_str = fm_to_splot(self.source_model)
        if self.path is not None:
            with open(self.path, 'w', encoding='utf8') as file:
                file.write(splot_str)
        return splot_str


def fm_to_splot(model: FeatureModel) -> str:
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    lines.append(f'<feature_model name="{model.root.name}">')
    lines.append('<feature_tree>')
    lines.append(f':r {model.root.name} ({model.root.name})')
    lines.extend(add_features(model.root, 1))
    lines.append('</feature_tree>')
    lines.append('<constraints>')
    lines.extend(add_constraints(model.ctcs))
    lines.append('</constraints>')
    lines.append('</feature_model>')
    return '\n'.join(lines)


def add_features(feature: Feature, n_tabs: int) -> list[str]:
    lines = []
    indentation = TAB * n_tabs
    for relation in feature.get_relations():
        if relation.is_optional():
            child = relation.children[0]
            lines.append(indentation + f':o {child.name} ({child.name})')
            lines.extend(add_features(child, n_tabs + 1))
        elif relation.is_mandatory():
            child = relation.children[0]
            lines.append(indentation + f':m {child.name} ({child.name})')
            lines.extend(add_features(child, n_tabs + 1))
        elif relation.is_alternative() or relation.is_or():
            lines.append(indentation + f':g [{relation.card_min},{relation.card_max}]')
            for child in relation.children:
                lines.append(indentation + TAB + f': {child.name} ({child.name})')
                lines.extend(add_features(child, n_tabs + 2))
    return lines


def add_constraints(constraints: list[Constraint]) -> list[str]:
    lines = []
    index = 1
    indentation = TAB
    for ctc in constraints:
        cnf_clauses = ctc.ast.get_clauses()
        for clause in cnf_clauses:
            clause_list_str = ['~' + t[1:] if t.startswith('-') else t for t in clause]
            clause_str = ' or '.join(clause_list_str)
            lines.append(indentation + f'C{index}: {clause_str}')
            index += 1
    return lines
