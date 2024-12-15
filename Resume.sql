# resume DataBase
create database resume;
use resume;
-- drop table user_data

CREATE TABLE user_data (
      ID INT AUTO_INCREMENT PRIMARY KEY,
      Name VARCHAR(50) NOT NULL,
      Email_ID VARCHAR(50) NOT NULL,
      Resume_score VARCHAR(8) NOT NULL,
      Timestamp VARCHAR(50) NOT NULL,
      Page_no VARCHAR(5) NOT NULL,
      Predicted_field BLOB NOT NULL,
      User_level BLOB NOT NULL,
      Actual_skills BLOB NOT NULL,
      Recommended_skills BLOB NOT NULL,
      Recommended_courses BLOB NOT NULL,

    #text data type to store unlimited characters
);

DESCRIBE user_data;
select * from user_data;

