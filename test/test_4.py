from run_pipeline import run_pipeline
from src.type_collector import TypeCollector
from src.type_builder import TypeBuilder
from src.type_checker import TypeChecker
from src.tset_builder import TSetBuilder
from src.tsets_reducer import TSetReducer
from src.tset_merger import TSetMerger
from src.cool_visitor import FormatVisitor

# Trabajando con IO. Probando inferir el tipo de 'a' a partir del tipo que recibe el metodo out_string()
# Se infiere:
# main(): IO
# a : String
# x : Int
# y : IO


def test():
    text = """
class Main {
    main(a : AUTO_TYPE) : AUTO_TYPE {
        let x : AUTO_TYPE <- 3 in
            case x of
                y : IO => y.out_string(a);
            esac
    };
};
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

    if errors != [
        '"main" method in class Main does not receive any parameters',
    ]:
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
        '"main" method in class Main does not receive any parameters',
        '"main" method in class Main does not receive any parameters',
    ]
