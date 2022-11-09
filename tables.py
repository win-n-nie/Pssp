import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()
AZURE_MYSQL_HOSTNAME = os.getenv("AZURE_MYSQL_HOSTNAME")
AZURE_MYSQL_USER = os.getenv("AZURE_MYSQL_USER")
AZURE_MYSQL_PASSWORD = os.getenv("AZURE_MYSQL_PASSWORD")
AZURE_MYSQL_DATABASE = os.getenv("AZURE_MYSQL_DATABASE")


connection_string_azure = f'mysql+pymysql://{AZURE_MYSQL_USER}:{AZURE_MYSQL_PASSWORD}@{AZURE_MYSQL_HOSTNAME}:3306/{AZURE_MYSQL_DATABASE}'
db_azure = create_engine(connection_string_azure)


table_patients = """
create table if not exists patients (
    id int auto_increment,
    mrn varchar(255) default null unique,
    first_name varchar(255) default null,
    last_name varchar(255) default null,
    zip_code varchar(255) default null,
    dob varchar(255) default null,
    gender varchar(255) default null,
    contact_mobile varchar(255) default null,
    contact_home varchar(255) default null,
    PRIMARY KEY (id) 
); 
"""
table_medications = """
create table if not exists medications (
    id int auto_increment,
    med_ndc varchar(255) default null unique,
    med_human_name varchar(255) default null,
    PRIMARY KEY (id)
    );
"""

table_pat_medications = """
create table if not exists patient_medications (
    id int auto_increment,
    mrn varchar(255) default null,
    med_ndc varchar(255) default null unique,
    PRIMARY KEY (id),
    FOREIGN KEY (mrn) REFERENCES patients(mrn) ON DELETE CASCADE,
    FOREIGN KEY (med_ndc) REFERENCES medications(med_ndc) ON DELETE CASCADE
); 
"""

table_treatments_procedures = """
create table if not exists treatments_procedures (
    id int auto_increment,
    CPT_code varchar(255) default null,
    CPT_description varchar(255) default null,
    PRIMARY KEY (id)
);
"""
table_pat_procedures = """
create table if not exists patient_procedures(
    id int auto_increment,
    mrn varchar(255) default null,
    CPT_description varchar(255) default null,
    PRIMARY KEY (id),
    FOREIGN KEY (mrn) REFERENCES patients(mrn) ON DELETE CASCADE,
    FOREIGN KEY (CPT_description) REFERENCES treatments_procedures(CPT_description) ON DELETE CASCADE
);
"""
table_condition = """
create table if not exists conditions (
    id int auto_increment,
    icd10_code varchar(255) default null unique,
    icd10_description varchar(255) default null,
    PRIMARY KEY (id)
); 
"""
table_pat_conditions = """
create table if not exists patient_conditions (
    id int auto_increment,
    mrn varchar(255),
    icd10_code varchar(255) default null unique,
    PRIMARY KEY (id),
    FOREIGN KEY (mrn) REFERENCES patients(mrn) ON DELETE CASCADE,
    FOREIGN KEY (icd10_code) REFERENCES conditions(icd10_code) ON DELETE CASCADE

); 
"""

table_social_determinants = """
create table if not exists social_determinants(
    id int auto_increment,
    LOINC_NUM varchar(255) default null,
    COMPONENT varchar(255) default null,
    PRIMARY KEY (id)
);
"""

db_azure.execute(table_patients)

db_azure.execute(table_medications)

db_azure.execute(table_pat_medications)

db_azure.execute(table_treatments_procedures)
db_azure.execute(table_pat_procedures)

db_azure.execute(table_condition)
db_azure.execute(table_pat_conditions)

db_azure.execute(table_social_determinants)