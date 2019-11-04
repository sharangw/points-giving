CREATE TABLE employee (
    employeeid       INTEGER NOT NULL,
    name             VARCHAR(25) NOT NULL,
    password         VARCHAR(20) NOT NULL,
    pointsreceived   INTEGER NOT NULL,
    pointsgiven      INTEGER NOT NULL,
    admin            CHAR(1) NOT NULL
);

ALTER TABLE points.employee ADD CONSTRAINT employee_pk PRIMARY KEY ( employeeid );

CREATE TABLE points.redemption (
    redemptionid          INTEGER NOT NULL,
    points                INTEGER NOT NULL,
    redemptiondate        DATE NOT NULL,
    employee_employeeid   INTEGER NOT NULL,
    employeeid            INTEGER NOT NULL
);

ALTER TABLE points.redemption ADD CONSTRAINT redemption_pk PRIMARY KEY ( redemptionid );

CREATE TABLE points.transaction (
    transactionid     INTEGER NOT NULL,
    transactiondate   DATE NOT NULL,
    points            INTEGER NOT NULL,
    senderid          INTEGER NOT NULL,
    receiverid        INTEGER NOT NULL
);

ALTER TABLE points.transaction ADD CONSTRAINT transaction_pk PRIMARY KEY ( transactionid );

ALTER TABLE points.redemption
    ADD CONSTRAINT redemption_employee_fk FOREIGN KEY ( employee_employeeid )
        REFERENCES points.employee ( employeeid );

ALTER TABLE points.transaction
    ADD CONSTRAINT transaction_employee_fk FOREIGN KEY ( receiverid )
        REFERENCES points.employee ( employeeid );

ALTER TABLE points.transaction
    ADD CONSTRAINT transaction_employee_fkv2 FOREIGN KEY ( senderid )
        REFERENCES points.employee ( employeeid );



-- Oracle SQL Developer Data Modeler Summary Report: 
-- 
-- CREATE TABLE                             3
-- CREATE INDEX                             0
-- ALTER TABLE                              6
-- CREATE VIEW                              0
-- ALTER VIEW                               0
-- CREATE PACKAGE                           0
-- CREATE PACKAGE BODY                      0
-- CREATE PROCEDURE                         0
-- CREATE FUNCTION                          0
-- CREATE TRIGGER                           0
-- ALTER TRIGGER                            0
-- CREATE COLLECTION TYPE                   0
-- CREATE STRUCTURED TYPE                   0
-- CREATE STRUCTURED TYPE BODY              0
-- CREATE CLUSTER                           0
-- CREATE CONTEXT                           0
-- CREATE DATABASE                          0
-- CREATE DIMENSION                         0
-- CREATE DIRECTORY                         0
-- CREATE DISK GROUP                        0
-- CREATE ROLE                              0
-- CREATE ROLLBACK SEGMENT                  0
-- CREATE SEQUENCE                          0
-- CREATE MATERIALIZED VIEW                 0
-- CREATE MATERIALIZED VIEW LOG             0
-- CREATE SYNONYM                           0
-- CREATE TABLESPACE                        0
-- CREATE USER                              0
-- 
-- DROP TABLESPACE                          0
-- DROP DATABASE                            0
-- 
-- REDACTION POLICY                         0
-- 
-- ORDS DROP SCHEMA                         0
-- ORDS ENABLE SCHEMA                       0
-- ORDS ENABLE OBJECT                       0
-- 
-- ERRORS                                   0
-- WARNINGS                                 0
