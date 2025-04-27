CREATE DATABASE organ_donation_db;
USE organ_donation_db;

CREATE TABLE donor (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    blood_group VARCHAR(5),
    organ_donated VARCHAR(50),
    contact_info VARCHAR(100),
    city VARCHAR(50),
    donation_status VARCHAR(20) DEFAULT 'Available'
);



INSERT INTO donor (name, age, gender, blood_group, organ_donated, contact_info, city)
VALUES
('John Doe', 45, 'Male', 'A+', 'Kidney', '1234567890', 'New York'),
('Jane Smith', 32, 'Female', 'B+', 'Liver', '9876543210', 'Los Angeles');

SELECT * FROM donor;
UPDATE donor SET city = 'Chicago' WHERE donor_id = 1;
DELETE FROM donor WHERE donor_id = 2;


CREATE TABLE recipient (
    recipient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    blood_group VARCHAR(5),
    organ_needed VARCHAR(50),
    contact_info VARCHAR(100),
    city VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Waiting'
);


INSERT INTO recipient (name, age, gender, blood_group, organ_needed, contact_info, city)
VALUES
('Alice Brown', 29, 'Female', 'A+', 'Kidney', '5551234567', 'Boston'),
('Bob Johnson', 50, 'Male', 'B+', 'Liver', '4449876543', 'Chicago');


SELECT * FROM recipient;
UPDATE recipient SET status = 'Matched' WHERE recipient_id = 1;
DELETE FROM recipient WHERE recipient_id = 2;


CREATE TABLE organ_donation (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT,
    recipient_id INT,
    organ VARCHAR(50),
    date_of_donation DATE,
    FOREIGN KEY (donor_id) REFERENCES donor(donor_id),
    FOREIGN KEY (recipient_id) REFERENCES recipient(recipient_id)
);


INSERT INTO organ_donation (donor_id, recipient_id, organ, date_of_donation)
VALUES
(1, 1, 'Kidney', CURDATE());


SELECT * FROM organ_donation;


SELECT donor.name, donor.organ_donated
FROM donor
WHERE blood_group = 'A+' AND organ_donated = 'Kidney' AND donation_status = 'Available';


CREATE TABLE admin (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL
);


CREATE TABLE admin (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL
);


INSERT INTO admin (username, password)
VALUES ('admin', 'admin123');


SELECT * FROM admin;



