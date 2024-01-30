-- https://dbdiagram.io/d/63ebf3b6296d97641d80f50c

CREATE TABLE Projects (
  id INTEGER PRIMARY KEY,
  project_name TEXT
);

CREATE TABLE Experiments (
  id INTEGER PRIMARY KEY,
  experiment_name TEXT,
  project_id INTEGER,
  FOREIGN KEY (project_id) REFERENCES Projects(id)
);

CREATE TABLE Sample_Groups(
  id INTEGER PRIMARY KEY,
  sample_group TEXT,
  experiment_id INTEGER,
  FOREIGN KEY (experiment_id) REFERENCES Experiments(id)
);

CREATE TABLE Samples (
  id INTEGER PRIMARY KEY,
  sample_name TEXT,
  "day" TEXT,
  donor TEXT,
  experiment_id INTEGER,
  "control" BOOLEAN,
  FOREIGN KEY (experiment_id) REFERENCES Experiments(id)
);

CREATE TABLE Events (
  id INTEGER PRIMARY KEY,
  sample_id INTEGER,
  random REAL,
  FOREIGN KEY (sample_id) REFERENCES Samples(id)
);

CREATE TABLE Gates (
  id INTEGER PRIMARY KEY, 
  experiment_id INTEGER,
  sample_group_id INTEGER,
  gate_name TEXT,
  gate_label TEXT,
  parent_id INTEGER, -- blank if there is no parent
  is_linear BOOLEAN,
  FOREIGN KEY (experiment_id) REFERENCES Experiments(id),
  FOREIGN KEY (parent_id) REFERENCES Gates(id),
  FOREIGN KEY (sample_group_id) REFERENCES Sample_Groups(id)
);

CREATE TABLE Channels (
  id INTEGER PRIMARY KEY,
  channel_label TEXT,
  channel_fluor TEXT,
  experiment_id INTEGER,
  FOREIGN KEY (experiment_id) REFERENCES Experiments(id)
);

CREATE TABLE Linear_Scalers (
  id INTEGER PRIMARY KEY,
  gate TEXT,
  channel_id INTEGER,
  boundry FLOAT,
  parent_id INTEGER,
  FOREIGN KEY (channel_id) REFERENCES Channels(id),
  FOREIGN KEY (parent_id) REFERENCES Gates(id)
);

CREATE TABLE Communities(
  event_id INTEGER,
  leiden SMALLINT,
  FOREIGN KEY (event_id) REFERENCES Events(id)
);

CREATE TABLE "{gateID}_Membership" (
  event_id INTEGER,
  membership BOOLEAN,
  FOREIGN KEY (event_id) REFERENCES Events(id)
);

CREATE TABLE "{channelID}_Flourescence" (
  event_id INTEGER,
  flourescense FLOAT,
  FOREIGN KEY (event_id) REFERENCES Events(id)
);
