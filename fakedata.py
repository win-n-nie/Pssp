#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dbm
from hashlib import new
import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from faker import Faker
import uuid
import random 
load_dotenv()

AZURE_MYSQL_HOSTNAME = os.getenv("AZURE_MYSQL_HOSTNAME")
AZURE_MYSQL_USER = os.getenv("AZURE_MYSQL_USER")
AZURE_MYSQL_PASSWORD = os.getenv("AZURE_MYSQL_PASSWORD")
AZURE_MYSQL_DATABASE = os.getenv("AZURE_MYSQL_DATABASE")

connection_string_gcp = f'mysql+pymysql://{AZURE_MYSQL_USER}:{AZURE_MYSQL_PASSWORD}@{AZURE_MYSQL_HOSTNAME}:3306/{AZURE_MYSQL_DATABASE}'
db_azure = create_engine(connection_string_gcp)

fake = Faker()

fake_patients = [
       {
        #keep just the first 8 characters of the uuid
        'mrn': str(uuid.uuid4())[:8], 
        'first_name':fake.first_name(), 
        'last_name':fake.last_name(),
        'zip_code':fake.zipcode(),
        'dob':(fake.date_between(start_date='-90y', end_date='-20y')).strftime("%Y-%m-%d"),
        'gender': fake.random_element(elements=('M', 'F')),
        'contact_mobile':fake.phone_number(),
        'contact_home':fake.phone_number()
    } for x in range(10)]
df_fake_patients = pd.DataFrame(fake_patients)
df_fake_patients = df_fake_patients.drop_duplicates(subset=['mrn'])

#### real ndc codes
ndc_codes = pd.read_csv('https://raw.githubusercontent.com/hantswilliams/FDA_NDC_CODES/main/NDC_2022_product.csv')
ndc_codes_1k = ndc_codes.sample(n=1000, random_state=1)
# drop duplicates from ndc_codes_1k
ndc_codes_1k = ndc_codes_1k.drop_duplicates(subset=['PRODUCTNDC'], keep='first')

icd10codes = pd.read_csv('https://raw.githubusercontent.com/Bobrovskiy/ICD-10-CSV/master/2020/diagnosis.csv')
list(icd10codes.columns)
icd10codesShort = icd10codes[['CodeWithSeparator', 'ShortDescription']]
icd10codesShort_1k = icd10codesShort.sample(n=1000, random_state=1)

### cpt codes
cptcodes = pd.read_csv('https://gist.githubusercontent.com/lieldulev/439793dc3c5a6613b661c33d71fdd185/raw/25c3abcc5c24e640a0a5da1ee04198a824bf58fa/cpt4.csv')
list(cptcodes.columns)
newCPTcode = cptcodes.rename(columns={'com.medigy.persist.reference.type.clincial.CPT.code':'CPT_code', 'label':'CPT_description'})
newCPTcode.sample(n=100)

##treatment/procedure fake data
insertQuery = "INSERT INTO treatments_procedures (CPT_code, CPT_description) VALUES (%s, %s)"
startingRow = 0
for index, row in newCPTcode.iterrows():
    startingRow += 1
    print('startingRow: ', startingRow)
    # db_azure.execute(insertQuery, (row['CodeWithSeparator'], row['ShortDescription']))
    print("inserted row db_azure: ", index)
    db_azure.execute(insertQuery, (row['CPT_code'], row['CPT_description']))
    print("inserted row db_gcp: ", index)
    ## stop once we have 100 rows
    if startingRow == 60:
        break

###LOINC
loinc = pd.read_csv('/Users/wendyarias/Desktop/GitHub/cloud-managed-MySQL/Loinc.csv')
list(loinc.columns)
shortloinc= loinc[['LOINC_NUM', 'COMPONENT']]
LOINCnew = shortloinc.sample(n=50)
insertQuery = "INSERT INTO social_determinants (LOINC_NUM, COMPONENT) VALUES (%s, %s)"
startingRow = 0
for index, row in LOINCnew.iterrows():
    startingRow += 1
    print('startingRow: ', startingRow)
    # db_azure.execute(insertQuery, (row['CodeWithSeparator'], row['ShortDescription']))
    print("inserted row db_azure: ", index)
    db_azure.execute(insertQuery, (row['LOINC_NUM'], row['COMPONENT']))
    print("inserted row db_gcp: ", index)
    ## stop once we have 100 rows
    if startingRow == 60:
        break

### inserting fake data 

insertQuery = "INSERT INTO patients (mrn, first_name, last_name, zip_code, dob, gender, contact_mobile, contact_home) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

for index, row in df_fake_patients.iterrows():

    db_azure.execute(insertQuery, (row['mrn'], row['first_name'], row['last_name'], row['zip_code'], row['dob'], row['gender'], row['contact_mobile'], row['contact_home']))
    print("inserted row: ", index)



########## INSERTING IN FAKE MEDICATIONS ##########

df_medications = pd.read_sql_query("SELECT med_ndc FROM medications", db_azure) 
df_patients= pd.read_sql_query("SELECT mrn FROM patients", db_azure)
# create a dataframe that is stacked and give each patient a random number of medications between 1 and 5
df_patient_medications = pd.DataFrame(columns=['mrn', 'med_ndc'])
# for each patient in df_patient_medications, take a random number of medications between 1 and 10 from df_medications and palce it in df_patient_medications
for index, row in df_patients.iterrows():
    # get a random number of medications between 1 and 5
    numMedications = random.randint(3, 5)
    # get a random sample of medications from df_medications
    df_medications_sample = df_medications.sample(n=numMedications)
    # add the mrn to the df_medications_sample
    df_medications_sample['mrn'] = row['mrn']
    # append the df_medications_sample to df_patient_medications
    df_patient_medications = df_patient_medications.append(df_medications_sample)

print(df_patient_medications.head(10))

insertQuery = "INSERT INTO medications (mrn, med_ndc, med_human_name) VALUES (%s, %s, %s)"

medRowCount = 0
for index, row in ndc_codes_1k.iterrows():
    medRowCount += 1
    # db_azure.execute(insertQuery, (row['PRODUCTNDC'], row['NONPROPRIETARYNAME']))
    db_azure.execute(insertQuery, (row['PRODUCTNDC'], row['NONPROPRIETARYNAME']))
    print("inserted row: ", index)
    ## stop once we have 50 rows
    if medRowCount == 75:
        break


##patient conditions data
insertQuery = "INSERT INTO patient_conditions (mrn, icd10_code, icd10_description) VALUES (%s, %s, %s)"

startingRow = 0
for index, row in icd10codesShort_1k.iterrows():
    startingRow += 1
    print('startingRow: ', startingRow)
    # db_azure.execute(insertQuery, (row['CodeWithSeparator'], row['ShortDescription']))
    print("inserted row db_azure: ", index)
    db_azure.execute(insertQuery, (row['mrn'], row['CodeWithSeparator'], row['ShortDescription']))
    print("inserted row db_gcp: ", index)
    ## stop once we have 100 rows
    if startingRow == 100:
        break
