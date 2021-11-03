USE onlinecourses;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('student', 'teacher'),
    email VARCHAR(255) NOT NULL,
	password VARCHAR(45) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    course_id INT NOT NULL
);

CREATE TABLE course (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
	hours_to_complete INT NOT NULL,
    educational_material VARCHAR(255) NOT NULL,
	student_counter	INT CHECK(student_counter BETWEEN 0 and 5),
    user_id INT NOT NULL
);

CREATE TABLE course_membership (
	user_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id)
);

CREATE TABLE request (
	id INT AUTO_INCREMENT PRIMARY KEY,
	student_id INT NOT NULL,
    teacher_id INT NOT NULL,
	course_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (teacher_id) REFERENCES user(id),
    FOREIGN KEY (course_id) REFERENCES course(id)
);