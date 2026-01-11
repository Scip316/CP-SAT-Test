import pandas as pd
from ortools.sat.python import cp_model
from math import floor

pers_df = pd.read_excel('Phase2.xlsx', sheet_name='Pers')
pos_df = pd.read_excel('Phase2.xlsx', sheet_name='Pos')
# Mapping
citizenship_map = {"Local": 1, "PR": 2, "Foreigner": 3, "Any": 4}
field_map = {"IT":1, "MED":2, "SALES":3, "ENGINEER":4, "RANDOM":5, "LEAD":6, "ANY":7}
tag_map = {"HR":1, "Int":2, "Ops":3, "Logs":4, "Plans":5, "Train":6, "Main":7}
tier_map = {"Junior":1, "Mid":2, "Senior":3}

pers_df["Citizenship"] = pers_df["Citizenship"].map(citizenship_map)
pers_df["Tier"] = pers_df["Tier"].map(tier_map)
pers_df["Field"] = pers_df["Field"].map(field_map)

pos_df["Req_Citizenship"] = pos_df["Req_Citizenship"].map(citizenship_map)
pos_df["Req_Tier"] = pos_df["Req_Tier"].map(tier_map)
pos_df["Req_Field"] = pos_df["Req_Field"].map(field_map)
pos_df["Tag"] = pos_df["Tag"].map(tag_map)

model = cp_model.CpModel()
solver = cp_model.CpSolver()

no_of_people = len(pers_df)
no_of_desk = len(pos_df)

assignments = {}
penalties   = {}
for i in range(no_of_people):
    for j in range(no_of_desk):
        pers = pers_df.loc[i]
        pos  = pos_df.loc[j]

        citizen_match = (pers["Citizenship"] == pos["Req_Citizenship"]) or (pos["Req_Citizenship"] == 4)
        field_match   = (pers["Field"] == pos["Req_Field"]) or (pos["Req_Field"] == 7)

        if citizen_match and field_match:
            assignments[i,j] = model.NewBoolVar(f"x_{i}_{j}")

            # --- Tier penalty variable ---
            penalty_var = model.NewIntVar(0, 10, f"penalty_{i}_{j}")
            penalties[i,j] = penalty_var

            pers_tier = pers["Tier"]
            pos_tier  = pos["Req_Tier"]

            # Exact match → penalty 0
            if pers_tier == pos_tier:
                model.Add(penalty_var == 0).OnlyEnforceIf(assignments[i,j])

            # Allowed mismatches → penalty 1
            elif (pers_tier == 1 and pos_tier == 2) or \
                 (pers_tier == 2 and pos_tier == 1) or \
                 (pers_tier == 2 and pos_tier == 3) or \
                 (pers_tier == 3 and pos_tier == 2):
                model.Add(penalty_var == 1).OnlyEnforceIf(assignments[i,j])

            # Forbidden mismatches → disallow assignment
            elif (pers_tier == 1 and pos_tier == 3) or \
                 (pers_tier == 3 and pos_tier == 1):
                model.Add(assignments[i,j] == 0)
                model.Add(penalty_var == 10)  # not used, but defined

for i in range(no_of_people):
    feasible_jobs = [j for j in range(no_of_desk) if (i,j) in assignments]
    if feasible_jobs:
        model.Add(sum(assignments[i,j] for j in feasible_jobs) == 1)
    else:
        print(f"Warning: Person {pers_df.loc[i,'Name_ID']} has no feasible job!")
        
for j in range(no_of_desk): 
    feasible_people = [i for i in range(no_of_people) if (i,j) in assignments]
    if feasible_people:
        model.Add(sum(assignments[i,j] for i in feasible_people) <= 1)

# --- Objective: maximize assignments, minimize penalties ---
appointment_mismatch = model.NewIntVar(0, no_of_people * no_of_desk, "appointment_mismatch")
model.Add(appointment_mismatch == sum(penalties.values()))

# Weighted objective: prioritize assignments, discourage mismatches
model.Maximize(sum(assignments.values()) - appointment_mismatch)

status_code = solver.Solve(model)
print(f"{solver.StatusName(status_code)} ({status_code})")
print("Objective value:", solver.ObjectiveValue())
print("Best bound:", solver.BestObjectiveBound())

# --- Optional relaxation: allow within 5% of best bound ---
model.Add(appointment_mismatch <= floor(1.05 * solver.ObjectiveValue()))
status_code = solver.Solve(model)
print(f"Relaxed solve: {solver.StatusName(status_code)} ({status_code})")

# Invert the dictionaries
inv_citizenship_map = {v: k for k, v in citizenship_map.items()}
inv_field_map = {v: k for k, v in field_map.items()}
inv_tag_map = {v: k for k, v in tag_map.items()}
inv_tier_map = {v: k for k, v in tier_map.items()}

# pers_df
pers_df["Citizenship"] = pers_df["Citizenship"].map(inv_citizenship_map)
pers_df["Tier"] = pers_df["Tier"].map(inv_tier_map)
pers_df["Field"] = pers_df["Field"].map(inv_field_map)

# pos_df
pos_df["Req_Citizenship"] = pos_df["Req_Citizenship"].map(inv_citizenship_map)
pos_df["Req_Tier"] = pos_df["Req_Tier"].map(inv_tier_map)
pos_df["Req_Field"] = pos_df["Req_Field"].map(inv_field_map)
pos_df["Tag"] = pos_df["Tag"].map(inv_tag_map)

