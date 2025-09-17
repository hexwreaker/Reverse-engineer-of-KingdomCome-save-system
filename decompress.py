import zlib
import sys


def parse_header(save_datas):
    header = save_datas[:0x20]
    
    save_type_name = ""
    if   int.from_bytes(header[16:20], 'little') == 0:
        save_type_name = "permanent"
    elif int.from_bytes(header[16:20], 'little') == 1:
        save_type_name = "autosave"
    elif int.from_bytes(header[16:20], 'little') == 2:
        save_type_name = "save"
    
    myheader = {
        "head_1":           header[0:4],
        "head_2":           header[4:8],
        "head_3":           header[8:12],
        "head_4":           header[12:16],
        "save_type":        int.from_bytes(header[16:20], 'little'),
        "save_type_name":   save_type_name,
        "save_number":      int.from_bytes(header[20:24], 'little'),
        "save_timestamp":   int.from_bytes(header[24:32], 'little'),
    }
    return myheader

def parse_infos(save_datas, save_type):
    infos = save_datas.split(b'|')
    myinfos = {
        "save_type":        infos[0],
        "save_number":      infos[1],
        "subchapter":       infos[2],
        "objective":        infos[3],
        "location":         infos[4],
        "save_timestamp":   infos[5],
        "save_datetime":    infos[6],
        "playing_time":     infos[7],
        "player_info":      {},
    }
    
    # Classic save format
    infos_header = infos[8]
    if save_type == 2:
        infos_header = infos[8][infos[8].find(b"\xc8"):]
    # Autosave (1) or permanent (0) save format
    else:
        infos_header = infos[9][infos[9].find(b"\xc8"):]
        
    player_info = {
        "a_number_0":  infos_header[:4],
        "a_number_1":  infos_header[4:8],
        "a_number_2":  infos_header[8:9],
        "maybe_number_of_some_objects":  infos_header[9:11],
        "field_5":  infos_header[12:16],
        "field_6":  infos_header[16:20],
        "field_7":  infos_header[20:24],
        "field_8":  infos_header[24:28],
        "field_9":  infos_header[28:30],
        "field_10": infos_header[30:34],
        "field_11": infos_header[34:36],
        "field_12": infos_header[36:40],
        "field_13": infos_header[40:42],
        "field_14": infos_header[42:46],
    }
    myinfos["player_info"] = player_info
    return myinfos

def parse_save(save_datas):
    # Header
    myheader = parse_header(save_datas)
    print(f"Header : ") 
    for key, value in myheader.items():
        print(f"{key}: {value}")
    
    # Infos
    myinfos = parse_infos(save_datas, myheader["save_type"])
    print(f"Infos : ") 
    for key, value in myinfos.items():
        print(f"{key}: {value}")
    print(f"Player infos : ") 
    for key, value in myinfos["player_info"].items():
        print(f"{key}: {value}")
    
def decompress_save(filename):
    datas = open(filename, 'rb').read()

    # skip header (8 bytes)
    stream = datas[8:]
    print(f"- compressed size is \t{len(stream)} bytes")
    dec = b""
    # decompress each blocks
    while stream:
        a = len(stream)
        dco = zlib.decompressobj()
        dec += bytearray(dco.decompress(stream))
        used_datas = a - len(dco.unused_data)
        #print(f"used datas : {used_datas}")
        stream = stream[used_datas+8:]
        if stream[0] != 0x78 and stream[1] != 0x5e:
            break
        #print(stream[:64].hex())

    return dec

if len(sys.argv) != 3:
    print(f"Usage : decompress.py <save_name.whs> <out.datas>")
    exit(0)

print(f"Decompress save '{sys.argv[1]}' to '{sys.argv[2]}'")
dec = decompress_save(sys.argv[1])
print(f"- final size is \t{len(dec)} bytes")
open(sys.argv[2], 'wb').write(dec)


#decomp = bytearray(zlib.decompress(datas[8:]))
#print(hex(zlib.adler32(decomp)))

#parse_save(decomp)

#decomp[0x94] = 0xcb

#comp = zlib.compress(decomp)
#sys.stdout.buffer.write(datas[:8] + comp)


#print(decomp[0x20:].hex())
#sys.stdout.buffer.write(datas[8:])



