from src.cmp.pycompiler import Grammar
from src.ast_nodes import (
    ProgramNode,
    ClassDeclarationNode,
    FuncDeclarationNode,
    AttrDeclarationNode,
    IfNode,
    WhileNode,
    LetNode,
    CaseNode,
    IsvoidNode,
    AssignNode,
    VarDeclarationNode,
    CaseItemNode,
    NotNode,
    LessNode,
    LessEqualNode,
    EqualNode,
    PlusNode,
    MinusNode,
    StarNode,
    DivNode,
    NegNode,
    InstantiateNode,
    BlockNode,
    CallNode,
    ConstantNumNode,
    VariableNode,
    BooleanNode,
    StringNode,
)


def define_cool_grammar(print_grammar=False):
    # grammar
    G = Grammar()

    # non-terminals
    program = G.NonTerminal("<program>", startSymbol=True)
    class_list, def_class = G.NonTerminals("<class-list> <def-class>")
    feature_list, def_attr, def_func = G.NonTerminals(
        "<feature-list> <def-attr> <def-func>"
    )
    param_list, param = G.NonTerminals("<param-list> <param>")
    expr, comp, arith, term, factor, element, atom = G.NonTerminals(
        "<expr> <comp> <arith> <term> <factor> <element> <atom>"
    )
    identifiers_list, identifier_init = G.NonTerminals("<ident-list> <ident-init>")
    block, case_block, case_item = G.NonTerminals("<block> <case-block> <case-item>")
    func_call, arg_list = G.NonTerminals("<func-call> <arg-list>")

    # terminals
    classx, inherits, notx, isvoid = G.Terminals("class inherits not isvoid")
    let, inx = G.Terminals("let in")
    ifx, then, elsex, fi = G.Terminals("if then else fi")
    whilex, loop, pool = G.Terminals("while loop pool")
    case, of, esac = G.Terminals("case of esac")
    semi, colon, comma, dot, opar, cpar, ocur, ccur, at, larrow, rarrow = G.Terminals(
        "; : , . ( ) { } @ <- =>"
    )
    equal, plus, minus, star, div, less, equal, lesseq, neg = G.Terminals(
        "= + - * / < = <= ~"
    )
    idx, num, new, string, true, false = G.Terminals("id int new string true false")

    # productions
    program %= class_list, lambda h, s: ProgramNode(s[1])

    class_list %= def_class + class_list, lambda h, s: [s[1]] + s[2]
    class_list %= def_class, lambda h, s: [s[1]]

    def_class %= (
        classx + idx + ocur + feature_list + ccur + semi,
        lambda h, s: ClassDeclarationNode(s[2], s[4]),
    )
    def_class %= (
        classx + idx + inherits + idx + ocur + feature_list + ccur + semi,
        lambda h, s: ClassDeclarationNode(s[2], s[6], s[4]),
    )

    feature_list %= def_attr + semi + feature_list, lambda h, s: [s[1]] + s[3]
    feature_list %= def_func + semi + feature_list, lambda h, s: [s[1]] + s[3]
    feature_list %= G.Epsilon, lambda h, s: []

    def_attr %= (
        idx + colon + idx + larrow + expr,
        lambda h, s: AttrDeclarationNode(s[1], s[3], s[5]),
    )
    def_attr %= idx + colon + idx, lambda h, s: AttrDeclarationNode(s[1], s[3])

    def_func %= (
        idx + opar + param_list + cpar + colon + idx + ocur + expr + ccur,
        lambda h, s: FuncDeclarationNode(s[1], s[3], s[6], s[8]),
    )

    param_list %= param + comma + param_list, lambda h, s: [s[1]] + s[3]
    param_list %= param, lambda h, s: [s[1]]
    param_list %= G.Epsilon, lambda h, s: []

    param %= idx + colon + idx, lambda h, s: (s[1], s[3])

    expr %= idx + larrow + expr, lambda h, s: AssignNode(s[1], s[3])
    expr %= let + identifiers_list + inx + expr, lambda h, s: LetNode(s[2], s[4])
    expr %= (
        ifx + expr + then + expr + elsex + expr + fi,
        lambda h, s: IfNode(s[2], s[4], s[6]),
    )
    expr %= whilex + expr + loop + expr + pool, lambda h, s: WhileNode(s[2], s[4])
    expr %= case + expr + of + case_block + esac, lambda h, s: CaseNode(s[2], s[4])
    expr %= notx + expr, lambda h, s: NotNode(s[2])
    expr %= comp, lambda h, s: s[1]

    identifiers_list %= (
        identifier_init + comma + identifiers_list,
        lambda h, s: [s[1]] + s[3],
    )
    identifiers_list %= identifier_init, lambda h, s: [s[1]]

    identifier_init %= (
        idx + colon + idx + larrow + expr,
        lambda h, s: VarDeclarationNode(s[1], s[3], s[5]),
    )
    identifier_init %= idx + colon + idx, lambda h, s: VarDeclarationNode(s[1], s[3])

    case_block %= case_item + case_block, lambda h, s: [s[1]] + s[2]
    case_block %= case_item, lambda h, s: [s[1]]
    case_item %= (
        idx + colon + idx + rarrow + expr + semi,
        lambda h, s: CaseItemNode(s[1], s[3], s[5]),
    )

    comp %= comp + less + arith, lambda h, s: LessNode(s[1], s[3])
    comp %= comp + equal + arith, lambda h, s: EqualNode(s[1], s[3])
    comp %= comp + lesseq + arith, lambda h, s: LessEqualNode(s[1], s[3])
    comp %= arith, lambda h, s: s[1]

    arith %= arith + plus + term, lambda h, s: PlusNode(s[1], s[3])
    arith %= arith + minus + term, lambda h, s: MinusNode(s[1], s[3])
    arith %= term, lambda h, s: s[1]

    term %= term + star + factor, lambda h, s: StarNode(s[1], s[3])
    term %= term + div + factor, lambda h, s: DivNode(s[1], s[3])
    term %= factor, lambda h, s: s[1]

    factor %= isvoid + element, lambda h, s: IsvoidNode(s[2])
    factor %= neg + element, lambda h, s: NegNode(s[2])
    factor %= new + idx, lambda h, s: InstantiateNode(s[2])
    factor %= element, lambda h, s: s[1]

    element %= opar + expr + cpar, lambda h, s: s[2]
    element %= ocur + block + ccur, lambda h, s: BlockNode(s[2])
    element %= (element + dot + func_call, lambda h, s: CallNode(*s[3], obj=s[1]))
    element %= (
        element + at + idx + dot + func_call,
        lambda h, s: CallNode(*s[5], obj=s[1], at_type=s[3]),
    )
    element %= func_call, lambda h, s: CallNode(*s[1])
    element %= atom, lambda h, s: s[1]

    atom %= num, lambda h, s: ConstantNumNode(s[1])
    atom %= idx, lambda h, s: VariableNode(s[1])
    atom %= (
        true,
        lambda h, s: BooleanNode(s[1]),
    )
    atom %= false, lambda h, s: BooleanNode(s[1])
    atom %= string, lambda h, s: StringNode(s[1])

    block %= expr + semi, lambda h, s: [s[1]]
    block %= expr + semi + block, lambda h, s: [s[1]] + s[3]

    func_call %= idx + opar + arg_list + cpar, lambda h, s: (s[1], s[3])

    arg_list %= expr + comma + arg_list, lambda h, s: [s[1]] + s[3]
    arg_list %= expr, lambda h, s: [s[1]]
    arg_list %= G.Epsilon, lambda h, s: []

    if print_grammar:
        print(G)
    return (G, idx, string, num)
