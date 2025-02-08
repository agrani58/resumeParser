import bcrypt
import mysql.connector
from datetime import  timezone

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="resume_parser"
    )

def create_session_token(email, token, expires_at):
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_sessions (session_token, email, expires_at)
                VALUES (%s, %s, %s)
            """, (token, email, expires_at.astimezone(timezone.utc).replace(tzinfo=None)))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        print(f"Session error: {err}")
        return False

def get_user_from_session_token(token):
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.email, u.username FROM user_sessions s
                JOIN users u ON s.email = u.email
                WHERE session_token = %s AND expires_at > UTC_TIMESTAMP()
            """, (token,))
            return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Session error: {err}")
        return None

def delete_session_token(token):
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("DELETE FROM user_sessions WHERE session_token = %s", (token,))
            conn.commit()
    except mysql.connector.Error as err:
        print(f"Delete error: {err}")

def create_user(email, username, password):
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor.execute("""
                INSERT INTO users (email, username, password, role_id)
                VALUES (%s, %s, %s, 1)
            """, (email, username, hashed))
            conn.commit()
            return True
    except mysql.connector.Error:
        return False

def verify_user(email, password):
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("SELECT email, username, password FROM users WHERE email = %s", (email,))
            if user := cursor.fetchone():
                if bcrypt.checkpw(password.encode(), user[2].encode()):
                    return {'status': True, 'username': user[1]}
                return {'status': False, 'username': None}
    except mysql.connector.Error as err:
        print(f"Auth error: {err}")
        return {'status': False, 'username': None}


ds_course = [['Machine Learning Crash Course by Google [Free]', 'https://developers.google.com/machine-learning/crash-course'],
            ['Machine Learning A-Z by Udemy','https://www.udemy.com/course/machinelearning/'],
            ['Machine Learning by Andrew NG','https://www.coursera.org/learn/machine-learning'],
            ['Data Scientist Master Program of Simplilearn (IBM)','https://www.simplilearn.com/big-data-and-analytics/senior-data-scientist-masters-program-training'],
            ['Data Science Foundations: Fundamentals by LinkedIn','https://www.linkedin.com/learning/data-science-foundations-fundamentals-5'],
            ['Data Scientist with Python','https://www.datacamp.com/tracks/data-scientist-with-python'],
            ['Programming for Data Science with Python','https://www.udacity.com/course/programming-for-data-science-nanodegree--nd104'],
            ['Programming for Data Science with R','https://www.udacity.com/course/programming-for-data-science-nanodegree-with-R--nd118'],
            ['Introduction to Data Science','https://www.udacity.com/course/introduction-to-data-science--cd0017'],
            ['Intro to Machine Learning with TensorFlow','https://www.udacity.com/course/intro-to-machine-learning-with-tensorflow-nanodegree--nd230']]

software_dev_course = [
            ['CS50’s Introduction to Computer Science  [Free]', 'https://cs50.harvard.edu/'],
            ['Google IT Automation with Python', 'https://www.coursera.org/professional-certificates/google-it-automation'],
            ['Python for Everybody ', 'https://www.coursera.org/specializations/python'],
            ['The Complete Java Developer Course ', 'https://www.udemy.com/course/java-the-complete-java-developer-course/'],
            ['Full-Stack Web Development with React ', 'https://www.coursera.org/specializations/full-stack-react'],
            ['AWS Certified Developer Associate', 'https://aws.amazon.com/certification/certified-developer-associate/'],
            ['The Odin Project  [Free]', 'https://www.theodinproject.com/'],
            ['Google Advanced Android Developer Certification', 'https://developer.android.com/certification/associate-android-developer'],
            ['Microsoft Certified: Azure Developer Associate', 'https://learn.microsoft.com/en-us/certifications/azure-developer/'],
            ['DevOps Engineer Certification ', 'https://www.udacity.com/course/devops-engineer-nanodegree--nd9991']
        ]

qa_course=qa_courses = [
    ['ISTQB Foundation Level Certification', 'https://www.istqb.org/certifications/foundation-level.html'],
    ['Certified Tester Advanced Level', 'https://www.istqb.org/certifications/advanced-level.html'],
    ['Automation Testing with Selenium & Java', 'https://www.udemy.com/course/selenium-webdriver-with-java-basics-to-advanced/'],
    ['Test Automation University by Applitools [Free]', 'https://testautomationu.applitools.com/'],
    ['Software Testing and Automation Specialization ', 'https://www.coursera.org/specializations/software-testing-automation'],
    ['SDET Automation Testing Course ', 'https://www.udemy.com/course/full-stack-automation-with-java/'],
    ['QA Software Testing Bootcamp ', 'https://www.linkedin.com/learning/software-testing-foundations'],
    ['DevOps Test Engineer Certification ', 'https://www.udacity.com/course/devops-engineer-nanodegree--nd9991'],
    ['Advanced Test Automation', 'https://www.udemy.com/course/advanced-test-automation/'],
    ['Cypress: End-to-End Testing', 'https://www.udemy.com/course/cypress-web-automation/']
]

web_course = [['Django Crash course [Free]','https://youtu.be/e1IyzVyrLSU'],
            ['Python and Django Full Stack Web Developer Bootcamp','https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp'],
            ['React Crash Course [Free]','https://youtu.be/Dorf8i6lCuk'],
            ['ReactJS Project Development Training','https://www.dotnettricks.com/training/masters-program/reactjs-certification-training'],
            ['Full Stack Web Developer - MEAN Stack','https://www.simplilearn.com/full-stack-web-developer-mean-stack-certification-training'],
            ['Node.js and Express.js [Free]','https://youtu.be/Oe421EPjeBE'],
            ['Flask: Develop Web Applications in Python','https://www.educative.io/courses/flask-develop-web-applications-in-python'],
            ['Full Stack Web Developer by Udacity','https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044'],
            ['Front End Web Developer by Udacity','https://www.udacity.com/course/front-end-web-developer-nanodegree--nd0011'],
            ['Become a React Developer by Udacity','https://www.udacity.com/course/react-nanodegree--nd019']]

android_course = [['Android Development for Beginners [Free]','https://youtu.be/fis26HvvDII'],
                ['Android App Development Specialization','https://www.coursera.org/specializations/android-app-development'],
                ['Associate Android Developer Certification','https://grow.google/androiddev/#?modal_active=none'],
                ['Become an Android Kotlin Developer by Udacity','https://www.udacity.com/course/android-kotlin-developer-nanodegree--nd940'],
                ['Android Basics by Google','https://www.udacity.com/course/android-basics-nanodegree-by-google--nd803'],
                ['The Complete Android Developer Course','https://www.udemy.com/course/complete-android-n-developer-course/'],
                ['Building an Android App with Architecture Components','https://www.linkedin.com/learning/building-an-android-app-with-architecture-components'],
                ['Android App Development Masterclass using Kotlin','https://www.udemy.com/course/android-oreo-kotlin-app-masterclass/'],
                ['Flutter & Dart - The Complete Flutter App Development Course','https://www.udemy.com/course/flutter-dart-the-complete-flutter-app-development-course/'],
                ['Flutter App Development Course [Free]','https://youtu.be/rZLR5olMR64']]

ios_course = [['IOS App Development by LinkedIn','https://www.linkedin.com/learning/subscription/topics/ios'],
            ['iOS & Swift - The Complete iOS App Development Bootcamp','https://www.udemy.com/course/ios-13-app-development-bootcamp/'],
            ['Become an iOS Developer','https://www.udacity.com/course/ios-developer-nanodegree--nd003'],
            ['iOS App Development with Swift Specialization','https://www.coursera.org/specializations/app-development'],
            ['Mobile App Development with Swift','https://www.edx.org/professional-certificate/curtinx-mobile-app-development-with-swift'],
            ['Swift Course by LinkedIn','https://www.linkedin.com/learning/subscription/topics/swift-2'],
            ['Objective-C Crash Course for Swift Developers','https://www.udemy.com/course/objectivec/'],
            ['Learn Swift by Codecademy','https://www.codecademy.com/learn/learn-swift'],
            ['Swift Tutorial - Full Course for Beginners [Free]','https://youtu.be/comQ1-x2a1Q'],
            ['Learn Swift Fast - [Free]','https://youtu.be/FcsY1YPBwzQ']]
uiux_course = [['Google UX Design Professional Certificate','https://www.coursera.org/professional-certificates/google-ux-design'],
            ['UI / UX Design Specialization','https://www.coursera.org/specializations/ui-ux-design'],
            ['The Complete App Design Course - UX, UI and Design Thinking','https://www.udemy.com/course/the-complete-app-design-course-ux-and-ui-design/'],
            ['UX & Web Design Master Course: Strategy, Design, Development','https://www.udemy.com/course/ux-web-design-master-course-strategy-design-development/'],
            ['The Complete App Design Course - UX, UI and Design Thinking','https://www.udemy.com/course/the-complete-app-design-course-ux-and-ui-design/'],
            ['DESIGN RULES: Principles + Practices for Great UI Design','https://www.udemy.com/course/design-rules/'],
            ['Become a UX Designer by Udacity','https://www.udacity.com/course/ux-designer-nanodegree--nd578'],
            ['Adobe XD Tutorial: User Experience Design Course [Free]','https://youtu.be/68w2VwalD5w'],
            ['Adobe XD for Beginners [Free]','https://youtu.be/WEljsc2jorI'],
            ['Adobe XD in Simple Way','https://learnux.io/course/adobe-xd']]

resume_videos = [
    'https://www.youtube.com/embed/3agP4x8LYFM',
    'https://www.youtube.com/embed/fS_t3yS8v5s',
    'https://www.youtube.com/embed/aArb68OBFPg',
    'https://www.youtube.com/embed/h-NuvOeWWh0',
    'https://www.youtube.com/embed/BdQniERyw8I',
    'https://www.youtube.com/embed/Tt08KmFfIYQ',
    'https://www.youtube.com/embed/CLUsplI4xMU',
    'https://www.youtube.com/embed/bhwEsfXS6y8',
    'https://www.youtube.com/embed/J5gy9iqjwXM',
    'https://www.youtube.com/embed/31EWjB_9Jig'
]

interview_videos = [
    'https://www.youtube.com/embed/KCm6JVtoRdo',
    'https://www.youtube.com/embed/ZU9x1vFx5lI',
    'https://www.youtube.com/embed/KukmClH1KoA',
    'https://www.youtube.com/embed/-3vtMt8zEp0',
    'https://www.youtube.com/embed/LCWr-TJrc0k',
    'https://www.youtube.com/embed/1mHjMNZZvFo',
    'https://www.youtube.com/embed/WfdtKbAJOmE',
    'https://www.youtube.com/embed/wFbU185CvDU',
    'https://www.youtube.com/embed/0siE31sqz0Q',
    'https://www.youtube.com/embed/TZ3C_syg9Ow'
]
