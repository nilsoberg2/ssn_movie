#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
from SsnViz.edgelist import parse_xgmml
from SsnViz.edgelist import save_edgelist




parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
     description="See the effect of alignement threshold based on annotation color")

general_option = parser.add_argument_group(title = "General input dataset options")
general_option.add_argument("-i",'--xgmml',
                            metavar="<XGMML>",
                            dest="xgmml",
                            help="XGMML file from the analysis of EFI-EST : https://efi.igb.illinois.edu/efi-est/",
                            required=True)
general_option.add_argument("-o",'--output',
                            dest="output",
                            metavar='<OUTPUT>',
                            help="Name of the output file (default: [NAME_OF_XGMML])",
                            required=True)
general_option.add_argument("-p",'--progress',
                            dest="print_progress",
                            metavar='<PROGRESS>',
                            help="",
                            default=0,
                            required=False)


args = parser.parse_args()
print_progress = None

if args.print_progress:
    progress_inc = 1000000 #int(args.print_progress)
    def print_progress(edge_count):
        if not (edge_count % progress_inc):
            print(f'Num edges processed: {edge_count}')
        return 

(edgelist, ascores_map, node_map) = parse_xgmml(args.xgmml, print_progress)

save_edgelist(args.output, edgelist, node_map)

#, args.output, print_progress)

