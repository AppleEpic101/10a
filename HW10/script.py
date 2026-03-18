import pandas as pd
import ssl

# Setup
sheet_id = '1TnKetCAg2NvMBcMc5EvTSCexvkHO4fWfMF46lFpzFjY'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'

ssl._create_default_https_context = ssl._create_unverified_context
df = pd.read_csv(url)
df = df.dropna(subset=['Opcode'])
df = df[df['Include'] == True]

def format_abel(row):
    lines = []
    
    def get_assignment(signal_name):
        val = row[signal_name]
        if pd.isna(val):
            return f"    {signal_name} = 0;"
        
        str_val = str(val).strip().upper()
        # If the value is .X., we return None so the caller knows not to include the line
        if str_val == '.X.':
            return None
        
        try:
            clean_val = int(float(val))
            return f"    {signal_name} = {clean_val};"
        except (ValueError, TypeError):
            return f"    {signal_name} = {val};"

    # Define the signals for each block
    pau_signals = ['MuxSel2', 'MuxSel1', 'MuxSel0', 'Load']
    alu_signals = [
        'UpdateAcc', 'OpSelect', 'UseAdder', 'F3', 'F2', 'F1', 'F0', 
        'CinSel1', 'CinSel0', 'InvertCarry', 'LSBselect1', 'LSBselect0', 
        'MiddleSelect', 'MSBselect2', 'MSBselect1', 'MSBselect0', 
        'MaskSZ', 'MaskVC', 'PopF'
    ]
    dau_signals = ['EnableInc', 'UseOffset', 'AddressSel1', 'AddressSel0', 'UseInc', 'UsePost', 'MaskS', 'MaskX']
    ctrl_signals = ['RD', 'WR', 'SelectDB1', 'SelectDB0', 'OffsetSel']

    # Header
    output = [f"WHEN (IR == {row['Opcode']}) THEN {{"]
    
    # PAU Block logic
    condition = row['Condition'] if 'Condition' in row and pd.notnull(row['Condition']) else None
    output.append(f"    \" PAU: {row['PAU']}")
    if condition:
        output.append(f"    WHEN ({condition}) THEN {{ \n        MuxSel2 = 0; MuxSel1 = 1; MuxSel0 = 1; Load = 0;\n    }} ELSE {{\n        MuxSel2 = 0; MuxSel1 = 0; MuxSel0 = 0; Load = 0;\n    }}")
    else:
        for s in pau_signals:
            line = get_assignment(s)
            if line: output.append(line)

    # ALU Block
    output.append(f"\n    \" ALU: {row['ALU']}")
    for s in alu_signals:
        line = get_assignment(s)
        if line: output.append(line)

    # DAU Block
    output.append(f"\n    \" DAU: {row['DAU']}")
    for s in dau_signals:
        line = get_assignment(s)
        if line: output.append(line)

    # Control Block
    output.append(f"\n    \" Control Unit Top Level")
    for s in ctrl_signals:
        line = get_assignment(s)
        if line: output.append(line)

    output.append("}")
    return "\n".join(output)

# Generate and filter
abel_blocks = [format_abel(row) for _, row in df.iterrows()]
final_output = "\n\n".join(abel_blocks)

with open("HW10/instructions.abel", "w") as f:
    f.write(final_output)

print("Final ABEL file generated successfully.")