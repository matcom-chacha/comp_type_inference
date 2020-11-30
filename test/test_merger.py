from run_pipeline import run_pipeline
from src.type_collector import TypeCollector
from src.type_builder import TypeBuilder
from src.type_checker import TypeChecker
from src.tset_builder import TSetBuilder
from src.tsets_reducer import TSetReducer
from src.tset_merger import TSetMerger
from src.cool_visitor import FormatVisitor


def test():
    text = """

       class A {
           a : String ;
           b : AUTO_TYPE ;
           c : AUTO_TYPE <- 0 ;
           d : Object <- while c loop c + 1 pool  ; (*first and second errors*)
           j : AUTO_TYPE ;
           l : AUTO_TYPE ;
           fact ( n : AUTO_TYPE ) : AUTO_TYPE { if  n < 0  then 1 else  n + fact ( n - 1 )   fi } ;
           step ( p : AUTO_TYPE ) : AUTO_TYPE {
               b <-
                {
                    p + 5 ;
                    j <- p ; (*third error*)
                    p <- false ;
                    isvoid d ;

                    l @ Point . main ( ) ;
                }
            } ;
        } ;
         class Point inherits A {
            h : AUTO_TYPE <- "debe ser tipo string" ;
            k : AUTO_TYPE ;
            main ( ) : AUTO_TYPE {
                let i : AUTO_TYPE <- new A in {
                    isvoid i ; (*Puede lanzar error semantico*)
                }
            } ;
            ackermann ( m : AUTO_TYPE , n : AUTO_TYPE ) : AUTO_TYPE {
                if  m < 0  then 1 else
                    if  n < 0  then ackermann ( m - 1 , 1 ) else
                        ackermann ( m - 1 , ackermann ( m , n - 1 ) )
                    fi
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
    checker.visit(ast, None)

    print(errors)
    if errors != []:
        print(errors)
        assert False

    tset_builder = TSetBuilder(context, errors)
    tset = tset_builder.visit(ast, None)

    tset_reducer = TSetReducer(context, errors)
    reduced_set = tset_reducer.visit(ast, tset)

    tset_merger = TSetMerger(context, errors)
    tset_merger.visit(ast, reduced_set)

    collector = TypeCollector(errors)
    collector.visit(ast)

    context = collector.context

    builder = TypeBuilder(context, errors)
    builder.visit(ast)

    checker = TypeChecker(context, errors)
    checker.visit(ast, None)

    formatter = FormatVisitor()
    tree = formatter.visit(ast)

    print("Errors:", errors)
    print("Context:")
    print(context)
    print(reduced_set)
    print(tree)

    assert errors == [
        "Expression after 'while' must be bool, current is Object",
        'Operation is not defined between "Object" and "Int".',
        'Cannot convert "Object" into "Int".',
    ]
