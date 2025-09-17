import idautils
import idc
import ida_segment

dll_target = "WHGame.DLL"

debugger_segments = []
loader_segments = []

def get_dll_segments(dll_name, is_loader):
    segs = []
    for seg in idautils.Segments():
        if "WHGame.DLL" in idc.get_segm_name(seg): # Check name of segment
            if not is_loader and not ida_segment.getseg(seg).is_loader_segm(): # waiting for implementation of "is_debugger_segment" function (see github...). Supposing if t's not a loader seg it's a debugger seg.
                segs.append(seg)
            elif is_loader and ida_segment.getseg(seg).is_loader_segm():
                segs.append(seg)

    return segs

def remove_segments(segments):
    # replaces all segments
    for s in segments:
        print(f"Delete segment at {hex(s)}")
        ida_segment.del_segm(s, SEGMOD_KEEP)

def move_segment(DLL_name, seg_src, base_addr_src, base_addr_dst):
    offset   = seg_src - base_addr_src
    new_addr = base_addr_dst + offset
    print(f"Move {DLL_name} segment at {hex(seg_src)} to {hex(new_addr)}      (offset = {hex(offset)})")
    ida_segment.move_segm(ida_segment.getseg(seg_src), new_addr)
    
def replace_dll_segments(dll_name):

    # get WHGame.DLL loader segments
    segs_L = get_dll_segments("WHGame.DLL", 1)
    whgame_dll_loader_addr_start = segs_L[0]
    print(f"Moving {len(segs_L)} loader segments of {dll_name}")
    print(f"{dll_name} L start address : {hex(whgame_dll_loader_addr_start)}")
    
    # get WHGame.DLL debugger segments
    segs_D = get_dll_segments("WHGame.DLL", 0)
    whgame_dll_debugger_addr_start = segs_D[0]
    print(f"{dll_name} D start address : {hex(whgame_dll_debugger_addr_start)}")    
    
    # Assert that space is enough to move segments
    if (len(segs_L) > len(segs_D)):
        print(f"ERROR ! Space is not enough to copy segments from {hex(whgame_dll_loader_addr_start)} to {hex(whgame_dll_debugger_addr_start)}")
    
    # delete debugger segments
    print(f"Delete all debugger segments of {dll_name}")
    remove_segments(segs_D)

    # move loader segments
    print(f"Move segments from {hex(whgame_dll_loader_addr_start)} to {hex(whgame_dll_debugger_addr_start)}")
    for s in segs_L:
        move_segment(dll_name, s, whgame_dll_loader_addr_start, whgame_dll_debugger_addr_start)
    

def main():
    replace_dll_segments("WHGame.DLL")
    

if __name__ == "__main__":
    main()
