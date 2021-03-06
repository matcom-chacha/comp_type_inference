from run_pipeline import run_pipeline
from src.cool_visitor import FormatVisitor


def test():
    text = """
        class Cons inherits List {
        xcar : Int ;
        xcdr : List ;

        isNill ( ) : Bool {
                false
        } ;

        init ( hd : Int , tl : List ) : Cons {
                {
                xcar <- hd ;
                xcdr <- tl ;
                self ;
                }
        } ;
        } ;
        """

    ast = run_pipeline(text)

    formatter = FormatVisitor()
    tree = formatter.visit(ast)

    tree = tree.replace("\t", "")
    tree = tree.replace("\n", "")
    tree = tree.replace("\\", "")

    assert (
        tree
        == "__ProgramNode [<class> ... <class>]__ClassDeclarationNode: class Cons inherits List { <feature> ... <feature> }__AttrDeclarationNode: xcar : Int <- <exp>__NONE__AttrDeclarationNode: xcdr : List <- <exp>__NONE__FuncDeclarationNode: isNill() : Bool { <body> }__ BooleanNode: false__FuncDeclarationNode: init(hd:Int, tl:List) : Cons { <body> }__BlockNode: {<exp>; ... <exp>;}__AssignNode: xcar <- <expr>__ VariableNode: hd__AssignNode: xcdr <- <expr>__ VariableNode: tl__ VariableNode: self"
    )
