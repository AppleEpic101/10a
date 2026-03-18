import pandas as pd
import ssl

# Fetch data
sheet_id = '1yYmfFwq5_bMKeojHUvYkk4ksbMl_yaIAT2HGvagZAHo'
gid = '0'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'

ssl._create_default_https_context = ssl._create_unverified_context
df = pd.read_csv(url)

# Filter data
df = df[df['Include'] == True]
df = df.dropna(subset=['name', 'Instruction'])

def format_instruction_array(name, instruction, description):
    # Convert instruction string to list of elements
    elements = []
    for char in str(instruction):
        if char in ('0', '1'):
            elements.append(char)
        else:
            elements.append('.X.')
    
    array_str = ", ".join(elements)
    
    desc_str = str(description).strip()
    if pd.isna(description) or not desc_str or desc_str == 'nan':
        return f"{name:<6} = [{array_str}];"
    else:
        return f"{name:<6} = [{array_str}]; \" {desc_str}"

# Generate lines
lines = [format_instruction_array(row['name'], row['Instruction'], row.get('Description', '')) for _, row in df.iterrows()]
final_output = "\n".join(lines)

# Write to file
output_file = "HW10/instruction_definitions.abel"
with open(output_file, "w") as f:
    f.write(final_output)

print(f"Generated {len(lines)} instruction definitions in {output_file}")
