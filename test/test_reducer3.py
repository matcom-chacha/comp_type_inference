from run_pipeline import run_pipeline
from src.type_collector import TypeCollector
from src.type_builder import TypeBuilder
from src.type_checker import TypeChecker
from src.tset_builder import TSetBuilder
from src.tsets_reducer import TSetReducer


def test():
    text = """
        
       class A { 
           a : String ;
        } ;
         class Point inherits A {
            f ( a : AUTO_TYPE , b : AUTO_TYPE ) : AUTO_TYPE {
                if ( a = 1 ) then b else
                    g ( a + 1 , b / 2 )
                fi
            } ;
            g ( a : AUTO_TYPE , b : AUTO_TYPE ) : AUTO_TYPE {
                if ( b = 1 ) then a else
                    f ( a / 2 , b + 1 ) 
                fi
            } ;
        } ;
        
        """

    ast = run_pipeline(text)
    errors = []

    collector = TypeCollector(errors)
    collector.visit(ast)

    context = collector.context

    builder = TypeBuilder(context, errors)
    builder.visit(ast)

    checker = TypeChecker(context, errors)
    __ = checker.visit(ast, None)

    tset_builder = TSetBuilder(context, errors)
    tset = tset_builder.visit(ast, None)

    tset_reducer = TSetReducer(context, errors)
    reduced_set = tset_reducer.visit(ast, tset)

    print("Errors:", errors)
    print("Context:")
    print(context)
    print(reduced_set)

    assert errors == ["A class Main with a method main most be provided"]
