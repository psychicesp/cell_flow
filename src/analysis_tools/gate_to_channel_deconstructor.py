def clean_quadrant_name(gate_name):
    out_name_list = gate_name.split(': ')[-1].split(' , ')
    out_name_list = [x.split('-')[0] + x.strip(' ')[-1] for x in out_name_list]
    out_name = ', '.join(out_name_list)
    return out_name


def is_quadrant_gate(gate_name):
    return len(gate_name) > 10 and gate_name[0] == 'Q'


def gate_renamer(gate_list):
    rename_dict = {}
    for gate in gate_list:
        if is_quadrant_gate(gate):
            rename_dict[gate] = clean_quadrant_name(gate)
    return rename_dict


def list_renamer(list_to_rename, rename_dict):
    renamed_list = []
    for gate in list_to_rename:
        if gate in rename_dict:
            renamed_list.append(rename_dict[gate])
        else:
            renamed_list.append(gate)
    return renamed_list


def gate_to_channel(
        flowkit_session,
        sample_group='Samples + Controls',
        scaler_out=False
        ):
    gate_names = [x[0] for x in flowkit_session.get_gate_ids(sample_group)]
    gates = [flowkit_session.get_gate(sample_group, x) for x in gate_names]
    gates = [x for x in gates if (x.gate_type == 'RectangleGate' and len(
        x.dimensions) == 1) or (is_quadrant_gate(x.gate_name) and len(x.dimensions) == 2)]
    # Sorting by gate name length is the simplest way to ensure that quadrant gates are first and will usualy work
    gates = sorted(gates, key=lambda x: len(x.gate_name))
    channel_renamer = {}
    scaler = {}
    for gate in gates:
        gate_name = gate.gate_name.strip()
        if is_quadrant_gate(gate_name):
            clean_gate_name = clean_quadrant_name(gate_name)
            channel_renamer[gate_name] = clean_gate_name
            for i, sub_gate in enumerate(clean_gate_name.split(', ')):
                channel_renamer[gate.dimensions[i].id] = sub_gate[:-1]

                if sub_gate[-1] == '+':
                    dim_min = gate.dimensions[i].min
                    if dim_min:
                        scaler[sub_gate[:-1]] = dim_min
                        scaler[gate.dimensions[i].id] = dim_min
                elif sub_gate[-1] == '-':
                    dim_max = gate.dimensions[i].max
                    if dim_max:
                        scaler[sub_gate[:-1]] = dim_max
                        scaler[gate.dimensions[i].id] = dim_max

        else:
            channel_renamer[gate.dimensions[0].id] = gate_name[:-1]
            if gate_name[-1] == '+':
                dim_min = gate.dimensions[0].min
                if dim_min:
                    scaler[gate_name[:-1]] = dim_min
                    scaler[gate.dimensions[0].id] = dim_min
            elif gate_name[-1] == '-':
                dim_max = gate.dimensions[0].max
                if dim_max:
                    scaler[gate_name[:-1]] = dim_max
                    scaler[gate.dimensions[0].id] = dim_max
    if scaler_out:
        return channel_renamer, scaler
    else:
        return channel_renamer