CREATE TABLE Paper
(
paper_id int NOT NULL,
href varchar(255),
name varchar(255),
crawed tinyint,
PRIMARY KEY (paper_id)
);

CREATE TABLE Author
(
author_id int NOT NULL,
href varchar(255),
name varchar(255),
paper_id int,
PRIMARY KEY (author_id),
FOREIGN KEY (paper_id) REFERENCES Paper(paper_id)
);

CREATE TABLE Institution
(
author_id int NOT NULL,
href varchar(255),
name varchar(255),
paper_id int,
PRIMARY KEY (author_id),
FOREIGN KEY (paper_id) REFERENCES Paper(paper_id)
);

CREATE TABLE Ref
(
id int NOT NULL,
href varchar(255),
name varchar(255),
paper_id int,
ref_id int,
PRIMARY KEY (id),
FOREIGN KEY (ref_id) REFERENCES Paper(paper_id),
FOREIGN KEY (paper_id) REFERENCES Paper(paper_id)
);

