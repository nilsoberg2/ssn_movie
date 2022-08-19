
import os
import re
import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from itertools import cycle
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


class SsnViz:
    def __init__(self, plot_title = ""):
        self.something = 1
        self.plot_title = plot_title


    def load_color_file(self, file_path):
        self.colors = []
        try:
            cfile = open(file_path, 'r')
        except Exception as ex:
            return False, str(ex)

        for line in cfile:
            parts = re.split("\t", line.strip())
            self.colors.append(parts[1])

        return True, ""


    def create_folder(self, mypath):

        """
        Created the folder that I need to store my result if it doesn't exist
        :param mypath: path where I want the folder (write at the end of the path)
        :type: string
        :return: Nothing
        """

        try:
            os.makedirs(mypath)
        except OSError:
            pass

        return


    def get_color_cmap(self, name, n_colors=6):

        """
        Return discrete colors from a matplotlib palette.

        :param name: Name of the palette. This should be a named matplotlib colormap.
        :type: str
        :param n_colors: Number of discrete colors in the palette.
        :type: int
        :return: List-like object of colors as hexadecimal tuples
        :type: list
        """

        brewer_qual_pals = {"Accent": 8, "Dark2": 8, "Paired": 12,
                            "Pastel1": 9, "Pastel2": 8,
                            "Set1": 9, "Set2": 8, "Set3": 12, 'tab20':20, 'tab20b':20}


        if name == 'tab20' and n_colors > 19:
            second = 'tab20b'
            ncolor2 = n_colors - 19
            n_colors = 19
        else :
            second = False

        cmap = getattr(cm, name)

        if name in brewer_qual_pals:
            bins = np.linspace(0, 1, brewer_qual_pals[name])
            if 'tab20' == name :
                len_bins = len(bins)
                bins = [bins[i] for i in range(len_bins) if i != 14][:n_colors]
            else :
                bins = bins[:n_colors]
        else:
            bins = np.linspace(0, 1, n_colors + 2)[1:-1]

        palette = list(map(tuple, cmap(bins)[:, :3]))

        if second :
            cmap = getattr(cm, second)
            bins = np.linspace(0, 1, brewer_qual_pals[second])[:ncolor2]
            palette += list(map(tuple, cmap(bins)[:, :3]))

            pal_cycle = cycle(palette)
            palette = [next(pal_cycle) for _ in range(n_colors+ncolor2)]
        else :
            pal_cycle = cycle(palette)
            palette = [next(pal_cycle) for _ in range(n_colors)]

        return [colors.rgb2hex(rgb) for rgb in palette]


    # Public
    # Use to plot general purpose SSNs
    def plot_graph(self, graph, output):

        colors = self.get_colors_by_cluster()

        retval = self.graph_elements(graph, colors, "lightgrey")
        if not retval:
            return False

        retval = self.graph_finish(output)
        if not retval:
            return False

        return True


    # Public
    # Original, from Remi 2
    def plot_anno_graph(self, graph, output, threshold, all_hit_id = None, annot_df = None, hit_id2node = None) :

        show_anno, tmp_color, dict_color = self.get_anno_colors(all_hit_id, annot_df, hit_id2node)

        self.remove_edges(graph, threshold)

        retval = self.graph_elements(graph, dict_color)
        if not retval:
            return False

        if show_anno:
            custom_lines = []
            custom_text = []
            for gene, color in tmp_color.items() :
                custom_text.append(gene)
                custom_lines.append(Line2D(range(1), range(1), color="white", marker='o', markerfacecolor=color, linestyle='none'))
            plt.legend(custom_lines, custom_text, bbox_to_anchor=(1.05, 1), loc='upper left', prop={"size":'xx-small'})
            #Label drawing as well
            # nx.draw_networkx_labels(graph,pos,font_size=8)

        retval = self.graph_finish(output)

        if not retval:
            return False

        return True


    def get_anno_colors(self, all_hit_id, annot_df, hit_id2node):
        show_anno = all_hit_id is not None and annot_df is not None and hit_id2node is not None

        if show_anno:
            annot_df = annot_df[annot_df.Hit_Id.isin(all_hit_id)]
            all_gene = annot_df.Gene.unique()
            num_gene = all_gene.shape[0]
            all_gene = sorted(all_gene)

            palette = self.get_color_cmap("tab20", n_colors = num_gene)
            tmp_color = {all_gene[i]:palette[i] for i in range(num_gene)}

            hit_id2gene = annot_df.set_index('Hit_Id').Gene.to_dict()

            dict_color = {}
            for hit_id in all_hit_id :
                if hit_id in hit_id2gene :
                    dict_color[hit_id2node[hit_id]] = tmp_color[hit_id2gene[hit_id]]
                else :
                    dict_color[hit_id2node[hit_id]] = 'grey'

        return show_anno, tmp_color, dict_color


    def remove_edges(self, graph, threshold):
        edge2remove = []
        # Parsing the edges
        for n1, n2, edge_dict in graph.edges.data() :
            #if edge_dict['ascore'] >= threshold :
            #    graph.edges[(n1, n2)]["color"] = "lightgrey"
            #else :
            if edge_dict['ascore'] < threshold :
                edge2remove.append((n1, n2))

        for e in edge2remove :
            graph.remove_edge(*e)

    # Private
    def graph_elements(self, graph, dict_color = None, edge_color = None, shared_color = "black") :

        graph = graph.to_undirected()

        # Choose between : dot, neato, fdp, sfdp, twopi, circo
        try:
            pos = graphviz_layout(graph, prog="sfdp")
        except OSError as e:
            print("ERROR: Failed to layout: " + str(e))
            return False

        plt.figure(figsize=(12,12))

        # Put the color of the node
        the_colors = None
        if dict_color is not None:
            nx.set_node_attributes(graph, dict_color, "color")
            # Color nodes
            nodes, the_colors = zip(*nx.get_node_attributes(graph,'color').items())
        else:
            the_colors = shared_color
        nx.draw_networkx_nodes(graph, pos, node_size=100, node_color=the_colors, linewidths=0.5, edgecolors="black")

        # Color edges
        if edge_color is not None:
            #edges,edge_colors = zip(*nx.get_edge_attributes(graph,'color').items())   
            #edges = zip(*nx.get_edges(graph).items())   
            nx.draw_networkx_edges(graph, pos, edgelist=graph.edges, edge_color=edge_color)
        else:
            nx.draw_networkx_edges(graph, pos)

        return True


    # Private
    def graph_finish(self, output):

        plt.axis('off')
        plt.tight_layout()

        if self.plot_title:
            plt.title(self.plot_title)

        if output!=None:
            plt.savefig(output.replace("graphml", "pdf"), dpi=300, bbox_inches='tight')

        plt.close('all')

        return True


    def create_graph(self, edgelist, node_map):
        G = nx.Graph()
        for edge in edgelist:
            G.add_edge(edge[0], edge[1], ascore = edge[2])
        self.G = G
        self.node_map = node_map
        return G

    
    def get_colors_by_cluster(self):
        
        color_dict = {}
        for node_id in self.node_map.keys():
            color_dict[node_id] = self.node_map[node_id][1]

        return color_dict

