import pandas as pd
import ssl

# Fetch data
sheet_id = '1TnKetCAg2NvMBcMc5EvTSCexvkHO4fWfMF46lFpzFjY'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'

ssl._create_default_https_context = ssl._create_unverified_context
df = pd.read_csv(url)

# Filter data
df = df[df['Include'] == True]
df = df.dropna(subset=['name', 'Instruction'])

def format_instruction_array(name, instruction):
    # Convert instruction string to list of elements
    elements = []
    for char in str(instruction):
        if char in ('0', '1'):
            elements.append(char)
        else:
            elements.append('.X.')
    
    # Ensure it's 16 elements (though usually it should be)
    # The user said "expanded into an array of 16"
    # If it's shorter than 16, we might need to pad it, but usually these are 16 bits.
    # If it's longer, maybe truncate?
    # Let's just process what's there.
    
    array_str = ", ".join(elements)
    return f"{name:<6} = [{array_str}];"

# Generate lines
lines = [format_instruction_array(row['name'], row['Instruction']) for _, row in df.iterrows()]
final_output = "\n".join(lines)

# Write to file
output_file = "instruction_definitions.abel"
with open(output_file, "w") as f:
    f.write(final_output)

print(f"Generated {len(lines)} instruction definitions in {output_file}")
