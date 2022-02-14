import inspect
import os
from typing import List, NoReturn, Any, Tuple
import ast
import _ast
import astunparse
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout


class AstDrawer(ast.NodeVisitor):
    class AstVisitor(ast.NodeVisitor):
        def __init__(self):
            self.nodes = []
            self.colors = []
            self.edges = []
            self.edge_labels = {}

            self.parent_index = -1
            self.parent_edge_label = ""

        def generic_visit(self, node: _ast.AST) -> Any:
            print("log: skipped " + str(type(node)))
            ast.NodeVisitor.generic_visit(self, node)

        def __visit_known_node(self, label: str, children: List[Tuple[str, _ast.AST]], color: str) -> NoReturn:
            self.nodes.append(label)
            self.colors.append(color)
            node_index = len(self.nodes) - 1

            node_parent_index = self.parent_index
            node_parent_edge_label = self.parent_edge_label
            if node_parent_index != -1:
                edge = (node_parent_index, node_index)
                self.edges.append(edge)
                self.edge_labels[edge] = node_parent_edge_label

            self.parent_index = len(self.nodes) - 1
            for (edge_label, child) in children:
                self.parent_edge_label = edge_label
                self.visit(child)
            self.parent_index = node_parent_index
            self.parent_edge_label = node_parent_edge_label

        @staticmethod
        def __zip_edge_label(edge_label: str, children: List[_ast.AST]) -> List[Tuple[str, _ast.AST]]:
            return list(zip([edge_label for _ in range(len(children))], children))

        def visit_Module(self, node: _ast.Module) -> Any:
            label = "Module"
            self.__visit_known_node(label, self.__zip_edge_label("body", node.body), "orange")

        def visit_FunctionDef(self, node: _ast.FunctionDef) -> Any:
            label = "FunctionDef\nname: " + node.name
            self.__visit_known_node(label, self.__zip_edge_label("body", node.body), "mediumorchid")

        def visit_Return(self, node: _ast.Return) -> Any:
            label = "Return"
            self.__visit_known_node(label, [("value", node.value)], "darkgray")

        def visit_BinOp(self, node: _ast.BinOp) -> Any:
            label = "BinOp\nop: " + astunparse.dump(node.op)
            self.__visit_known_node(label, [("left", node.left), ("right", node.right)], "palegreen")

        def visit_UnaryOp(self, node: _ast.UnaryOp) -> Any:
            label = "UnaryOp\nop: " + astunparse.dump(node.op)
            self.__visit_known_node(label, [("operand", node.operand)], "palegreen")

        def visit_Name(self, node: _ast.Name) -> Any:
            label = "Variable\nname: " + node.id
            self.__visit_known_node(label, [], "skyblue")

        def visit_Constant(self, node: _ast.Constant) -> Any:
            label = "Constant\nvalue: " + str(node.value)
            self.__visit_known_node(label, [], "khaki")

        def visit_For(self, node: _ast.For) -> Any:
            label = "For"
            self.__visit_known_node(label, [("target", node.target)]
                                    + [("iter", node.iter)]
                                    + self.__zip_edge_label("body", node.body), "gold")

        def visit_If(self, node: _ast.If) -> Any:
            label = "If"
            self.__visit_known_node(label, [("test", node.test)]
                                    + self.__zip_edge_label("body", node.body)
                                    + self.__zip_edge_label("else", node.orelse), "gold")

        def visit_List(self, node: _ast.List) -> Any:
            label = "List"
            self.__visit_known_node(label, self.__zip_edge_label("elements", node.elts), "skyblue")

        def visit_Subscript(self, node: _ast.Subscript) -> Any:
            label = "Subscript"
            self.__visit_known_node(label, [("value", node.value), ("slice", node.slice)], "skyblue")

        def visit_Assign(self, node: _ast.Assign) -> Any:
            label = "Assign"
            self.__visit_known_node(label, self.__zip_edge_label("target", node.targets)
                                    + [("value", node.value)], "palegreen")

        def visit_Compare(self, node: _ast.Compare) -> Any:
            label = "Compare"
            self.__visit_known_node(label, [("left", node.left)]
                                    + self.__zip_edge_label("ops", node.ops)
                                    + self.__zip_edge_label("comparators", node.comparators), "palegreen")

        def visit_Eq(self, node: _ast.Eq) -> Any:
            label = "Eq: =="
            self.__visit_known_node(label, [], "palegreen")

        def visit_Call(self, node: _ast.Call) -> Any:
            label = "Call"
            self.__visit_known_node(label, [("func", node.func)]
                                    + self.__zip_edge_label("args", node.args)
                                    + self.__zip_edge_label("keywords", node.keywords), "orchid")

        def visit_Attribute(self, node: _ast.Attribute) -> Any:
            label = "Attribute\nattr: " + node.attr
            self.__visit_known_node(label, [("value", node.value)], "plum")

        def visit_Expr(self, node: _ast.Expr) -> Any:
            label = "Expr"
            self.__visit_known_node(label, [("value", node.value)], "palegreen")

    @staticmethod
    def draw(code: str) -> NoReturn:
        visitor = AstDrawer.AstVisitor()
        visitor.visit(ast.parse(code))

        labels = {i: visitor.nodes[i] for i in range(len(visitor.nodes))}
        node_colors = visitor.colors
        edges = visitor.edges
        edge_labels = visitor.edge_labels

        graph = nx.DiGraph()
        graph.add_edges_from(edges)

        plt.figure(figsize=(30, 25))
        pos = graphviz_layout(graph, prog="dot")  # need graphviz installed
        nx.draw(graph, node_color=node_colors, pos=pos, labels=labels, with_labels=True,
                font_size=12, node_shape="s", node_size=[len(labels[i]) * 400 for i in pos])
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

        filename = "artifacts/ast.png"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename)


def gen_fibs(n: int) -> List[int]:
    # """Generate first fibonacci numbers up to n-th inclusive starting from zero"""
    if n == 0:
        return [0]
    if n == 1:
        return [1]
    fibs = [0, 1]
    for _ in range(n - 1):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs


def draw_fibs_ast() -> NoReturn:
    drawer = AstDrawer()
    drawer.draw(inspect.getsource(gen_fibs))


if __name__ == '__main__':
    draw_fibs_ast()
