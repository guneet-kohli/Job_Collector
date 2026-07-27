jobbot/
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── main.py
│
├── config.py                  # keywords, locations, settings
│
├── resumes/
│   ├── master_resume.pdf
│   ├── tailored/
│   └── cover_letters/
│
├── data/
│   ├── jobs.csv
│   ├── ranked_jobs.csv
│   ├── applied_jobs.csv
│   └── companies.csv
│
├── logs/
│   └── run.log
│
├── playwright/
│   └── linkedin_state.json
│
├── modules/
│   │
│   ├── login.py
│   ├── linkedin_collector.py
│   ├── job_details.py
│   ├── resume_parser.py
│   ├── matcher.py
│   ├── resume_optimizer.py
│   ├── cover_letter.py
│   ├── tracker.py
│   └── utils.py
│
├── prompts/
│   ├── resume_prompt.txt
│   └── coverletter_prompt.txt
│
└── output/
    ├── screenshots/
    └── debug/