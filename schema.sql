DROP TABLE IF EXISTS `Students`;
DROP TABLE IF EXISTS `Quiz`;
DROP TABLE IF EXISTS `Results`;

CREATE TABLE `Students`(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fname TEXT,
    lname TEXT
    );

CREATE TABLE `Quiz`(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    questions INT,
    quiz_date DATE
    );

CREATE TABLE `Results`(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    score INT,
    quiz_id INT,
    students_id INT,
    FOREIGN KEY(quiz_id) REFERENCES Quiz(id),
    FOREIGN KEY(students_id) REFERENCES Students(id)
    );

INSERT INTO Quiz (id, subject, questions, quiz_date) VALUES
(1, 'Python Basics', 5, '2015-05-05');

INSERT INTO Students (id, fname, lname) VALUES
(1, 'John', 'Smith');

INSERT INTO Results (score, quiz_id, students_id) VALUES
(85, 1, 1);