DROP DATABASE IF EXISTS queue_management_db;

CREATE DATABASE queue_management_db;

USE queue_management_db;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE organizations (
    org_id INT AUTO_INCREMENT PRIMARY KEY,
    org_name VARCHAR(150) NOT NULL,
    category ENUM('Hospital','Clinic','Pharmacy','Restaurant','Salon','Educational Institute') NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    area VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(15),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    org_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('Manager','Receptionist','Service Staff') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    org_id INT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    avg_duration_minutes INT DEFAULT 15,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    org_id INT NOT NULL,
    service_id INT,
    token_number INT NOT NULL,
    appointment_type ENUM('Booked','Walk-in') DEFAULT 'Booked',
    status ENUM('Pending','In Progress','Completed','Cancelled') DEFAULT 'Pending',
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (org_id) REFERENCES organizations(org_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
);

CREATE TABLE queue_status (
    queue_id INT AUTO_INCREMENT PRIMARY KEY,
    org_id INT NOT NULL,
    current_token_serving INT DEFAULT 0,
    avg_wait_time_minutes INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO organizations (org_name, category, address, city, area, contact_email, contact_phone, is_verified) VALUES

('City Care Hospital', 'Hospital', '12 MG Road', 'Mumbai', 'Andheri', 'contact@citycare.com', '9876543210', TRUE),
('Sunrise Multispeciality Hospital', 'Hospital', '22 Hill Road', 'Mumbai', 'Bandra', 'info@sunrise.com', '9876543211', TRUE),
('LifeLine Hospital', 'Hospital', '7 Powai Lake Road', 'Mumbai', 'Powai', 'contact@lifeline.com', '9876543212', TRUE),
('Green Valley Hospital', 'Hospital', '18 SV Road', 'Mumbai', 'Andheri East', 'info@greenvalley.com', '9876543213', TRUE),
('Trinity Hospital', 'Hospital', '5 Turner Road', 'Mumbai', 'Bandra West', 'contact@trinity.com', '9876543214', TRUE),

('Wellness Clinic', 'Clinic', '8 Chakala Road', 'Mumbai', 'Andheri', 'contact@wellness.com', '9876543220', TRUE),
('Smile Dental Clinic', 'Clinic', '11 Waterfield Road', 'Mumbai', 'Bandra', 'info@smile.com', '9876543221', TRUE),
('Family Health Clinic', 'Clinic', '6 Central Ave', 'Mumbai', 'Powai', 'contact@familyhealth.com', '9876543222', TRUE),
('Skin Care Clinic', 'Clinic', '19 JP Road', 'Mumbai', 'Andheri West', 'info@skin.com', '9876543223', TRUE),
('Vision Eye Clinic', 'Clinic', '4 Pali Hill', 'Mumbai', 'Bandra East', 'contact@vision.com', '9876543224', TRUE),

('MedPlus Pharmacy', 'Pharmacy', '2 Station Road', 'Mumbai', 'Andheri', 'contact@medplus.com', '9876543225', TRUE),
('Apollo Pharmacy', 'Pharmacy', '16 Hill Road', 'Mumbai', 'Bandra', 'info@apollo.com', '9876543226', TRUE),
('Wellness Forever', 'Pharmacy', '13 Powai Chowk', 'Mumbai', 'Powai', 'contact@wellnessforever.com', '9876543227', TRUE),
('HealthKart Pharmacy', 'Pharmacy', '17 SV Road', 'Mumbai', 'Andheri East', 'info@healthkart.com', '9876543228', TRUE),
('Care Pharmacy', 'Pharmacy', '20 Turner Road', 'Mumbai', 'Bandra West', 'contact@carepharmacy.com', '9876543229', TRUE),

('Spice Garden', 'Restaurant', '10 Linking Road', 'Mumbai', 'Bandra', 'hello@spicegarden.com', '9876543230', TRUE),
('The Food Hub', 'Restaurant', '14 Powai Plaza', 'Mumbai', 'Powai', 'info@foodhub.com', '9876543231', TRUE),
('Curry Point', 'Restaurant', '9 Market Road', 'Mumbai', 'Andheri', 'contact@currypoint.com', '9876543232', TRUE),
('Bombay Bites', 'Restaurant', '21 Carter Road', 'Mumbai', 'Bandra West', 'hello@bombaybites.com', '9876543233', TRUE),
('Green Leaf Cafe', 'Restaurant', '3 Hiranandani Road', 'Mumbai', 'Powai', 'info@greenleaf.com', '9876543234', TRUE),

('Glow Salon', 'Salon', '45 Link Road', 'Mumbai', 'Bandra', 'glow@salon.com', '9876543235', TRUE),
('Trendz Unisex Salon', 'Salon', '15 Powai Garden', 'Mumbai', 'Powai', 'info@trendz.com', '9876543236', TRUE),
('Style Studio', 'Salon', '23 Andheri West', 'Mumbai', 'Andheri', 'contact@style.com', '9876543237', TRUE),
('Elegance Salon', 'Salon', '9 Carter Road', 'Mumbai', 'Bandra East', 'info@elegance.com', '9876543238', TRUE),
('Urban Cuts', 'Salon', '11 Hiranandani Gardens', 'Mumbai', 'Powai', 'contact@urbancuts.com', '9876543239', TRUE),

('SIES College', 'Educational Institute', '1 Sion Road', 'Mumbai', 'Sion', 'contact@sies.edu', '9876543240', TRUE),
('Bandra Public School', 'Educational Institute', '6 Waterfield Road', 'Mumbai', 'Bandra', 'info@bandraschool.com', '9876543241', TRUE),
('Powai Institute of Technology', 'Educational Institute', '2 IIT Road', 'Mumbai', 'Powai', 'contact@powaiinst.com', '9876543242', TRUE),
('Andheri Junior College', 'Educational Institute', '14 SV Road', 'Mumbai', 'Andheri', 'info@andherijc.com', '9876543243', TRUE),
('Bandra Coaching Center', 'Educational Institute', '8 Turner Road', 'Mumbai', 'Bandra West', 'contact@bandracoaching.com', '9876543244', TRUE);
INSERT INTO queue_status (org_id, current_token_serving, avg_wait_time_minutes)
SELECT org_id, 0, 15
FROM organizations;
INSERT INTO services (org_id, service_name, avg_duration_minutes) VALUES

-- Hospitals (1-5)
(1,'General OPD',15),(1,'Cardiology',30),(1,'Orthopedics',25),
(2,'General OPD',15),(2,'Neurology',40),(2,'Dermatology',20),
(3,'Pediatrics',20),(3,'Gynecology',30),(3,'ENT',20),
(4,'Emergency',10),(4,'Radiology',20),(4,'Blood Test',10),
(5,'Health Checkup',20),(5,'MRI Scan',45),(5,'CT Scan',35),

-- Clinics (6-10)
(6,'General Consultation',20),(6,'Vaccination',15),(6,'Health Checkup',25),
(7,'Dental Checkup',20),(7,'Root Canal',45),(7,'Teeth Cleaning',30),
(8,'Family Consultation',20),(8,'Child Checkup',25),(8,'Blood Pressure Check',10),
(9,'Skin Consultation',20),(9,'Acne Treatment',30),(9,'Laser Treatment',45),
(10,'Eye Checkup',20),(10,'Vision Test',15),(10,'Eye Surgery Consultation',30),

-- Pharmacies (11-15)
(11,'Medicine Pickup',10),(11,'Prescription Verification',15),(11,'Health Consultation',20),
(12,'Medicine Pickup',10),(12,'Health Consultation',20),(12,'BP & Sugar Check',15),
(13,'Medicine Pickup',10),(13,'Vitamin Consultation',20),(13,'Prescription Verification',15),
(14,'Medicine Pickup',10),(14,'Health Consultation',20),(14,'Diabetes Consultation',25),
(15,'Medicine Pickup',10),(15,'Prescription Verification',15),(15,'Health Consultation',20),

-- Restaurants (16-20)
(16,'Table Booking',10),(16,'Takeaway Order',10),(16,'Home Delivery Pickup',10),
(17,'Table Booking',10),(17,'Family Dining',15),(17,'Takeaway Order',10),
(18,'Table Booking',10),(18,'Party Reservation',20),(18,'Home Delivery Pickup',10),
(19,'Table Booking',10),(19,'Takeaway Order',10),(19,'Family Dining',15),
(20,'Table Booking',10),(20,'Home Delivery Pickup',10),(20,'Takeaway Order',10),

-- Salons (21-25)
(21,'Haircut',30),(21,'Hair Spa',45),(21,'Facial',40),
(22,'Haircut',30),(22,'Beard Styling',20),(22,'Hair Coloring',60),
(23,'Haircut',30),(23,'Facial',40),(23,'Manicure',30),
(24,'Haircut',30),(24,'Pedicure',35),(24,'Hair Spa',45),
(25,'Haircut',30),(25,'Hair Coloring',60),(25,'Facial',40),

-- Educational Institutes (26-30)
(26,'Admission Inquiry',20),(26,'Fee Payment',15),(26,'Certificate Collection',10),
(27,'Admission Inquiry',20),(27,'Exam Form Submission',15),(27,'Fee Payment',15),
(28,'Admission Inquiry',20),(28,'Library Services',10),(28,'Certificate Collection',10),
(29,'Admission Inquiry',20),(29,'Student Support',15),(29,'Fee Payment',15),
(30,'Admission Inquiry',20),(30,'Counselling',25),(30,'Certificate Collection',10);
SELECT * FROM organizations;

SHOW TABLES;



USE queue_management_db;
SELECT * FROM organizations;
SELECT DATABASE();

USE queue_management_db;

SELECT COUNT(*) AS total_organizations
FROM organizations;
SELECT COUNT(*) FROM services;
SELECT * FROM services;
SELECT * FROM users;
SELECT org_id,org_name
FROM organizations
WHERE org_name = 'Style Studio';
DESCRIBE appointments;
USE queue_management_db;

SELECT
    a.appointment_id,
    a.user_id,
    a.org_id,
    a.service_id,
    a.token_number,
    a.status,
    u.full_name,
    o.org_name,
    s.service_name
FROM appointments a
LEFT JOIN users u
    ON a.user_id = u.user_id
LEFT JOIN organizations o
    ON a.org_id = o.org_id
LEFT JOIN services s
    ON a.service_id = s.service_id
ORDER BY a.appointment_id DESC;
SELECT 1;
SHOW DATABASES;
SELECT @@version;
USE queue_management_db;