CREATE TABLE locomotives (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    model VARCHAR(100) NOT NULL,
    built_in DATE NOT NULL,
    mezuri_install_date DATE NOT NULL,
    mezure_sn VARCHAR(100) NOT NULL,
    mezure_version VARCHAR(50) NOT NULL
);

CREATE TABLE egu (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    locomotive_id BIGINT NOT NULL,
    time_stamp DATETIME NOT NULL,
    value_1 DOUBLE,
    value_2 DOUBLE,
    value_3 DOUBLE,
    value_4 DOUBLE,
    value_5 DOUBLE,
    value_6 DOUBLE,
    value_7 DOUBLE,
    value_8 DOUBLE,
    FOREIGN KEY (locomotive_id) REFERENCES locomotives(id) ON DELETE CASCADE,
    INDEX idx_egu_locomotive_time (locomotive_id, time_stamp)
);

CREATE TABLE exc (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    locomotive_id BIGINT NOT NULL,
    time_stamp DATETIME NOT NULL,
    value_1 DOUBLE,
    value_2 DOUBLE,
    value_3 DOUBLE,
    value_4 DOUBLE,
    value_5 DOUBLE,
    value_6 DOUBLE,
    value_7 DOUBLE,
    value_8 DOUBLE,
    value_9 DOUBLE,
    value_10 DOUBLE,
    value_11 DOUBLE,
    value_12 DOUBLE,
    value_13 DOUBLE,
    value_14 DOUBLE,
    value_15 DOUBLE,
    value_16 DOUBLE,
    value_17 DOUBLE,
    value_18 DOUBLE,
    value_19 DOUBLE,
    value_20 DOUBLE,
    FOREIGN KEY (locomotive_id) REFERENCES locomotives(id) ON DELETE CASCADE,
    INDEX idx_exc_locomotive_time (locomotive_id, time_stamp)
);

CREATE TABLE cab (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    locomotive_id BIGINT NOT NULL,
    time_stamp DATETIME NOT NULL,
    value_1 VARCHAR(255),
    value_2 VARCHAR(255),
    value_3 VARCHAR(255),
    value_4 VARCHAR(255),
    value_5 VARCHAR(255),
    value_6 VARCHAR(255),
    value_7 VARCHAR(255),
    value_8 VARCHAR(255),
    value_9 VARCHAR(255),
    value_10 VARCHAR(255),
    FOREIGN KEY (locomotive_id) REFERENCES locomotives(id) ON DELETE CASCADE,
    INDEX idx_cab_locomotive_time (locomotive_id, time_stamp)
);

CREATE TABLE aux (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    locomotive_id BIGINT NOT NULL,
    time_stamp DATETIME NOT NULL,
    value_1 DOUBLE,
    value_2 DOUBLE,
    value_3 DOUBLE,
    value_4 DOUBLE,
    value_5 DOUBLE,
    FOREIGN KEY (locomotive_id) REFERENCES locomotives(id) ON DELETE CASCADE,
    INDEX idx_aux_locomotive_time (locomotive_id, time_stamp)
);

CREATE TABLE gps (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    locomotive_id BIGINT NOT NULL,
    time_stamp DATETIME NOT NULL,
    gps_timestamp DATETIME NOT NULL,
    gps_status ENUM('A', 'V') NOT NULL,
    gps_lat DECIMAL(9,6) NOT NULL,
    gps_lon DECIMAL(9,6) NOT NULL,
    gps_mag_variation DECIMAL(5,2),
    gps_mag_var_dir ENUM('E', 'W'),
    gps_speed_on_ground DECIMAL(5,2),
    gps_true_course DECIMAL(6,2),
    FOREIGN KEY (locomotive_id) REFERENCES locomotives(id) ON DELETE CASCADE,
    INDEX idx_gps_locomotive_time (locomotive_id, gps_timestamp)
);
