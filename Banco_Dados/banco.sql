CREATE DATABASE locomotive_MBC;

USE locomotive_MBC;

CREATE TABLE locomotives (
    id INT AUTO_INCREMENT PRIMARY KEY,              -- Unique identifier for each locomotive
    model VARCHAR(255) NOT NULL,                    -- Model name or identifier of the locomotive
    built_in DATE,                                  -- Date the locomotive was built
    mezuri_install_date DATE ,                      -- Date the locomotives mezure was installed
    mezure_SN VARCHAR(255),                         -- Serial number for the measurement system
    mezure_version VARCHAR(255)                     -- Version of the measurement system
);

CREATE TABLE LOCOMOTIVAS (
    id INT AUTO_INCREMENT PRIMARY KEY,              
    locomotiva VARCHAR(255) UNIQUE NOT NULL,     
    serial VARCHAR(255),
    imei VARCHAR(255),
    lan_mac VARCHAR(255),
    wifi_ssid VARCHAR(255),
    wifi_password VARCHAR(255),
    username VARCHAR(255),
    password VARCHAR(255),
    operadora VARCHAR(255),
    chip VARCHAR(255),
    data_ativacao DATE,
    data_instalacao DATE                  
);


CREATE TABLE EGU ( -- EGU data max 8 values
    data_EGU_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_locomotiva INT,
    FOREIGN KEY (id_locomotiva) REFERENCES LOCOMOTIVAS(id) ON DELETE CASCADE,
    time_stamp DATETIME,
    value_EGU_1 DOUBLE,
    value_EGU_2 DOUBLE,
    value_EGU_3 DOUBLE,
    value_EGU_4 DOUBLE,
    value_EGU_5 DOUBLE,
    value_EGU_6 DOUBLE,
    value_EGU_7 DOUBLE,
    value_EGU_8 DOUBLE
);

CREATE TABLE EXC (
    data_EXC_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_locomotiva INT,
    FOREIGN KEY (id_locomotiva) REFERENCES LOCOMOTIVAS(id) ON DELETE CASCADE,
    time_stamp DATETIME,
    value_EXC_1 DOUBLE,
    value_EXC_2 DOUBLE,
    value_EXC_3 DOUBLE,
    value_EXC_4 DOUBLE,
    value_EXC_5 DOUBLE,
    value_EXC_6 DOUBLE,
    value_EXC_7 DOUBLE,
    value_EXC_8 DOUBLE,
    value_EXC_9 DOUBLE,
    value_EXC_10 DOUBLE,
    value_EXC_11 DOUBLE,
    value_EXC_12 DOUBLE,
    value_EXC_13 DOUBLE,
    value_EXC_14 DOUBLE,
    value_EXC_15 DOUBLE,
    value_EXC_16 DOUBLE,
    value_EXC_17 DOUBLE,
    value_EXC_18 DOUBLE,
    value_EXC_19 DOUBLE,
    value_EXC_20 DOUBLE
);

CREATE TABLE CAB (
    data_CAB_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_locomotiva INT,
    FOREIGN KEY (id_locomotiva) REFERENCES LOCOMOTIVAS(id) ON DELETE CASCADE,
    time_stamp DATETIME,
    value_CAB_1 VARCHAR(255),
    value_CAB_2 VARCHAR(255),
    value_CAB_3 VARCHAR(255),
    value_CAB_4 VARCHAR(255),
    value_CAB_5 VARCHAR(255),
    value_CAB_6 VARCHAR(255),
    value_CAB_7 VARCHAR(255),
    value_CAB_8 VARCHAR(255),
    value_CAB_9 VARCHAR(255),
    value_CAB_10 VARCHAR(255)
);

CREATE TABLE AUX (
    data_AUX_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_locomotiva INT,
    FOREIGN KEY (id_locomotiva) REFERENCES LOCOMOTIVAS(id) ON DELETE CASCADE,
    time_stamp DATETIME,
    value_AUX_1 DOUBLE,
    value_AUX_2 DOUBLE,
    value_AUX_3 DOUBLE,
    value_AUX_4 DOUBLE,
    value_AUX_5 DOUBLE
);

CREATE TABLE GPS (
    data_GPS_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    locomotive INT,
    FOREIGN KEY (locomotive) REFERENCES locomotives(locomotive) ON DELETE CASCADE,
    time_stamp DATETIME,
    gps_timestamp DATETIME NOT NULL,
    gps_status ENUM('A', 'V') NOT NULL,
    gps_lat DECIMAL(9,6) NOT NULL,
    gps_lon DECIMAL(9,6) NOT NULL,
    gps_mag_variation DECIMAL(5,2),
    gps_mag_var_dir ENUM('E', 'W'),
    gps_speed_on_ground DECIMAL(5,2),
    gps_true_course DECIMAL(6,2)
);