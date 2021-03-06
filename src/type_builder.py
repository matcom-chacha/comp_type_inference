from src.cmp.semantic import SemanticError
from src.cmp.semantic import Attribute, Method, Type
from src.cmp.semantic import VoidType, IntType, ErrorType, StringType, BoolType
from src.cmp.semantic import Context
from src.ast_nodes import (
    ProgramNode,
    ClassDeclarationNode,
    AttrDeclarationNode,
    FuncDeclarationNode,
)
import src.cmp.visitor as visitor
from src.tset import Tset
from collections import deque


class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node):
        # Despues de entregar!!!!!!
        io_type = self.context.get_type("IO")
        self_type = self.context.get_type("SELF_TYPE")
        int_type = self.context.get_type("Int")
        string_type = self.context.get_type("String")
        object_type = self.context.get_type("Object")

        # IO
        parent_tset = Tset()
        parent_tset.locals["out_string"] = {"SELF_TYPE"}
        parent_tset.locals["out_int"] = {"SELF_TYPE"}
        parent_tset.locals["in_string"] = {"String"}
        parent_tset.locals["in_int"] = {"Int"}

        method = io_type.define_method("out_string", ["x"], [string_type], self_type)
        method.tset = Tset(parent_tset)
        method.tset.locals["x"] = {"String"}

        method = io_type.define_method("out_int", ["x"], [int_type], self_type)
        method.tset = Tset(parent_tset)
        method.tset.locals["x"] = {"Int"}

        method = io_type.define_method("in_string", [], [], string_type)
        method.tset = Tset(parent_tset)

        method = io_type.define_method("in_int", [], [], int_type)
        method.tset = Tset(parent_tset)

        # -------String
        parent_tset = Tset()
        parent_tset.locals["concat"] = {"String"}
        parent_tset.locals["substr"] = {"String"}
        parent_tset.locals["length"] = {"Int"}

        method = string_type.define_method("concat", ["s"], [string_type], string_type)
        method.tset = Tset(parent_tset)
        method.tset.locals["s"] = {"String"}

        method = string_type.define_method(
            "substr", ["i", "l"], [int_type, int_type], string_type
        )
        method.tset = Tset(parent_tset)
        method.tset.locals["i"] = {"Int"}
        method.tset.locals["l"] = {"Int"}

        method = string_type.define_method("length", [], [], int_type)
        method.tset = Tset(parent_tset)

        # Object
        parent_tset = Tset()
        parent_tset.locals["abort"] = {"Object"}
        parent_tset.locals["type_name"] = {"String"}
        parent_tset.locals["copy"] = {"SELF_TYPE"}

        method = object_type.define_method("abort", [], [], object_type)
        method.tset = Tset(parent_tset)

        method = object_type.define_method("type_name", [], [], string_type)
        method.tset = Tset(parent_tset)

        method = object_type.define_method("copy", [], [], self_type)
        method.tset = Tset(parent_tset)

        # --------------------

        # ------checking for in order definitions and cyclic heritage
        parent_child_dict = {}
        queue = deque()
        visited = {}
        not_visited = []  # ++

        for class_declaration in node.declarations:
            not_visited.append(class_declaration)  # ++
            parent_type = class_declaration.parent
            try:
                self.context.get_type(parent_type)
                try:
                    parent_child_dict[parent_type].append(class_declaration)
                except:  # KeyError
                    parent_child_dict[parent_type] = [class_declaration]
            except SemanticError:  # parent is None or not definition provided
                queue.append(class_declaration)

        main_round = 0
        while not_visited:  # ++
            main_round += 1
            while queue:
                class_declaration = queue.popleft()
                try:
                    class_visited, roundn = visited[class_declaration]  # .id

                    if roundn == main_round:
                        self.errors.append(
                            f"{class_declaration.id} is involved in a cyclic heritage"
                        )

                except:
                    not_visited.remove(class_declaration)
                    try:
                        children = parent_child_dict[class_declaration.id]
                        for declaration in children:
                            queue.append(declaration)
                    except:  # no es padre de nadie
                        pass

                    self.visit(class_declaration)
                    visited[class_declaration] = (True, main_round)  # .id

            if not_visited:
                queue.append(not_visited[0])

        try:
            main_meth = self.context.get_type("Main").get_method("main", non_rec=True)
            if len(main_meth.param_names) > 0:
                self.errors.append(
                    '"main" method in class Main does not receive any parameters'
                )
            # modify in semantic get_method in order to get some ancestor where the method is already defined
        except SemanticError:
            self.errors.append("A class Main with a method main most be provided")

        # ----------------------------------------------------
        # for declaration in node.declarations:
        #     self.visit(declaration)

    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        # print(f"------------visiting class {node.id}------------")
        self.current_type = self.context.get_type(node.id)

        if node.parent is not None:
            try:
                parent_type = self.get_type(node.parent)
                self.current_type.set_parent(parent_type)
            except SemanticError as error:
                self.errors.append(error.text)
        else:
            object_type = self.context.get_type("Object")
            try:
                self.current_type.set_parent(object_type)
            except SemanticError as error:
                self.errors.append(error.text)

        for feature in node.features:
            self.visit(feature)

    @visitor.when(FuncDeclarationNode)
    def visit(self, node):
        param_names = [fname for fname, ftype in node.params]

        try:
            param_types = [self.get_type(ftype) for fname, ftype in node.params]
            return_type = self.get_type(node.type)
            self.current_type.define_method(
                node.id, param_names, param_types, return_type
            )
        except SemanticError as error:
            # print("--------aqui se esta reportando el error del metodo doble---------")
            self.errors.append(error.text)

    @visitor.when(AttrDeclarationNode)
    def visit(self, node):
        try:
            attr_type = self.get_type(node.type)
            self.current_type.define_attribute(node.id, attr_type)
        except SemanticError as error:
            self.errors.append(error.text)

    def get_type(self, tname):
        try:
            return self.context.get_type(tname)
        except SemanticError as error:
            self.errors.append(error.text)
            return ErrorType()
