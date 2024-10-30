

#Schema for each milestone in the database
SCHEMAS = { 
  "Milestone_1": [   #Milestone 1
    {
    "name": "term_start_date",
      "type": "date",
      "required": True,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "enableTime": False
      },
      "description": "The start date of the teaching period"
    },
    {
      "name": "completion_time",
      "type": "date",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "enableTime": True
      },
      "description": "Completion time of the milestone"
    },
    {
      "name": "email",
      "type": "email",
      "required": False,
      "unique": False,
      "options": {},
      "description": "User's email address"
    },
    {
      "name": "name",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "User's full name"
    },
    {
      "name": "subject_coordinator",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Name of the subject coordinator"
    },
    {
      "name": "subject_code_and_name",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Subject code and name"
    },
    {
      "name": "subject_lms_link",
      "type": "url",
      "required": False,
      "unique": False,
      "options": {},
      "description": "URL to the subject in the Learning Management System"
    },
    {
      "name": "Verify_Assessments_Weightings_2Weeks",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Verify assessments, weightings, types, and hurdles, to match CourseLoop."
    },
    {
      "name": "Ensure_LMS_Access_2Weeks",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Ensure LMS site is setup to allow student access and remove access 12 months after the final grade."
    },
    {
      "name": "Setup_Welcome_Message_LMS_2Weeks",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Ensure setup of Welcome message on LMS homepage, with learning materials and the latest Subject Learning Guide."
    },
    {
      "name": "Add_Teaching_Team_Contact_1Week",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Add Teaching team contact details, including role, title, portrait, and bios."
    },
    {
      "name": "Add_Welcome_Post_1Week",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Add Welcome post to Announcement."
    },
    {
      "name": "Add_Introduce_Yourself_Post_1Week",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Add Introduce Yourself Discussion/Padlet post."
    },
    {
      "name": "Verify_Timetable_Accuracy_By_Week1",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Verify timetable accuracy in Allocate+ and schedule relevant live online sessions."
    },
    {
      "name": "Schedule_Student_Consults_By_Week1",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Schedule live student consults per week, preferably in break time or after hours."
    },
    {
      "name": "Ensure_First_Assessment_Details_By_Week1",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Ensure the first assessment details are prepared, including Turnitin enabled submission folders, with grades and rubrics."
    },
    {
      "name": "Engage_Forums_Respond_2Days_Initial_Weeks",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Engage regularly on forums and respond to students within 2 business days."
    },
    {
      "name": "Add_Weekly_Overview_Post_Beginning_Week1",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Add weekly overview/review post to Announcement, summarizing key points and connecting with upcoming learning."
    },
    {
      "name": "Upload_Live_Session_Recording_2Days",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Upload live session recording links to LMS within 2 business days."
    },
    {
      "name": "post_assignment_reminder",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Post assessment and support reminder to Announcement a week before due date, where relevant."
    },
    {
      "name": "accommodate_lap_requirements",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Accommodate student LAP requirements (e.g., adjusting Quiz/assessment, learning resources, delivery, communications, etc.)"
    },
    {
      "name": "additional_comments",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Additional comments"
    },
        {
    "name": "academic_period",
    "type": "select",
    "required": False,
    "unique": False,
    "options": {
      "values": ["Term", "Semester"],
      "default": "Term",
      "maxSelect": 1
    }
        },

  ],

  "Milestone_2": [
    {
    "name": "term_start_date",
      "type": "date",
      "required": True,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "enableTime": False
      },
      "description": "The start date of the teaching period"
    },
    {
      "name": "completion_time",
      "type": "date",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "enableTime": True
      },
      "description": "Completion time of the milestone"
    },
    {
      "name": "email",
      "type": "email",
      "required": False,
      "unique": False,
      "options": {},
      "description": "User's email address"
    },
    {
      "name": "name",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "User's full name"
    },
    {
      "name": "subject_coordinator",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Name of the subject coordinator"
    },
    {
      "name": "subject_code_and_name",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Subject code and name"
    },
    {
      "name": "subject_lms_link",
      "type": "url",
      "required": False,
      "unique": False,
      "options": {},
      "description": "URL to the subject in the Learning Management System"
    },
    {
      "name": "respond_in_2_days",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Engage on forums and respond to students within 2 business days"
    },
    {
      "name": "add_weekly_overview",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Add weekly overview/review post to Announcement"
    },
    {
      "name": "upload_live_session",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Upload live session recording links to LMS within 2 business days (1 day for Term subjects)"
    },
    {
      "name": "ensure_lms_materials_ready",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Ensure LMS materials are ready each week and compliant"
    },
    {
      "name": "ensure_remaining_assessments",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Ensure assessment details and submission folders are set up"
    },
    {
      "name": "post_assignment_reminder",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Post assessment and support reminder to Announcement a week before due date, where relevant"
    },
    {
      "name": "accommodate_lap_requirements",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Weeks 2 & 3 - Accommodate student LAP requirements (e.g., adjusting Quiz/assessment, learning resources, delivery, communications, etc.)"
    },
    {
      "name": "additional_comments",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Additional comments"
    },
    {
    "name": "academic_period",
    "type": "select",
    "required": False,
    "unique": False,
    "options": {
      "values": ["Term", "Semester"],
      "default": "Term",
      "maxSelect": 1
    },
    }
    ],
    
   "Milestone_3": [
       {
    "name": "term_start_date",
      "type": "date",
      "required": True,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "enableTime": False
      },
      "description": "The start date of the teaching period"
    },
    {
      "name": "completion_time",
      "type": "date",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "enableTime": True
      },
      "description": "Completion time of the milestone"
    },
    {
      "name": "email",
      "type": "email",
      "required": False,
      "unique": False,
      "options": {},
      "description": "User's email address"
    },
    {
      "name": "name",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "User's full name"
    },
    {
      "name": "subject_coordinator",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Name of the subject coordinator"
    },
    {
      "name": "subject_code_and_name",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Subject code and name"
    },
    {
      "name": "subject_lms_link",
      "type": "url",
      "required": False,
      "unique": False,
      "options": {},
      "description": "URL to the subject in the Learning Management System"
    },
    {
      "name": "Engage_Forums_Respond_2Days_Weeks_4_5_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Engage regularly on forums and respond to students within 2 business days."
    },
    {
      "name": "Add_Weekly_Overview_Post_Weeks_4_5_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Add weekly overview/review post to Announcement, summarizing key points and connecting with upcoming learning, including live session reminders."
    },
    {
      "name": "Upload_Live_Session_Recording_2Days_Weeks_4_5_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Upload live session recording links to LMS within 2 business days (1 day for Term subjects)."
    },
    {
      "name": "Ensure_LMS_Materials_Ready_Weeks_4_5_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Ensure remainder of LMS learning materials are ready each week and compliant with copyright."
    },
    {
      "name": "Ensure_Remaining_Assessments_Weeks_4_5_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Ensure remaining assessment details are available, including Turnitin enabled submission folders, with grades and rubrics."
    },
    {
      "name": "Post_Assessment_Reminder_Weeks_4_5_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Post assessment and support reminder to Announcement a week before due date, where relevant."
    },
    {
      "name": "Accommodate_LAP_Requirements_Weeks_4_5_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Accommodate student LAP requirements (e.g., adjusting Quiz/assessment, learning resources, delivery, communications, etc.)."
    },
    {
      "name": "Add_SFS_Survey_Weeks_5_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Add SFS survey to Announcement post and live session presentation slides."
    },
    {
      "name": "Post_End_Of_Subject_Review_Week_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Post end of subject review and well wishes on Announcement to students."
    },
    {
      "name": "Hide_LMS_Exam_Grades_Week_6",
      "type": "bool",
      "required": False,
      "unique": False,
      "options": {},
      "description": "Hide LMS exam grades, final marks, assessment rubrics, grade, and lock discussions at the end of the term."
    },
    {
      "name": "additional_comments",
      "type": "text",
      "required": False,
      "unique": False,
      "options": {
        "min": None,
        "max": None,
        "pattern": None
      },
      "description": "Additional comments"
    },
    {
    "name": "academic_period",
    "type": "select",
    "required": False,
    "unique": False,
    "options": {
      "values": ["Term", "Semester"],
      "default": "Term",
      "maxSelect": 1
    }
    }
   ],
}