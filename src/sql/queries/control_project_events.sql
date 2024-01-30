SELECT project_{project_id}_full_channels.* FROM project_{project_id}_full_channels
FULL JOIN project_{project_id} on project_{project_id}_full_channels.sample_id = project_{project_id}.sample_id
FULL JOIN project_{project_id}_full_membership on project_{project_id}_full_membership.event_id = project_{project_id}_full_channels.event_id
WHERE project_{project_id}.control = 1 AND {parent_gate} = 1;