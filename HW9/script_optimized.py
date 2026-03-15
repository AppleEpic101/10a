import pandas as pd
import ssl

# Fetch data from Google Sheets
sheet_id = '1TnKetCAg2NvMBcMc5EvTSCexvkHO4fWfMF46lFpzFjY'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'

ssl._create_default_https_context = ssl._create_unverified_context
df = pd.read_csv(url)
df = df.dropna(subset=['Opcode'])
df = df[df['Include'] == True]

# List of all control signals
signals = [
    'MuxSel2', 'MuxSel1', 'MuxSel0', 'Load',
    'UpdateAcc', 'OpSelect', 'UseAdder', 'F3', 'F2', 'F1', 'F0',
    'CinSel1', 'CinSel0', 'InvertCarry', 'LSBselect1', 'LSBselect0',
    'MiddleSelect', 'MSBselect2', 'MSBselect1', 'MSBselect0',
    'MaskSZ', 'MaskVC', 'PopF',
    'EnableInc', 'UseOffset', 'AddressSel1', 'AddressSel0',
    'UseInc', 'UsePost', 'MaskS', 'MaskX',
    'RD', 'WR', 'SelectDB1', 'SelectDB0', 'OffsetSel'
]

def get_val(row, col):
    return int(row[col]) if pd.notnull(row[col]) else 0

output = []

output.append("\" === Optimized Instruction Decoding === \"")

# Define nodes for each instruction
for _, row in df.iterrows():
    output.append(f"Inst_{row['Opcode']} node;")
    output.append(f"Inst_{row['Opcode']} = (IR == {row['Opcode']});")

output.append("\n\" === Intermediate Signal Groups === \"")

# Group signals by their unique values/functions
# We can group by columns like 'ALU', 'DAU', 'PAU' if they represent shared logic
# Or just group by unique combinations of bits.

# Option 1: Group by the descriptive columns if they are reliable
groups = {}
for col in ['PAU', 'ALU', 'DAU']:
    # Only group rows that DON'T have a special condition
    mask = df['Condition'].isnull() | (df['Condition'] == '')
    unique_vals = df[mask][col].unique()
    for val in unique_vals:
        if pd.isnull(val): continue
        group_name = f"Group_{col}_{val.replace(' ', '_').replace('(', '').replace(')', '').replace('+', 'plus').replace('-', 'minus').replace('/', '_')}"
        insts = df[mask & (df[col] == val)]['Opcode'].tolist()
        if insts:
            output.append(f"{group_name} node;")
            output.append(f"{group_name} = " + " # ".join([f"Inst_{i}" for i in insts]) + ";")
            groups[(col, val)] = group_name

output.append("\n\" === Signal Equations === \"")

# For each signal, build the equation based on groups or individual instructions
for sig in signals:
    terms = []
    
    # instructions where the signal is 1 and NO condition
    mask_no_cond = df['Condition'].isnull() | (df['Condition'] == '')
    is_one_no_cond = set(df[mask_no_cond & (df[sig] == 1)]['Opcode'].tolist())
    
    # Try to use groups for the no-condition instructions
    remaining_insts = is_one_no_cond
    used_groups = []
    for (col, val), group_name in groups.items():
        group_insts = set(df[mask_no_cond & (df[col] == val)]['Opcode'].tolist())
        if group_insts and group_insts.issubset(remaining_insts):
            used_groups.append(group_name)
            remaining_insts -= group_insts
    
    equation_terms = used_groups + [f"Inst_{i}" for i in remaining_insts]
    
    # Now add instructions with conditions
    mask_cond = df['Condition'].notnull() & (df['Condition'] != '')
    for _, row in df[mask_cond].iterrows():
        # This is tricky. If sig is one of the MuxSel signals changed by the condition, 
        # we need to handle it.
        # From script.py: Condition affects MuxSel2=0, MuxSel1=1, MuxSel0=1, Load=0
        # Otherwise it's 0,0,0,0.
        cond = row['Condition']
        if sig == 'MuxSel1' or sig == 'MuxSel0':
            # These are 1 if condition is true
            equation_terms.append(f"(Inst_{row['Opcode']} & ({cond}))")
        elif sig == 'MuxSel2' or sig == 'Load':
            # These are always 0 for the conditional cases in the original script
            pass 
        else:
            # For other signals, the condition doesn't seem to affect them in script.py
            # They stay at their get_val value.
            if get_val(row, sig) == 1:
                equation_terms.append(f"Inst_{row['Opcode']}")

    if not equation_terms:
        output.append(f"{sig} = 0;")
    else:
        output.append(f"{sig} = " + " # ".join(equation_terms) + ";")

final_abel = "\n".join(output)

with open("optimized_logic.abel", "w") as f:
    f.write(final_abel)

print("Optimized ABEL logic generated successfully.")
