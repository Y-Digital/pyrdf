"""Console script for graph_cli."""
import argparse
import logging
from rdflib import Graph
import sys
import glob
from pyshacl import validate


def main():
    """Console script for graph_cli."""
    logging.basicConfig()
    logger = logging.getLogger()
    graph = Graph()
    sg = Graph()
    parser = argparse.ArgumentParser()
    inputgroup = parser.add_mutually_exclusive_group(required=True)
    inputgroup.add_argument(
        "files", action="store", nargs='*', default=[],
        help="Use specific files as input")
    inputgroup.add_argument(
        "-r", "--recursive", action="store_true", default=False,
        help="Use all ttl files in subdirectories")
    actiongroup = parser.add_mutually_exclusive_group(required=True)
    actiongroup.add_argument(
        "-q", "--query", action="store", default=None,
        help="SPARQL query")
    actiongroup.add_argument(
        "-s", "--schema", action="store", default=None,
        help="Schema to validate with")
    actiongroup.add_argument(
        "-g", "--graph", action="store", default=None,
        help="Return results graph")
    parser.add_argument(
        "-o", "--output", action="store", default="turtle",
        help="Output format")
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="Verbose logging")
    cmdline_args = parser.parse_args()

    if cmdline_args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if cmdline_args.recursive:
        ttlfiles = [f for f in glob.glob('./**/*.ttl', recursive=True)]
        for f in ttlfiles:
            graph.parse(f, format='ttl')
    elif len(cmdline_args.files) > 0:
        for f in cmdline_args.files:
            graph.parse(f, format='ttl')
    else:
        logger.error(
            "Either provide input files with -f or provide the recursive switch -r.")
        sys.exit(1)

    if cmdline_args.schema is not None:
        sg.parse(cmdline_args.schema, format="ttl")
        r = validate(graph, shacl_graph=sg,  inference='rdfs', abort_on_error=False,
                     meta_shacl=True, advanced=True, js=False, debug=False)
        conforms, results_graph, results_text = r
        print(results_text)
    else:
        q = open(cmdline_args.query, 'r').read()
        if ("CONSTRUCT" in q) | (cmdline_args.output in ["csv", "json", "txt", "xml"]):
            print(graph.query(q).serialize(
                format=cmdline_args.output).decode("utf-8"))
        elif ("ASK" in q):
            if graph.query(q):
                print("true")
            else:
                print("false")
        else:
            logger.error("Unsupported output format")
            sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
