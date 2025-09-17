# Reverse-engineering-of-KingdomCome-save-system
Reverse engineering of the save system of Kingdom Come Deliverance 1. My goal was to modify a save to give my character full perks. I haven't finished and surely will never work on it again, but here are my results.

# Goal

My goal was to modify a save to give my character full perks.  
### Don't judge the way I play games !

# Game

- Launcher is **\Bin\Win64\KingdomCome.exe**
- Game logic is in the dll **\Bin\Win64\WHGame.dll** that is loaded by the launcher

# Content 

- [decompress.py](./decompress.py) : script to decompress a whs save and parse a bunch of it.
- [fix_idb_dll_in_debug_instance.py](fix_idb_dll_in_debug_instance.py) : script to replace all segments of a dynamically loaded DLL into the IDB of the binary - help while debugging.
- [launch_party_save010.CSV](launch_party_save010.CSV) : Call stack when loading a save
- 

# Save system

Save files are in **C:\Users\myUser\Saved Games\kingdomcome\saves\playline0**

![Pasted image 20250619202334.png](./images/Pasted%20image%2020250619202334.png)

**".whs"** format may be **WarHorse Save/Studio** ?

Load modes : 
- Quick load : when the game level is already loaded.

Type of save: 
- 0(permanent save), 
- 1(auto save), 
- 2(manual save), 
- 3(quick save)


In function : **0x7FFDE8A49454**

![Pasted image 20250619202453.png](./images/Pasted%20image%2020250619202453.png)

Saves are browsed and read when the player click on **menu->Charger partie**

When the player click on **Playline2->Save 10** the save is read by another function and the game start.

When a savefile is read by game :
- SUSPICIOUS
- execAFunction
- handleFileRessource (doesn't read the file)

read_ze_file_SUSPICIOUS read file and put in an object that is parse after...  (see CSaveReader_CryPak maybe)

![Pasted image 20250706183527.png](./images/Pasted%20image%2020250706183527.png)

The object is the following structure : 

```c
struct mySaveFileStruct
{
  void *ISaveReader;
  struct
  {
    void *CCryPakFile_vftable;
    struct allocated_obj file_datas;
    char *filepath;
    _QWORD fd;
    _QWORD curr_offset;
    _QWORD is_read_mode;
  };
};

struct allocated_obj
{
  char *start;
  char *end;
  char *a3;
};

```

The "header" (first 7 bytes) and all last datas are read from file and put in file_datas->start

The function responsible for reading save files is **LOAD_SAVES** - 07FFDB6FD9454 (base: 0x7FFDB6880000) or 0x759454.

Each file is read by **read_save** and appears to be decompressed by **SUSPICIOUS_maybe_parse_gamesave**.

# Decompression

The function SUSPICIOUS_maybe_decompress seems to handle the save file data.

The example below uses the save file **autosave003.whs**.

```
00000000  7b 20 00 00 00 80 00 00  78 5e 9d 5d c9 b6 24 c9  |{ ......x^.]..$.|
00000010  51 ad 12 9c c3 42 08 04  88 79 6a 26 31 b4 90 ea  |Q....B...yj&1...|
00000020  4d f5 ba 80 85 fe 41 1f  10 27 32 c3 33 33 5e 46  |M.....A..'2.33^F|
00000030  46 64 c7 90 d9 f9 4e 2d  f8 07 96 fc 0a 2b d8 b0  |Fd....N-.....+..|
00000040  e0 73 60 c5 86 6b 66 3e  87 7b bc 28 e0 54 a9 2b  |.s`..kf>.{.(.T.+|
00000050  ec ba f9 64 66 6e 6e 6e  ee f9 a3 77 ef de fd cf  |...dfnnn...w....|
00000060  fb ff c2 df 3f 78 f7 6f  f8 fb 3d fe fc 12 fe 9c  |....?x.o..=.....|
00000070  ff e3 79 8f ff 79 d7 97  63 f9 a2 de dd 7d 7e f8  |..y..y..c....}~.|
00000080  fc f3 61 da 6c 0f e5 79  54 7d 71 ff e9 9b a2 2d  |..a.l..yT}q....-|
00000090  4f ea f3 cf bb cd 8b da  8e f5 45 15 0f 9f 9e 3e  |O.........E....>|
```

The file header corresponds to the first 8 bytes:

```
00000000  7b 20 00 00 00 80 00 00  -- -- -- -- -- -- -- --
```

The next two bytes are processed by block **16180** and correspond to the following data:

```
00000000  -- -- -- -- -- -- -- --  78 5e 9d 5d c9 b6 24 c9
```

In the code `SUSPICIOUS_maybe_decompress()`, the function checks if the stream begins with a compression header (likely a GZIP header).

These two bytes (0x78, 0x5e) means :
- `0x78` = CMF (Compression Method and Flags): means **"DEFLATE with 32K window size"**, and check bits pass.
- `0x5e` = FLG (Flags): Indicates dictionary usage, compression level, etc.

It try to matches `v13 == 0x8b1f` to detect GZIP
So to confirm it's gzip compressed datas : 

```py
import zlib

datas = open("./autosave003.whs", 'rb').read()
compressed = datas[8:]
decomp = zlib.decompress(compressed)
print(decomp)
```

And we got theses decompressed datas :

```py
b'\x14\x00\x00\x00\xf5\x01\xcc\x00\x00\x00\r\x00\xbc\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00p\xc37g\x00\x00\x00\x00rataje\x001|3|@subchapter_298_name|@objective_39566_Savename|@location_Skalice|1731707760|15/11/2024 22:56|0.065582|\x00@subchapter_298_name|@objective_39566_Savename\x00\xc8\x00\x00\x00\xc8\x00\x00\x00\x00\x00\x00\x10\x00\x04\x00\x00\x00\x01\x00\x00\x00\xf4\x01\x93\x01\x9b\x01\xfb\x01,\x80\x00\x00\x03s&\x80\x00\x00\xc2\x0b \x80\x00\x00+\x02\x0f\x00\x00\x00_matus_fricek\x00\x00+\x02\x0b\x00\x00\x00a_camps_1\x00\x00+\x02\x0b\x00\x00\x00a_camps_2\x00\x00+\x02\x0b\x00\x00\x00a_camps_3\x00\x00+\x02\x18\x00\x00\x00antiquehooker_massacre\x00\x00+\x02\x0f\x00\x00\x00aus_mill_npcs\x00\x01+\x02#\x00\x00\x00burnt_farms_01_rataje_north_burnt\x00\x00+\x02
...'
```

Yummy !

# Save File Format

Using binwalk on the save file, it reveals a sequence of compressed data blocks.

![Pasted%20image%2020250718200007.png](./images/Pasted%20image%2020250718200007.png)

Each decompressed block is 32 KB in size.

![Pasted%20image%2020250718200141.png](./images/Pasted%20image%2020250718200141.png)

The code assert that that a block contains only compressed data by comparing sizes (exactly **32,768 bytes)**.

![Pasted%20image%2020250718200907.png](./images/Pasted%20image%2020250718200907.png)

Only the final block differs in size. Once decompressed, it contains **9,071 bytes**.

Observation shows that the data blocks are contiguous in memory. To reconstruct the save, simply decompress each block and concatenate them in sequence.


# Parsing

The format of a save file is : 

```c
struct save_file
{
	char header[8];
	char gzip_compressed_datas[0xffffffff];
}
```

The format of save datas (uncompressed) is defined in the python script : **decompress.py**.

Like : 

```c
struct save_datas 
{
	int32_t head_1;
	int32_t head_2;
	int32_t head_3;
	int32_t head_4;
	int32_t save_type;
	int32_t save_number;
	int64_t save_timestamp;
	
	struct save_description 
	{
		char save_name[];     'rataje'
		char save_type[2];    '1|'
		char save_number[2];  '5|'
		char subchapter[];    '@subchapter_313_name|'
		char objective[];     '@objective_39606_Savename|'
		char locartion[];     '@location_Skalice|'
		char save_timestamp[];     '1750449822|'
		char save_datetime[];     '20/06/2025 22:03|'
		char playing_time[];     '0.641548|'
	}

}
```

## Listing of the saves

![screen_recorder.gif](./images/screen_recorder.gif)

The following function is called when the player displays the list of saves that can be loaded in the game menu.
It goes through the save files, reads them, and retrieves the description of each save to populate the save list in the game’s interface.

```c
// This function browse save files in C:\Users\User\Saved Games\kingdomcome\saves\playline* (0-7)
// Read all "*.whs" files and parse the description of saves in order to update the savelist in the game UI
__int64 __fastcall UpdateSaveDescriptionsFromsFiles(__int64 a1)
{
  do
  {
    v10 = copy_str_TLS((void **)&v1->bla1[12], "*.whs");
    create_playline_save_fullpath((char *)&v1->bla1[4], (const char **)v10, v8);
      do
      {
        // "wh::framework::C_SaveGameManager::UpdateSaveGameDescriptions"
        v13 = copy_str_TLS((void **)&v1->bla1[14], (char *)&v1->bla[12]);
        create_playline_save_fullpath();
        save_fullpath = v1->save_fullpath;
        MySaveObject = read_a_save_0(v15, v1->save_fullpath);
        if ( MySaveObject ) {
    insert_an_element_in_vector(my_saves_array, &MySaveObject->save_number, -1); 
        }
      }
      while ();
    my_saves_array = (struct std_vector *)((char *)my_saves_array + 56);
  }
  while ( v8 < 7 );
  return 0;
}
```

I wasted a lot of time reversing all the sub-functions before realizing that I was only observing the mechanism for retrieving save descriptions.
The actual save data was not being used, only the metadata.
My work is not lost, however, since the sub-functions are also used in the “Load Save” mechanism, which allows the game to start from a save file.

## Loading a game

The save file is read by the function: **read_ze_file_SUSPICIOUS**

Call stack when loading a save:

```csv
"Frame","Module","Location","Address","Path"
"0","FLTMGR.SYS","FltGetStreamContext + 0x3b18","0xfffff8057540f1a8",
"1","FLTMGR.SYS","FltGetStreamContext + 0x2481","0xfffff8057540db11",
"2","FLTMGR.SYS","FltGetInstanceContext + 0xacc","0xfffff80575413b1c",
"3","FLTMGR.SYS","FltGetInstanceInformation + 0xd81","0xfffff80575469911",
"4","ntoskrnl.exe","NtQueryEaFile + 0xc35","0xfffff805e412dee5",
"5","ntoskrnl.exe","NtReadFile + 0xe6","0xfffff805e404ac06",
"6","ntoskrnl.exe","setjmpex + 0x9235","0xfffff805e3eb8c55",
"7","ntdll.dll","ZwReadFile + 0x14","0x7ffaf8ea1bc4",
"8","KERNELBASE.dll","ReadFile + 0x8d","0x7ffaf624db3d"
"9","ucrtbase.dll","fread_nolock_s + 0x44c","0x7ffaf6048c5c",
"10","ucrtbase.dll","fread_nolock_s + 0x28b","0x7ffaf6048a9b",
"11","ucrtbase.dll","fread_s + 0x5d","0x7ffaf60487ad",
"12","ucrtbase.dll","fread + 0x1b","0x7ffaf604873b",
"13","WHGame.DLL","wh::game::C_Game::CreateInstance + 0xe8fe0","0x7ffa80f90dcc",
"14","WHGame.DLL","wh::game::C_Game::CreateInstance + 0xe5bca","0x7ffa80f8d9b6",
"15","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x79c6d5","0x7ffa816444c1",
"16","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x79c656","0x7ffa81644442",
"17","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x79d657","0x7ffa81645443",
"18","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x79d070","0x7ffa81644e5c",
"19","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x53560d","0x7ffa813dd3f9",
"20","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x600bae","0x7ffa814a899a",
"21","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x60111d","0x7ffa814a8f09",
"22","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x601c10","0x7ffa814a99fc",
"23","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x602c1e","0x7ffa814aaa0a",
"24","WHGame.DLL","wh::game::C_Game::CreateInstance + 0xf477c2","0x7ffa81def5ae",
"25","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x1457d6","0x7ffa80fed5c2",
"26","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x14727b","0x7ffa80fef067",
"27","WHGame.DLL","wh::game::C_Game::CreateInstance + 0x88c","0x7ffa80ea8678",
"28","WHGame.DLL","wh::game::C_Game::CreateInstance + 0xa80","0x7ffa80ea886c",
"29","KingdomCome.exe","KingdomCome.exe + 0x28c5","0x7ff7ea0128c5",
"30","KingdomCome.exe","KingdomCome.exe + 0x3e60","0x7ff7ea013e60",
"31","KingdomCome.exe","KingdomCome.exe + 0x67e3","0x7ff7ea0167e3",
"32","KERNEL32.DLL","BaseThreadInitThunk + 0x17","0x7ffaf7d1e8d7",
"33","ntdll.dll","RtlUserThreadStart + 0x2c","0x7ffaf8d7c34c",
```

Save parsing ? -> PerformSaveLoad

# Dynamic problems encounter

My goal was to reverse static binaries (kingomdCome.exe and WHGame.dll) in the same idb file. This is possible to concatenate the two binaries doing this [method](https://hex-rays.com/blog/several-files-in-one-idb-part-3)
The problem is that the dll will be loaded at a different address sometimes even if the ASLR is disabled. The effect is duplicate of the WHGame.dll in memory and the previously "saved" one is not used by the processus. 
The reason is that addresses of the old and newly created are different.
We can solve this by moving original WHGame.dll segments in place of the fresh newly created one.

Move segments after the new dll is deleted :

![Pasted image 20250624000011.png](./images/Pasted%20image%2020250624000011.png)

I hope it exists a persistent way to achieve this, because it takes some times to move segments in memory. Don't forget to check "Fix up the relocated segments".

![Pasted image 20250625130939.png](./images/Pasted%20image%2020250625130939.png)

To do this automatically I build this IDA python script : [fix_idb_dll_in_debug_instance.py](./fix_idb_dll_in_debug_instance.py)

## Clues and future

### see for more information about ".whs" maybe :

Official Modding Tools update 2 to 3-864-3-0-1581495552$ grep -r "\.whs"
grep: bin/win64releasedll/editordll.dll: binary file matches
grep: bin/win64releasedll/framework.dll: binary file matches

### future of the RE

I haven't finished and surely will never work on it again.
But I hope my work could help someone else for continuing the job.

Enjoy and play hard !

