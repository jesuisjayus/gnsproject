import json
from datetime import datetime

with open("routeurs-data2.json") as file:
    data = json.load(file)


for autonomous_system in data["AS"]:

    AS=autonomous_system["AS_id"]
    protocole=autonomous_system["protocole_routage"] + " " + autonomous_system["nom_protocole"]

    for routeur in autonomous_system["routeur"]:

        header = open("header.txt")
        header2 = open("header2.txt")
        header3 = open("header3.txt")
        header4 = open("header4.txt")

        nomRouteur=routeur["nom_routeur"]

        myFile = open("i" + str(routeur["nom_routeur"]) + "_startup-config.cfg", "w+")
        myFile.write(header.read() + "\nhostname R" + routeur["nom_routeur"] + "\n!\n" + header2.read())

        #conf des interfaces
        for interface in routeur["interfaces"]:
            nom = "interface "+interface["int_name"]+"\n"
            noIP = " no ip address\n"
            negAuto = " negotiation auto\n"
            myFile.write(nom+noIP)
            if(interface["int_name"]=="Loopback0"):
                ip=" ipv6 address "+interface["plage_ip"]+nomRouteur+"::"+nomRouteur+interface["masque"]+"\n"
                ipv6=" ipv6 enable\n"
                if autonomous_system["protocole_routage"] == "rip":
                    prot=" ipv6 "+protocole+" enable\n"
                    myFile.write(ip+ipv6+prot+"!\n")
                elif(autonomous_system["protocole_routage"] == "ospf"):
                    prot = " ipv6 " + protocole + " area 0\n"
                    myFile.write(ip + ipv6 + prot + "!\n")
            elif(interface["plage_ip"]!=""):
                ip=" ipv6 address "+interface["plage_ip"]+nomRouteur+interface["masque"]+"\n"
                ipv6=" ipv6 enable\n"
                if(autonomous_system["protocole_routage"] == "rip"):
                    prot=" ipv6 "+protocole+" enable\n"
                    myFile.write(negAuto+ip+ipv6+prot+"!\n")
                elif(autonomous_system["protocole_routage"] == "ospf"):
                    prot = " ipv6 " + protocole + " area 0\n"
                    if(interface["cost"] != "") | (interface["int_name"] != "Loopback0")| (interface["cost"] != "default") :
                        cost = " ipv6 ospf cost "+interface["cost"]+"\n" # A voir si faut mettre sur l'interface ospf des asbr
                        myFile.write(negAuto+ip + ipv6 + prot + cost+"!\n")
                    else:
                        myFile.write(negAuto + ip + ipv6 + prot + "!\n")
            else:
                if(interface["int_name"]=="FastEthernet0/0"):
                    myFile.write(" shutdown\n duplex full\n!\n")
                else:
                    myFile.write(" shutdown\n negotiation auto\n!\n")

        #conf de BGP-----
        #on set les voisins
        bgpConf="router bgp "+AS+"\n"+" bgp router-id "+routeur["routeur_id"]+"\n bgp log-neighbor-changes\n no bgp default ipv4-unicast\n"
        myFile.write(bgpConf)
        for i in autonomous_system["routeur"]:
            if(i["nom_routeur"]!=nomRouteur):
                ip="2001:100:"+AS+":A"+i["nom_routeur"]+"::"+i["nom_routeur"]
                myFile.write(" neighbor "+ip+" remote-as "+AS+"\n neighbor "+ip+" update-source Loopback0\n")

        #SI ASBR
        if(routeur["ASBR"][0]["neighbor_as"]!=""):
            for neighbor in routeur["ASBR"]:
                myFile.write(" neighbor "+neighbor["neighbor_address"]+" remote-as "+(neighbor["neighbor_as"])+"\n")

        #on active les voisins et on advertise les networks
        myFile.write(" !\n address-family ipv4\n exit-address-family\n !\n address-family ipv6\n")
        for i in autonomous_system["routeur"]:
            if(i["nom_routeur"]!=nomRouteur):
                for interface in i["interfaces"]:
                    if(interface["int_name"]=="Loopback0"):
                        ip=interface["plage_ip"]+i["nom_routeur"]+"::"+i["nom_routeur"]
                myFile.write("  neighbor "+ip+" activate\n")
                myFile.write("  neighbor "+ip+" send-community\n")

        #SI ASBR verifier avec R6 et R7 si ça marche
        if(routeur["ASBR"][0]["neighbor_as"]!=""):
            for neighbor in routeur["ASBR"]:
                neighborRR = "  neighbor "+neighbor["neighbor_address"]+" activate\n"
                myFile.write(neighborRR)
                neighborBis = "  neighbor "+neighbor["neighbor_address"]+" send-community\n"
                myFile.write(neighborBis)
            for i in range(0,len(neighbor["network_advertisement"])):
                network = "  network "+neighbor["network_advertisement"][i]+"\n"
                myFile.write(network)
            redistribute = "  redistribute "+protocole+" \n"
            myFile.write(redistribute)

        myFile.write(header3.read())

        myFile.write("ipv6 router " + protocole + "\n")

        if ((autonomous_system["protocole_routage"] == "ospf")):
            myFile.write(" router-id " + routeur["routeur_id"] + "\n")

        if (autonomous_system["protocole_routage"] == "rip") | (routeur["ASBR"][0]["neighbor_as"] != ""):
            myFile.write(" redistribute connected\n!\n")

        myFile.write(header4.read())

        myFile.close()
