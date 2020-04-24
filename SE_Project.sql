PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE PRODUCT( PRODUCT_ID INT PRIMARY KEY, NAME TEXT, CATEGORY_ID INT, PRICE INT);
CREATE TABLE CREDENTIALS( USER_ID INT PRIMARY KEY, EMAIL_ID TEXT, PASSWORD TEXT);
CREATE TABLE USER( USER_ID INT PRIMARY KEY, NAME TEXT , EMAIL_ID TEXT , GENDER TEXT, AGE INT , FOREIGN KEY(EMAIL_ID) REFERENCES CREDENTIALS(EMAIL_ID));
CREATE table MEALDETAILS( MEAL_ID INT PRIMARY KEY, NAME TEXT NOT NULL, PRICE INT NOT NULL, AVAILABILITY INT NOT NULL, CUISINE TEXT NOT NULL );
CREATE TABLE MEAL( MEAL_ID INT, PRODUCT_ID INT, PRIMARY KEY (MEAL_ID, PRODUCT_ID), FOREIGN KEY(MEAL_ID) REFERENCES MEALDETAILS(MEAL_ID), FOREIGN KEY(PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID));
CREATE TABLE CART( USER_ID INT NOT NULL, PRODUCT_ID INT NOT NULL, PRIMARY KEY(USER_ID, PRODUCT_ID), FOREIGN KEY(USER_ID) REFERENCES USER(USER_ID), FOREIGN KEY(PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID));
CREATE TABLE USERDETAILS( USER_ID INT PRIMARY KEY, FAV_CUISINE TEXT, SPICINESS TEXT, LOCATION TEXT,FOREIGN KEY(USER_ID) REFERENCES USER(USER_ID));
CREATE TABLE USERALLERGIES( USER_ID INT, PRODUCT_ID INT, PRIMARY KEY(USER_ID, PRODUCT_ID), FOREIGN KEY(USER_ID) REFERENCES USER(USER_ID), FOREIGN KEY(PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID));
COMMIT;