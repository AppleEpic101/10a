# Assemble the final CU.abl
with open("CU.abl", "r") as f:
    lines = f.readlines()

header = lines[:158] # Everything up to EQUATIONS (excluding EQUATIONS line itself)

# Declare nodes before EQUATIONS
with open("optimized_logic.abel", "r") as f:
    optimized_lines = f.readlines()

declarations = [line for line in optimized_lines if "node;" in line or "===" in line]
equations = [line for line in optimized_lines if "node;" not in line and "===" not in line]
footer = ["\nEND CUInterface\n"]

with open("CU_new.abl", "w") as f:
    f.writelines(header)
    f.writelines(declarations)
    f.write("\nEQUATIONS\n\n")
    f.write("IR.CLK = Clock;\n")
    f.write("IR.CLR = Reset;\n")
    f.write("IR = ProgramDB;\n")
    f.write("[Address12..Address0] = IR[12..0];\n")
    f.write("IO = 0;\n\n")
    
    # Filter out duplicate EQUATIONS tags from optimized equations
    clean_equations = [line for line in equations if "EQUATIONS" not in line]
    f.writelines(clean_equations)
    f.writelines(footer)

print("CU_new.abl assembled.")
