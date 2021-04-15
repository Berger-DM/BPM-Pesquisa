from bs4 import BeautifulSoup
import PySimpleGUI as psg
import itertools
import os

flatten = itertools.chain.from_iterable


def BuildTPNFile(path, output):
    # Set filename and location for output file
    filename = path.split('/')[-1].split('.')[0] + '.tpn'
    print(filename)
    output = output.split('/')
    output.append(filename)
    final_file = os.path.sep.join(output)
    print(final_file)
    # Writing into file
    with open(final_file, 'w', encoding='utf8') as final:
        if path.endswith(".xml"):
            BuildFromXML(path, final)
        elif path.endswith(".cpn"):
            BuildFromCPN(path, final)


def BuildFromXML(path, outfile):
    places_list = list()
    transition_dict = dict()
    with open(path, 'rb') as file:  # BeautifulSoup does not accept files with encoding that are not UTF-8, but rb works
        soup = BeautifulSoup(file.read(), 'xml')
        # print(soup.prettify())
        pnml = soup.find('pnml')
        net = pnml.find('net')
        # Get all places in net
        places = net("place")
        places_list = [x.get('id') for x in places]
        # Get all transitions in net
        transitions = net("transition")
        transitions_list = [x.get('id') for x in transitions]
        # Assemble transition information
        for transition in transitions_list:
            # Get places that send arcs to transition
            trans_ins = [x.get("source") for x in net("arc", {"target": transition})]
            # Get palces that receive arcs from transition
            trans_outs = [x.get("target") for x in net("arc", {"source": transition})]
            transition_dict[transition] = (trans_ins, trans_outs)
        '''# Find Birth and Death places - Birth is never target, Death is never source
        # Step 1. Join places and transitions ids
        places_and_transitions = places_list + transitions_list
        # Step 2. Get all targets - to find which of the above is never one (Birth) - and add to transition_dict
        targets = list(flatten(x.get_attribute_list('target') for x in net("arc", {"target": True})))
        print(targets)
        birth = [x for x in places_and_transitions if x not in targets]
        transition_dict['Birth'] = (['GLOBAL_START'], birth)
        # Step 3. Get all sources - to find which of the above is never one (Death) - and add to transition_dict
        sources = list(flatten([x.get_attribute_list('source') for x in net("arc", {"source": True})]))
        print(sources)
        death = [x for x in places_and_transitions if x not in sources]
        transition_dict['Death'] = (death, ['GLOBAL_END'])
        for k, v in transition_dict.items():
            print(k, v)'''
    # Writing in output file
    for place in places_list:
        outfile.write(f"place {place};\n")
    outfile.write("\n")
    for k, v in transition_dict.items():
        outfile.write(f"trans {k}\n")
        outfile.write(f"  in  {', '.join(v[0])}\n")
        outfile.write(f"  out {', '.join(v[1])};\n\n")
    return


def BuildFromCPN(path, outfile):
    places_dict = dict()
    transition_dict = dict()
    with open(path, 'rb') as file:  # BeautifulSoup does not accept files with encoding that are not UTF-8, but rb works
        soup = BeautifulSoup(file.read(), 'xml')
        net = soup.find("workspaceElements").find("cpnet").find("page")
        places = net("place")
        places_dict = {x.get('id'): x.find("text").string for x in places}
        transitions = net("trans")
        transitions_list = [(x.get('id'), x.find("text").string) for x in transitions]
        # Assemble transition information
        for transition in transitions_list:
            trans_ins = [x.find("placeend").get("idref") for x in net("arc", {"orientation": "PtoT"})
                         if x.transend.get("idref") == transition[0]]
            trans_outs = [x.find("placeend").get("idref") for x in net("arc", {"orientation": "TtoP"})
                          if x.transend.get("idref") == transition[0]]
            transition_dict[transition[1]] = ([places_dict[x] for x in trans_ins], [places_dict[x] for x in trans_outs])
    # Writing in output file
    for k, v in places_dict.items():
        outfile.write(f"place {v};\n")
    outfile.write("\n")
    for k, v in transition_dict.items():
        outfile.write(f"trans {k}\n")
        outfile.write(f"  in  {', '.join(v[0])}\n")
        outfile.write(f"  out {', '.join(v[1])};\n\n")
    return


def startGUI():
    gui_layout = [[psg.Text('Choose files to convert:')],
                  [psg.InputText("", size=(70, 10), disabled=True),
                   psg.FilesBrowse(file_types=(("XML Files", "*.xml"),("CPN Files", "*.cpn")))],
                  [psg.Text('Choose location for output file:')],
                  [psg.InputText("", size=(70, 10), disabled=True), psg.FolderBrowse()],
                  [psg.OK("Transform PIPE XML file into Woflan .tpn file", auto_size_button=True)]]
    window = psg.Window('PIPEtoWoflan', layout=gui_layout, disable_close=True)
    while True:
        event, values = window.read()
        if event in (None, 'Transform PIPE XML file into Woflan .tpn file'):
            if values[1] == '':
                psg.popup_ok('Output location must be selected.')
            else:
                break
    pathways = values[0]
    output_location = values[1]
    pathways = pathways.split(';')
    print(pathways)
    for pathway in pathways:
        print(pathway)
        BuildTPNFile(pathway, output_location)
    gui_exit_layout = [[psg.Text("Files have been processed, and outputs will be at specified location.")],
                       [psg.Text("Click 'OK' to finish execution.")],
                       [psg.OK('OK')]]
    window = psg.Window('PIPEtoWoflan - Files Processed', layout=gui_exit_layout,disable_close=True)
    event, values = window.read()


startGUI()