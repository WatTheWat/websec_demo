CREATE TABLE  userdata  (
  id  int NOT NULL AUTO_INCREMENT,
  username  varchar(45) NOT NULL,
  email  varchar(45) NOT NULL,
  password  varchar(255) NOT NULL,
 PRIMARY KEY ( id ),
 UNIQUE KEY  id_UNIQUE  ( id )
)