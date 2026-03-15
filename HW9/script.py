import pandas as pd

sheet_id = '1TnKetCAg2NvMBcMc5EvTSCexvkHO4fWfMF46lFpzFjY'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'

import ssl

ssl._create_default_https_context = ssl._create_unverified_context
df = pd.read_csv(url)
df = df.dropna(subset=['Opcode'])
df = df[df['Include'] == True]

def format_abel(row):
    get_val = lambda col: int(row[col]) if pd.notnull(row[col]) else 0
    
    condition = row['Condition'] if 'Condition' in row and pd.notnull(row['Condition']) else None
    
    if condition:
        pau_block = f"""    WHEN ({condition}) THEN {{ 
        MuxSel2 = 0;
        MuxSel1 = 1;
        MuxSel0 = 1;
        Load = 0;
    }} ELSE {{
        MuxSel2 = 0;
        MuxSel1 = 0;
        MuxSel0 = 0;
        Load = 0;
    }}"""
    else:
        pau_block = f"""    MuxSel2 = {get_val('MuxSel2')};
    MuxSel1 = {get_val('MuxSel1')};
    MuxSel0 = {get_val('MuxSel0')};
    Load = {get_val('Load')};"""

    return f"""WHEN (IR == {row['Opcode']}) THEN {{
    \" PAU: {row['PAU']}
{pau_block}

    \" ALU: {row['ALU']}
    UpdateAcc = {get_val('UpdateAcc')};
    OpSelect = {get_val('OpSelect')};
    UseAdder = {get_val('UseAdder')};
    F3 = {get_val('F3')};
    F2 = {get_val('F2')};
    F1 = {get_val('F1')};
    F0 = {get_val('F0')};
    CinSel1 = {get_val('CinSel1')};
    CinSel0 = {get_val('CinSel0')};
    InvertCarry = {get_val('InvertCarry')};
    LSBselect1 = {get_val('LSBselect1')};
    LSBselect0 = {get_val('LSBselect0')};
    MiddleSelect = {get_val('MiddleSelect')};
    MSBselect2 = {get_val('MSBselect2')};
    MSBselect1 = {get_val('MSBselect1')};
    MSBselect0 = {get_val('MSBselect0')};
    MaskSZ = {get_val('MaskSZ')};
    MaskVC = {get_val('MaskVC')};
    PopF = {get_val('PopF')};

    \" DAU: {row['DAU']}
    EnableInc = {get_val('EnableInc')};
    UseOffset = {get_val('UseOffset')};
    AddressSel1 = {get_val('AddressSel1')};
    AddressSel0 = {get_val('AddressSel0')};
    UseInc = {get_val('UseInc')};
    UsePost = {get_val('UsePost')};
    MaskS = {get_val('MaskS')};
    MaskX = {get_val('MaskX')};
    
    \" Control Unit Top Level
    RD = {get_val('RD')};
    WR = {get_val('WR')};
    SelectDB1 = {get_val('SelectDB1')};
    SelectDB0 = {get_val('SelectDB0')};
    OffsetSel = {get_val('OffsetSel')};
}}"""

abel_blocks = [format_abel(row) for _, row in df.iterrows()]
final_output = "\n\n".join(abel_blocks)

with open("instructions.abel", "w") as f:
    f.write(final_output)

print("Final ABEL file generated successfully.")