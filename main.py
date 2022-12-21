import jsonc_decoder
import json
from os import path, chdir


def main():
    global sounds_data_path
    global vanilla_blocks_path
    global backup_file_path
    sounds_data_path = path.join('data', 'sounds_data.json')
    vanilla_blocks_path = path.join('vanilla_data', 'blocks.json')
    backup_file_path = path.join('data', 'backup_sounds_data.json')
    print('What do you want to create?\na - axe\np - pickaxe\nh - hoe\ns - shovel\nu - update options.')
    selected_mode = ''
    while selected_mode not in ['a', 'p', 's', 'h', 'u']:
        selected_mode = input('Mode: ')
    if selected_mode == 'u':
        print('Data options.\nWhat you want to update?\n1 - tool sounds\n2 - exclude list\n3 - add new sounds\n4 - all data.')
        data_option = 0
        while data_option not in range(1, 5):
            data_option = int(input())
        if data_option == 1:
            print('Sounds of what tool you want to reset?\n[a, p, s, h]')
            selected_tool = ''
            while selected_tool not in ['a', 'p', 's','h']:
                selected_tool = input()
            tool = get_tool_name(selected_tool)
            update_sound_group(tool)
        elif data_option == 2:
            print('What exclude list you want to update?\n[a, p, s, h]')
            selected_list = ''
            while selected_list not in ['a', 'p', 's', 'h']:
                selected_list = input()
            tool = get_tool_name(selected_list)
            update_exclude_group(tool)
        elif data_option == 3:
            add_new_sounds()
        elif data_option == 4:
            print("Are you sure you want to update all data?\n(Old data will be in backup file.)\nType 'yes' to continue.")
            if input() == 'yes':
                update_data()
            else:
                print('Data update has been cancelled.')
                main()
    else:
        speed = int(input('Destroy speed: '))
        event = input('on_dig event: ')
        tool = get_tool_name(selected_mode)
        create_component_data(tool, speed, event)

def create_component_data(tool: str, destroy_speed: int, on_dig_event: str):
    print(f'Creating {tool}...')
    with open(sounds_data_path, 'r') as sounds_data_file:
        sounds_data = json.load(sounds_data_file, cls=jsonc_decoder.JSONCDecoder)
    with open(vanilla_blocks_path, 'r') as vanilla_blocks_file:
        blocks_data = json.load(vanilla_blocks_file, cls=jsonc_decoder.JSONCDecoder)
    if path.exists(path.join('custom_data', 'blocks.json')):
        try:
            with open(path.join('custom_data', 'blocks.json')) as custom_blocks_data_file:
                custom_blocks_data = json.load(custom_blocks_data_file, cls=jsonc_decoder.JSONCDecoder)
        except:
            print('Something is wrong with custom blocks.json')
            custom_blocks_data = {}
        blocks_data |= custom_blocks_data
    digger_component = {'destroy_speeds':[],'on_dig':{}}
    digger_component['on_dig']['event'] = on_dig_event
    for block, block_data in blocks_data.items():
        if type(block_data) == dict and block_data.get('sound', '') in sounds_data[tool] and block not in sounds_data[f'{tool}_exclude'] and block not in sounds_data['exclude']:
            destroy_data = {}
            destroy_data['block'] = block
            destroy_data['speed'] = destroy_speed
            destroy_data['on_dig'] = {}
            destroy_data['on_dig']['event'] = on_dig_event
            digger_component['destroy_speeds'].append(destroy_data)
    for block in sounds_data[f'{tool}_add']:
        destroy_data = {}
        destroy_data['block'] = block
        destroy_data['speed'] = destroy_speed
        destroy_data['on_dig'] = {}
        destroy_data['on_dig']['event'] = on_dig_event
        digger_component['destroy_speeds'].append(destroy_data)
    with open('output.txt', 'w') as output_file:
        output_file.write('"minecraft:digger": '+json.dumps(digger_component, indent=4))
    print('Done!')

def get_tool_name(tool: str) -> str:
    if tool == 'a':
        tool = 'axe'
    elif tool == 'p':
        tool = 'pickaxe'
    elif tool == 's':
        tool = 'shovel'
    elif tool == 'h':
        tool = 'hoe'
    return tool

def update_sound_group(tool: str):
    """Update sounds of one tool"""
    with open(sounds_data_path, 'r') as sounds_data_file:
        sounds_data = json.load(sounds_data_file, cls=jsonc_decoder.JSONCDecoder)
    with open(backup_file_path, 'w') as backup_sounds_data_file:
        json.dump(sounds_data, backup_sounds_data_file, indent=4)
    sounds_data[tool] = []
    with open(vanilla_blocks_path, 'r') as vrp_blocks_json:
        vrp_blocks_data = json.load(vrp_blocks_json, cls=jsonc_decoder.JSONCDecoder)
    sounds = []
    for block_data in vrp_blocks_data.values():
        if type(block_data) == dict and block_data.get('sound', '') not in sounds:
            sounds.append(block_data.get('sound', ''))
    sounds.remove('')
    print("Add block sounds to tool via typing 'a', use 'x' to skip.")
    for sound in sorted(sounds):
        print(sound)
        add = input()
        while add not in ['a', 'x']:
            add = input()
        if add == 'a':
            sounds_data[tool].append(sound)
    with open(sounds_data_path, 'w') as sounds_data_file:
        json.dump(sounds_data, sounds_data_file, indent=4)
    print(f'Successfully updated {tool} sounds.')

def update_exclude_group(tool: str):
    """Update excluded blocks for one tool"""
    tool_group = tool + '_exclude'
    with open(sounds_data_path, 'r') as sounds_data_file:
        sounds_data = json.load(sounds_data_file, cls=jsonc_decoder.JSONCDecoder)
    with open(backup_file_path, 'w') as backup_sounds_data_file:
        json.dump(sounds_data, backup_sounds_data_file, indent=4)
    sounds_data[tool_group] = []
    with open(vanilla_blocks_path, 'r') as vrp_blocks_json:
        vrp_blocks_data = json.load(vrp_blocks_json, cls=jsonc_decoder.JSONCDecoder)
    print("Add blocks to exclude list via typing 'a', use 'x' to skip.")
    for block, block_data in vrp_blocks_data.items():
        if type(block_data) == dict and block_data.get('sound', '') in sounds_data[tool]:
            print(block)
            add = ''
            while add not in ['a', 'x']:
                add = input()
            if add == 'a':
                sounds_data[tool_group].append(block)
    with open(sounds_data_path, 'w') as sounds_data_file:
        json.dump(sounds_data, sounds_data_file, indent=4)
    print(f'Successfully updated {tool} exclude list.')

def add_new_sounds():
    """Sort new sounds to tools"""
    with open(sounds_data_path, 'r') as sounds_data_file:
        sounds_data = json.load(sounds_data_file, cls=jsonc_decoder.JSONCDecoder)
    with open(backup_file_path, 'w') as backup_sounds_data_file:
        json.dump(sounds_data, backup_sounds_data_file, indent=4)
    with open(vanilla_blocks_path, 'r') as vrp_blocks_json:
        vrp_blocks_data = json.load(vrp_blocks_json, cls=jsonc_decoder.JSONCDecoder)
    sounds = []
    for block_data in vrp_blocks_data.values():
        if type(block_data) == dict and block_data.get('sound', '') not in sounds:
            sounds.append(block_data.get('sound', ''))
    sounds.remove('')
    old_sounds = sounds_data['axe'] + sounds_data['pickaxe'] + sounds_data['shovel'] + sounds_data['hoe'] + sounds_data['skipped_sounds']
    new_sounds = []
    for i in sounds:
        if i not in old_sounds:
            new_sounds.append(i)
    if new_sounds == []:
        print('There are no new sounds.')
    else:
        print("Sort block sounds by tools [a, p, s, h]. Use 'x' to skip.")
        for sound in sorted(new_sounds):
            print(sound)
            tool = ''
            while tool not in ['a', 'p', 's', 'h', 'x']:
                tool = input()
            if tool != 'x':
                sounds_data[get_tool_name(tool)].append(sound)
            else:
                sounds_data['skipped_sounds'].append(sound)
    with open(sounds_data_path, 'w') as sounds_data_file:
        json.dump(sounds_data, sounds_data_file, indent=4)
    print('Sounds update completed.')


def update_data():
    with open(sounds_data_path, 'r') as sounds_data_file:
        sounds_data = json.load(sounds_data_file, cls=jsonc_decoder.JSONCDecoder)
    with open(backup_file_path, 'w') as backup_sounds_data_file:
        json.dump(sounds_data, backup_sounds_data_file, indent=4)
    for item in sounds_data:
        sounds_data[item] = []
    with open(vanilla_blocks_path, 'r') as vrp_blocks_json:
        vrp_blocks_data = json.load(vrp_blocks_json, cls=jsonc_decoder.JSONCDecoder)
    sounds = []
    for block_data in vrp_blocks_data.values():
        if type(block_data) == dict and block_data.get('sound', '') not in sounds:
            sounds.append(block_data.get('sound', ''))
    sounds.remove('')
    print("Sort block sounds by tools [a, p, s, h]. Use 'x' to skip.")
    for sound in sorted(sounds):
        print(sound)
        tool = ''
        while tool not in ['a', 'p', 's', 'h', 'x']:
            tool = input()
        if tool != 'x':
            sounds_data[get_tool_name(tool)].append(sound)
        else:
            sounds_data['skipped_sounds'].append(sound)
    with open(sounds_data_path, 'w') as sounds_data_file:
        json.dump(sounds_data, sounds_data_file, indent=4)
    print('Data update completed.')

def launch() -> None:
    vanilla_blocks_path = path.join('vanilla_data', 'blocks.json')
    print('Welcome to Bedrock Tools Generator!\nDeveloped by MJ105#0448.')
    chdir(path.dirname(path.realpath(__file__)))
    if not path.exists(vanilla_blocks_path):
        print(f"Missing '{vanilla_blocks_path}' file!")
        exit()
    main()

if __name__ == '__main__':
    launch()