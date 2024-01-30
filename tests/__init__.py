#%%
import flowkit as fk
import os

folder_loc = os.path.join('real_experiments', 'Exp 4_Donor 3 and 6_Day 0', 'samples')
full_folder = [os.path.join(folder_loc, x) for x in os.listdir(folder_loc)]

experiment_file = os.path.join('real_experiments', 'Exp 4_Donor 3 and 6_Day 0','Exp 4_Donor 3 and 6_Day 0.wsp')
single_sample = os.path.join(folder_loc, '20220321 Cytokine DOE Day 10_Donor 3_IL2+7.fcs')

# session1 = fk.Session(full_folder)
# session1.import_flowjo_workspace(experiment_file)

session2 = fk.Session(single_sample)
session2.import_flowjo_workspace(experiment_file)

oup_list = []
for file in full_folder:
    while len(oup_list) == 0:
        temp_session = fk.Session(file)
        temp_session.import_flowjo_workspace(experiment_file)
        temp_session.analyze_samples('Samples + Controls')
        oup_list = temp_session.get_group_sample_ids('Samples + Controls')

print(oup_list)
# %%
