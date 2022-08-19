
import re

def parse_xgmml(xgmml_file, print_progress = None):
    #edge_count = 0
    source = ""
    target = ""
    ascore = 0
    node_id = ""
    cluster_num = 0
    cluster_color = ""
    edgelist = []
    ascores_map = {}
    node_map = {}
    #cluster_colors = {}

    with open(xgmml_file, 'rb') as r_file :
        for line in r_file:
            line = line.strip().decode('utf-8')

            #result = re.search('<node.*label="([^"]+)"', line)
            result = re.search('<node id="([^"]+)"', line)
            if result:
                node_id = result.groups()[0]
                continue
            #<att name="Node Count Cluster Number" type="integer" value="2" />
            result = re.search('<att.*name="Node Count Cluster Number".*value="(\d+)"', line)
            if result:
                cluster_num = result.groups()[0]
                if cluster_color:
                    #cluster_colors[cluster_num] = cluster_color
                    node_map[node_id] = [cluster_num, cluster_color]
                    cluster_num = 0
                    cluster_color = ""
                continue
            #"Node Count Fill Color"
            result = re.search('<att.*name="Node Count Fill Color".*value="([^"]+)"', line)
            if result:
                cluster_color = result.groups()[0]
                if cluster_num:
                    #cluster_colors[cluster_num] = cluster_color
                    node_map[node_id] = [cluster_num, cluster_color]
                    cluster_num = 0
                    cluster_color = ""
                continue

            #<edge id="A0A1G1M2D7,A0A3N5M8J3" target="A0A3N5M8J3" label="A0A1G1M2D7,A0A3N5M8J3" source="A0A1G1M2D7"
            result = re.search('<edge.*source="([^"]+)"', line)
            if result:
                source = result.groups()[0]
            result = re.search('<edge.*target="([^"]+)"', line)
            if result:
                target = result.groups()[0]
    
            #<att name="alignment_score" type="real" value="12" />
            result = re.search('<att.*name="alignment_score".*value="([0-9]+)(\.\d+)?"', line);
            if result:
                ascore = result.groups()[0]
                continue
    
            result = re.search('</edge>', line)
            if result and source and ascore:
                ascores_map[ascore] = 1
                edgelist.append([source, target, ascore])
                source = ""
                target = ""
                ascore = 0

                if print_progress is not None:
                    print_progress(edge_count)
    
    return (edgelist, ascores_map, node_map)


def save_edgelist(out_file, edgelist, node_map = None):
    try:
        fh = open(out_file, 'w')
    except Exception as ex:
        return False

    if node_map is None:
        node_map = {}

    for edge in edgelist:
        snode = edge[0]
        enode = edge[1]
        ascore = edge[2]
        out_parts = [snode, enode, ascore]
        if snode in node_map: # don't need to check enode because they are in the same cluster
            out_parts.append(node_map[snode][1])
            out_parts.append(node_map[snode][0])
        out_line = " ".join(out_parts)
        fh.write(out_line + "\n")


def load_edgelist(edgelist_file):
    #edge_count = 0
    ascores_map = {}
    node_map = {}
    edgelist = []

    try:
        fh = open(edgelist_file, 'r')
    except Exception as ex:
        return None

    for line in fh:
        line = line.strip()
        result = re.split(' ', line)
        n1 = result[0]
        n2 = result[1]
        node_map[n1] = [1, ""]
        node_map[n2] = [1, ""]
        ascore = int(result[2])
        #G.add_edge(n1, n2, ascore = ascore)
        edgelist.append([n1, n2, ascore])
        ascores_map[ascore] = 1
        if len(result) > 3:
            color = result[3]
            node_map[n1][1] = color
            node_map[n2][1] = color
        if len(result) > 4:
            cluster_num = result[4]
            node_map[n1][0] = cluster_num
            node_map[n2][0] = cluster_num
        #edge_count = edge_count + 1
        #if not (edge_count % 1000000):
        #    print(f'Num edges loaded from edgelist file: {edge_count:,}')
    return (edgelist, ascores_map, node_map)


## Reads an XGMML file line by line to get the edge list, rather than parsing using
## XML libraries.  This is important because files can get large.
#def xgmml_to_edgelist(xgmml_file, out_file, print_progress = 0):
#    try:
#        output = open(out_file, 'w')
#    except Exception as ex:
#        print("Unable to open " + out_file + " for reading: " + str(ex))
#        return False
#
#    try:
#        r_file = open(xgmml_file, 'rb')
#    except Exception as ex:
#        print("Unable to open " + xgmml_file + " for writing: " + str(ex))
#        return False
#
#    edge_count = 0
#    source = ""
#    target = ""
#    ascore = 0
#    for line in r_file:
#        line = line.strip().decode('utf-8')
#        #<edge id="A0A1G1M2D7,A0A3N5M8J3" target="A0A3N5M8J3" label="A0A1G1M2D7,A0A3N5M8J3" source="A0A1G1M2D7"
#        result = re.search('<edge.*source="([^"]+)"', line)
#        if result:
#            source = result.groups()[0]
#        result = re.search('<edge.*target="([^"]+)"', line)
#        if result:
#            target = result.groups()[0]
#    
#        #<att name="alignment_score" type="real" value="12" />
#        result = re.search('<att.*name="alignment_score".*value="([0-9]+)"', line);
#        if result:
#            ascore = result.groups()[0]
#    
#        result = re.search('</edge>', line)
#        if result and source and ascore:
#            output.write(source + " " + target + " " + ascore + "\n")
#            source = ""
#            target = ""
#            ascore = 0
#            edge_count = edge_count + 1
#            if print_progress and not (edge_count % print_progress):
#                print(f'Num edges processed: {edge_count}')
#    
#    return True

