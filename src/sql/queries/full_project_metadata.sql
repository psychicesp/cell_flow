SELECT
	projects.project_name,
	experiments.*,
	samples.id as sample_id
	samples.*
FROM projects
FULL OUTER JOIN experiments ON experiments.project_id = projects.id
FULL OUTER JOIN samples ON samples.experiment_id = experiments.id
WHERE projects.id = {project_id}
EXCEPT
SELECT
	projects.id,
	experiments.id,
	samples.id
FROM projects
FULL OUTER JOIN experiments ON experiments.project_id = projects.id
FULL OUTER JOIN samples ON samples.experiment_id = experiments.id;