from run_pipeline import run_pipeline
from src.type_collector import TypeCollector
from src.type_builder import TypeBuilder
from src.type_checker import TypeChecker
from src.tset_builder import TSetBuilder
from src.tsets_reducer import TSetReducer
from src.tset_merger import TSetMerger
from src.cool_visitor import FormatVisitor


# Probando detectar herencia ciclica


def test():
    text = """
            class B inherits A { 
                a : String ;
                b : AUTO_TYPE ;
            };
            class A inherits A { } ;
            """

    print("corriendo")
    ast = run_pipeline(text)
    errors = []

    collector = TypeCollector(errors)
    collector.visit(ast)

    context = collector.context

    builder = TypeBuilder(context, errors)
    builder.visit(ast)

    checker = TypeChecker(context, errors)
    checker.visit(ast, None)

    err = [
        "A is involved in a cyclic heritage",
        "A class Main with a method main most be provided",
    ]

    if errors != err:
        print(errors)
        assert False

    assert True

