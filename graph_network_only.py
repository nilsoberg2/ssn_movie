#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import os.path
from SsnViz.SsnViz import SsnViz
from SsnViz.edgelist import parse_xgmml
from SsnViz.edgelist import load_edgelist



parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
     description="See the effect of alignement threshold based on annotation color")

general_option = parser.add_argument_group(title = "General input dataset options")
general_option.add_argument("-e","--edgelist",
                            metavar="<EDGELIST>",
                            dest="edgelist",
                            help="edgelist",
                            required=False)
general_option.add_argument("-x","--xgmml",
                            metavar="<XGMML>",
                            dest="xgmml",
                            help="xgmml",
                            required=False)
general_option.add_argument("-o","--output",
                            default=None,
                            dest="output",
                            metavar="<OUTPUT>",
                            help="Name of the output file (default: [NAME_OF_XGMML])")
general_option.add_argument("-n","--num-iter",
                            default=1,
                            dest="num_iter",
                            metavar="<NUM_ITER>",
                            help="Number of times to run the script (for testing)")
general_option.add_argument("-i","--ascore-inc",
                            default=1,
                            dest="ascore_inc",
                            metavar="<ASCORE_INC>",
                            help="Increment to use between alignment score image generation")
general_option.add_argument("-d","--debug",
                            default=False,
                            dest="debug_mode",
                            metavar="<DEBUG_MODE>",
                            help="Enable debug printing")
general_option.add_argument("-c","--color-file",
                            dest="color_file",
                            metavar="<COLOR_FILE>",
                            help="Path to file containing cluster colors (EFI-EST)")



args = parser.parse_args()
if not args.xgmml and not args.edgelist:
    print("Error: require either the xgmml file or an edgelist")
    quit()
if not args.output:
    print("Error: require output")
    quit()


num_iter = int(args.num_iter)
ascore_inc = int(args.ascore_inc)
debug_mode = args.debug_mode
output_file = args.output


if args.edgelist and os.path.exists(args.edgelist):
    edgelist, ascores_map, node_map = load_edgelist(args.edgelist)
elif args.xgmml and os.path.exists(args.xgmml):
    edgelist, ascores_map, node_map = parse_xgmml(args.xgmml)


if edgelist is None:
    print("Failed to load input file")
    quit()


if len(node_map) == 0:
    print("No clusters have been numbered, so we need to exit")
    quit()


ssnviz = SsnViz("")

if args.color_file and os.path.exists(args.color_file):
    status, msg = ssnviz.load_color_file(args.color_file)
    if not status:
        print("Unable to read color file " + args.color_file + ": " + msg)


G = ssnviz.create_graph(edgelist, node_map)

ssnviz.plot_graph(G, output_file)



