import pandas as pd
import re
import os


def extract_skills_pipeline():
    skills_data = [
        # --- 1. Programming / Scripting Languages ---
        {"skill_id": 1, "skill_name": "Python", "skill_category": "Programming Language", "normalized_form": "python",
         "pattern": r"\bpython\b"},
        {"skill_id": 2, "skill_name": "Java", "skill_category": "Programming Language", "normalized_form": "java",
         "pattern": r"\bjava\b"},
        {"skill_id": 3, "skill_name": "C++", "skill_category": "Programming Language", "normalized_form": "c++",
         "pattern": r"\bc\+\+\b"},
        {"skill_id": 4, "skill_name": "C#", "skill_category": "Programming Language", "normalized_form": "c#",
         "pattern": r"\bc#\b|\bc\s*sharp\b"},
        {"skill_id": 5, "skill_name": "JavaScript", "skill_category": "Programming Language",
         "normalized_form": "javascript", "pattern": r"\bjavascript\b|\bjs\b"},
        {"skill_id": 6, "skill_name": "TypeScript", "skill_category": "Programming Language",
         "normalized_form": "typescript", "pattern": r"\btypescript\b|\bts\b"},
        {"skill_id": 7, "skill_name": "PHP", "skill_category": "Programming Language", "normalized_form": "php",
         "pattern": r"\bphp\b"},
        {"skill_id": 8, "skill_name": "Ruby", "skill_category": "Programming Language", "normalized_form": "ruby",
         "pattern": r"\bruby\b"},
        {"skill_id": 9, "skill_name": "Go", "skill_category": "Programming Language", "normalized_form": "golang",
         "pattern": r"\bgo\b|\bgolang\b"},
        {"skill_id": 10, "skill_name": "Swift", "skill_category": "Programming Language", "normalized_form": "swift",
         "pattern": r"\bswift\b"},
        {"skill_id": 11, "skill_name": "Kotlin", "skill_category": "Programming Language", "normalized_form": "kotlin",
         "pattern": r"\bkotlin\b"},
        {"skill_id": 12, "skill_name": "SQL", "skill_category": "Programming Language", "normalized_form": "sql",
         "pattern": r"\bsql\b"},
        {"skill_id": 13, "skill_name": "R", "skill_category": "Programming Language", "normalized_form": "r",
         "pattern": r"\br\b"},
        {"skill_id": 14, "skill_name": "Scala", "skill_category": "Programming Language", "normalized_form": "scala",
         "pattern": r"\bscala\b"},
        {"skill_id": 15, "skill_name": "Rust", "skill_category": "Programming Language", "normalized_form": "rust",
         "pattern": r"\brust\b"},
        {"skill_id": 16, "skill_name": "Dart", "skill_category": "Programming Language", "normalized_form": "dart",
         "pattern": r"\bdart\b"},
        {"skill_id": 17, "skill_name": "Objective-C", "skill_category": "Programming Language",
         "normalized_form": "objective-c", "pattern": r"\bobjective-c\b|\bobj-c\b"},
        {"skill_id": 18, "skill_name": "Shell / Bash", "skill_category": "Programming Language",
         "normalized_form": "shell", "pattern": r"\bshell\b|\bbash\b|\bpowershell\b"},
        {"skill_id": 19, "skill_name": "Perl", "skill_category": "Programming Language", "normalized_form": "perl",
         "pattern": r"\bperl\b"},

        # --- 2. Frontend & UI/UX ---
        {"skill_id": 20, "skill_name": "HTML/CSS", "skill_category": "Frontend", "normalized_form": "html/css",
         "pattern": r"\bhtml5?\b|\bcss3?\b"},
        {"skill_id": 21, "skill_name": "ReactJS", "skill_category": "Frontend", "normalized_form": "react",
         "pattern": r"\breact\b|\breactjs\b"},
        {"skill_id": 22, "skill_name": "Angular", "skill_category": "Frontend", "normalized_form": "angular",
         "pattern": r"\bangular\b|\bangularjs\b"},
        {"skill_id": 23, "skill_name": "VueJS", "skill_category": "Frontend", "normalized_form": "vue",
         "pattern": r"\bvue\b|\bvuejs\b"},
        {"skill_id": 24, "skill_name": "Next.js", "skill_category": "Frontend", "normalized_form": "nextjs",
         "pattern": r"\bnext\.?js\b"},
        {"skill_id": 25, "skill_name": "Nuxt.js", "skill_category": "Frontend", "normalized_form": "nuxtjs",
         "pattern": r"\bnuxt\.?js\b|\bnuxt\b"},
        {"skill_id": 26, "skill_name": "Svelte", "skill_category": "Frontend", "normalized_form": "svelte",
         "pattern": r"\bsvelte\b"},
        {"skill_id": 27, "skill_name": "Tailwind CSS", "skill_category": "Frontend", "normalized_form": "tailwind",
         "pattern": r"\btailwind(?:css)?\b"},
        {"skill_id": 28, "skill_name": "Bootstrap", "skill_category": "Frontend", "normalized_form": "bootstrap",
         "pattern": r"\bbootstrap\b"},
        {"skill_id": 29, "skill_name": "Sass / Less", "skill_category": "Frontend", "normalized_form": "sass",
         "pattern": r"\bsass\b|\bless\b|\bscss\b"},
        {"skill_id": 30, "skill_name": "Redux", "skill_category": "Frontend", "normalized_form": "redux",
         "pattern": r"\bredux\b"},
        {"skill_id": 31, "skill_name": "Webpack", "skill_category": "Frontend", "normalized_form": "webpack",
         "pattern": r"\bwebpack\b"},
        {"skill_id": 32, "skill_name": "Figma / UI Design", "skill_category": "UI/UX", "normalized_form": "figma",
         "pattern": r"\bfigma\b|\badobe xd\b|\bsketch\b"},

        # --- 3. Backend Frameworks & Tech ---
        {"skill_id": 33, "skill_name": "Node.js", "skill_category": "Backend", "normalized_form": "nodejs",
         "pattern": r"\bnode\.?js\b|\bnode\b"},
        {"skill_id": 34, "skill_name": "Express.js", "skill_category": "Backend", "normalized_form": "express",
         "pattern": r"\bexpress(?:js|\.js)?\b"},
        {"skill_id": 35, "skill_name": "NestJS", "skill_category": "Backend", "normalized_form": "nestjs",
         "pattern": r"\bnest(?:js|\.js)?\b"},
        {"skill_id": 36, "skill_name": "Spring Boot", "skill_category": "Backend", "normalized_form": "spring boot",
         "pattern": r"\bspring\b|\bspring\s*boot\b"},
        {"skill_id": 37, "skill_name": "Django", "skill_category": "Backend", "normalized_form": "django",
         "pattern": r"\bdjango\b"},
        {"skill_id": 38, "skill_name": "Flask", "skill_category": "Backend", "normalized_form": "flask",
         "pattern": r"\bflask\b"},
        {"skill_id": 39, "skill_name": "FastAPI", "skill_category": "Backend", "normalized_form": "fastapi",
         "pattern": r"\bfastapi\b"},
        {"skill_id": 40, "skill_name": "ASP.NET", "skill_category": "Backend", "normalized_form": "asp.net",
         "pattern": r"\basp\.net\b|\b\.net\s*core\b|\bwinforms\b"},
        {"skill_id": 41, "skill_name": "Laravel", "skill_category": "Backend", "normalized_form": "laravel",
         "pattern": r"\blaravel\b"},
        {"skill_id": 42, "skill_name": "Ruby on Rails", "skill_category": "Backend", "normalized_form": "ruby on rails",
         "pattern": r"\bruby on rails\b|\brails\b"},
        {"skill_id": 43, "skill_name": "GraphQL", "skill_category": "Backend", "normalized_form": "graphql",
         "pattern": r"\bgraphql\b"},
        {"skill_id": 44, "skill_name": "gRPC", "skill_category": "Backend", "normalized_form": "grpc",
         "pattern": r"\bgrpc\b"},

        # --- 4. Mobile Development ---
        {"skill_id": 45, "skill_name": "React Native", "skill_category": "Mobile", "normalized_form": "react native",
         "pattern": r"\breact\s*native\b"},
        {"skill_id": 46, "skill_name": "Flutter", "skill_category": "Mobile", "normalized_form": "flutter",
         "pattern": r"\bflutter\b"},
        {"skill_id": 47, "skill_name": "Android Native", "skill_category": "Mobile", "normalized_form": "android",
         "pattern": r"\bandroid\b|\bandroid sdk\b"},
        {"skill_id": 48, "skill_name": "iOS Native", "skill_category": "Mobile", "normalized_form": "ios",
         "pattern": r"\bios\b|\bios sdk\b"},
        {"skill_id": 49, "skill_name": "Xamarin", "skill_category": "Mobile", "normalized_form": "xamarin",
         "pattern": r"\bxamarin\b"},
        {"skill_id": 50, "skill_name": "Ionic", "skill_category": "Mobile", "normalized_form": "ionic",
         "pattern": r"\bionic\b"},

        # --- 5. Databases & NoSQL ---
        {"skill_id": 51, "skill_name": "MySQL", "skill_category": "Database", "normalized_form": "mysql",
         "pattern": r"\bmysql\b"},
        {"skill_id": 52, "skill_name": "PostgreSQL", "skill_category": "Database", "normalized_form": "postgresql",
         "pattern": r"\bpostgres(?:ql)?\b"},
        {"skill_id": 53, "skill_name": "Oracle", "skill_category": "Database", "normalized_form": "oracle",
         "pattern": r"\boracle\b"},
        {"skill_id": 54, "skill_name": "SQL Server", "skill_category": "Database", "normalized_form": "sql server",
         "pattern": r"\bsql\s*server\b|\bmssql\b"},
        {"skill_id": 55, "skill_name": "MongoDB", "skill_category": "Database", "normalized_form": "mongodb",
         "pattern": r"\bmongo(?:db)?\b"},
        {"skill_id": 56, "skill_name": "Redis", "skill_category": "Database", "normalized_form": "redis",
         "pattern": r"\bredis\b"},
        {"skill_id": 57, "skill_name": "Cassandra", "skill_category": "Database", "normalized_form": "cassandra",
         "pattern": r"\bcassandra\b"},
        {"skill_id": 58, "skill_name": "Elasticsearch", "skill_category": "Database",
         "normalized_form": "elasticsearch", "pattern": r"\belasticsearch\b|\bes\b|\belk\b"},
        {"skill_id": 59, "skill_name": "DynamoDB", "skill_category": "Database", "normalized_form": "dynamodb",
         "pattern": r"\bdynamodb\b"},
        {"skill_id": 60, "skill_name": "MariaDB", "skill_category": "Database", "normalized_form": "mariadb",
         "pattern": r"\bmariadb\b"},
        {"skill_id": 61, "skill_name": "Firebase", "skill_category": "Database", "normalized_form": "firebase",
         "pattern": r"\bfirebase\b"},
        {"skill_id": 62, "skill_name": "Neo4j", "skill_category": "Database", "normalized_form": "neo4j",
         "pattern": r"\bneo4j\b"},

        # --- 6. Cloud & DevOps & CI/CD ---
        {"skill_id": 63, "skill_name": "AWS", "skill_category": "Cloud/DevOps", "normalized_form": "aws",
         "pattern": r"\baws\b|\bamazon\s*web\s*services\b"},
        {"skill_id": 64, "skill_name": "Azure", "skill_category": "Cloud/DevOps", "normalized_form": "azure",
         "pattern": r"\bazure\b"},
        {"skill_id": 65, "skill_name": "Google Cloud", "skill_category": "Cloud/DevOps", "normalized_form": "gcp",
         "pattern": r"\bgcp\b|\bgoogle\s*cloud\b"},
        {"skill_id": 66, "skill_name": "Docker", "skill_category": "Cloud/DevOps", "normalized_form": "docker",
         "pattern": r"\bdocker\b"},
        {"skill_id": 67, "skill_name": "Kubernetes", "skill_category": "Cloud/DevOps", "normalized_form": "kubernetes",
         "pattern": r"\bkubernetes\b|\bk8s\b"},
        {"skill_id": 68, "skill_name": "Jenkins", "skill_category": "Cloud/DevOps", "normalized_form": "jenkins",
         "pattern": r"\bjenkins\b"},
        {"skill_id": 69, "skill_name": "Git", "skill_category": "Cloud/DevOps", "normalized_form": "git",
         "pattern": r"\bgit\b|\bgithub\b|\bgitlab\b"},
        {"skill_id": 70, "skill_name": "CI/CD", "skill_category": "Cloud/DevOps", "normalized_form": "ci/cd",
         "pattern": r"\bci/cd\b|\bci\\cd\b|\bgitlab ci\b|\bgithub actions\b"},
        {"skill_id": 71, "skill_name": "Linux", "skill_category": "Cloud/DevOps", "normalized_form": "linux",
         "pattern": r"\blinux\b|\bubuntu\b|\bcentos\b|\bunix\b"},
        {"skill_id": 72, "skill_name": "Terraform", "skill_category": "Cloud/DevOps", "normalized_form": "terraform",
         "pattern": r"\bterraform\b"},
        {"skill_id": 73, "skill_name": "Ansible", "skill_category": "Cloud/DevOps", "normalized_form": "ansible",
         "pattern": r"\bansible\b"},
        {"skill_id": 74, "skill_name": "Prometheus / Grafana", "skill_category": "Cloud/DevOps",
         "normalized_form": "monitoring", "pattern": r"\bprometheus\b|\bgrafana\b|\bdatadog\b"},
        {"skill_id": 75, "skill_name": "Nginx / Apache", "skill_category": "Cloud/DevOps",
         "normalized_form": "web server", "pattern": r"\bnginx\b|\bapache\b"},

        # --- 7. Data Engineering & Big Data ---
        {"skill_id": 76, "skill_name": "Hadoop", "skill_category": "Data Engineering", "normalized_form": "hadoop",
         "pattern": r"\bhadoop\b"},
        {"skill_id": 77, "skill_name": "Spark", "skill_category": "Data Engineering", "normalized_form": "spark",
         "pattern": r"\bspark\b|\bpyspark\b"},
        {"skill_id": 78, "skill_name": "Kafka", "skill_category": "Data Engineering", "normalized_form": "kafka",
         "pattern": r"\bkafka\b"},
        {"skill_id": 79, "skill_name": "Airflow", "skill_category": "Data Engineering", "normalized_form": "airflow",
         "pattern": r"\bairflow\b"},
        {"skill_id": 80, "skill_name": "Hive", "skill_category": "Data Engineering", "normalized_form": "hive",
         "pattern": r"\bhive\b"},
        {"skill_id": 81, "skill_name": "Data Warehouse", "skill_category": "Data Engineering", "normalized_form": "dwh",
         "pattern": r"\bdwh\b|\bdata\s*warehouse\b"},
        {"skill_id": 82, "skill_name": "ETL", "skill_category": "Data Engineering", "normalized_form": "etl",
         "pattern": r"\betl\b|\belt\b"},
        {"skill_id": 83, "skill_name": "Snowflake", "skill_category": "Data Engineering",
         "normalized_form": "snowflake", "pattern": r"\bsnowflake\b"},
        {"skill_id": 84, "skill_name": "BigQuery", "skill_category": "Data Engineering", "normalized_form": "bigquery",
         "pattern": r"\bbigquery\b"},
        {"skill_id": 85, "skill_name": "Databricks", "skill_category": "Data Engineering",
         "normalized_form": "databricks", "pattern": r"\bdatabricks\b"},
        {"skill_id": 86, "skill_name": "Talend / Pentaho", "skill_category": "Data Engineering",
         "normalized_form": "data tools", "pattern": r"\btalend\b|\bpentaho\b"},

        # --- 8. AI / Machine Learning / Data Science ---
        {"skill_id": 87, "skill_name": "Machine Learning", "skill_category": "AI/Data Science",
         "normalized_form": "machine learning", "pattern": r"\bmachine\s*learning\b|\bml\b"},
        {"skill_id": 88, "skill_name": "AI", "skill_category": "AI/Data Science", "normalized_form": "ai",
         "pattern": r"\bai\b|\bartificial\s*intelligence\b"},
        {"skill_id": 89, "skill_name": "NLP", "skill_category": "AI/Data Science", "normalized_form": "nlp",
         "pattern": r"\bnlp\b|\bnatural\s*language\s*processing\b"},
        {"skill_id": 90, "skill_name": "Deep Learning", "skill_category": "AI/Data Science",
         "normalized_form": "deep learning", "pattern": r"\bdeep\s*learning\b|\bdl\b"},
        {"skill_id": 91, "skill_name": "Computer Vision", "skill_category": "AI/Data Science",
         "normalized_form": "computer vision", "pattern": r"\bcomputer\s*vision\b|\bcv\b|\bopencv\b"},
        {"skill_id": 92, "skill_name": "TensorFlow", "skill_category": "AI/Data Science",
         "normalized_form": "tensorflow", "pattern": r"\btensorflow\b|\btf\b"},
        {"skill_id": 93, "skill_name": "PyTorch", "skill_category": "AI/Data Science", "normalized_form": "pytorch",
         "pattern": r"\bpytorch\b"},
        {"skill_id": 94, "skill_name": "Scikit-Learn", "skill_category": "AI/Data Science",
         "normalized_form": "scikit-learn", "pattern": r"\bscikit-learn\b|\bsklearn\b"},
        {"skill_id": 95, "skill_name": "Keras", "skill_category": "AI/Data Science", "normalized_form": "keras",
         "pattern": r"\bkeras\b"},
        {"skill_id": 96, "skill_name": "Pandas / NumPy", "skill_category": "AI/Data Science",
         "normalized_form": "data wrangling", "pattern": r"\bpandas\b|\bnumpy\b"},
        {"skill_id": 97, "skill_name": "LLM / Generative AI", "skill_category": "AI/Data Science",
         "normalized_form": "llm",
         "pattern": r"\bllm\b|\bgenerative\s*ai\b|\bopenai\b|\blangchain\b|\bhugging\s*face\b"},
        {"skill_id": 98, "skill_name": "Power BI", "skill_category": "AI/Data Science", "normalized_form": "power bi",
         "pattern": r"\bpower\s*bi\b"},
        {"skill_id": 99, "skill_name": "Tableau", "skill_category": "AI/Data Science", "normalized_form": "tableau",
         "pattern": r"\btableau\b"},
        {"skill_id": 100, "skill_name": "MLOps", "skill_category": "AI/Data Science", "normalized_form": "mlops",
         "pattern": r"\bmlops\b|\bmlflow\b"},

        # --- 9. QA / Testing ---
        {"skill_id": 101, "skill_name": "Automation Testing", "skill_category": "QA/Testing",
         "normalized_form": "automation test", "pattern": r"\bautomation\s*test\b|\bautomation\b"},
        {"skill_id": 102, "skill_name": "Manual Testing", "skill_category": "QA/Testing",
         "normalized_form": "manual test", "pattern": r"\bmanual\s*test\b|\bkiểm thử thủ công\b"},
        {"skill_id": 103, "skill_name": "Selenium", "skill_category": "QA/Testing", "normalized_form": "selenium",
         "pattern": r"\bselenium\b"},
        {"skill_id": 104, "skill_name": "Cypress", "skill_category": "QA/Testing", "normalized_form": "cypress",
         "pattern": r"\bcypress\b"},
        {"skill_id": 105, "skill_name": "Appium", "skill_category": "QA/Testing", "normalized_form": "appium",
         "pattern": r"\bappium\b"},
        {"skill_id": 106, "skill_name": "JUnit / TestNG", "skill_category": "QA/Testing",
         "normalized_form": "java testing", "pattern": r"\bjunit\b|\btestng\b"},
        {"skill_id": 107, "skill_name": "Jest / Mocha", "skill_category": "QA/Testing", "normalized_form": "js testing",
         "pattern": r"\bjest\b|\bmocha\b|\bchai\b"},
        {"skill_id": 108, "skill_name": "Postman / API Testing", "skill_category": "QA/Testing",
         "normalized_form": "api testing", "pattern": r"\bpostman\b|\bapi\s*testing\b|\bswagger\b"},

        # --- 10. Cyber Security & Networking ---
        {"skill_id": 109, "skill_name": "Cyber Security", "skill_category": "Security/Network",
         "normalized_form": "security", "pattern": r"\bcyber\s*security\b|\ban toàn thông tin\b|\bbảo mật\b"},
        {"skill_id": 110, "skill_name": "Penetration Testing", "skill_category": "Security/Network",
         "normalized_form": "pentest", "pattern": r"\bpenetration\s*testing\b|\bpentest\b"},
        {"skill_id": 111, "skill_name": "OWASP", "skill_category": "Security/Network", "normalized_form": "owasp",
         "pattern": r"\bowasp\b"},
        {"skill_id": 112, "skill_name": "Firewall / VPN", "skill_category": "Security/Network",
         "normalized_form": "network security", "pattern": r"\bfirewalls?\b|\bvpn\b"},
        {"skill_id": 113, "skill_name": "TCP/IP & DNS", "skill_category": "Security/Network",
         "normalized_form": "networking", "pattern": r"\btcp/ip\b|\bdns\b|\bwireshark\b"},
        {"skill_id": 114, "skill_name": "SIEM", "skill_category": "Security/Network", "normalized_form": "siem",
         "pattern": r"\bsiem\b"},

        # --- 11. Game Dev & Blockchain ---
        {"skill_id": 115, "skill_name": "Unity", "skill_category": "Game Dev", "normalized_form": "unity",
         "pattern": r"\bunity\b|\bunity3d\b"},
        {"skill_id": 116, "skill_name": "Unreal Engine", "skill_category": "Game Dev",
         "normalized_form": "unreal engine", "pattern": r"\bunreal\s*engine\b|\bue4\b|\bue5\b"},
        {"skill_id": 117, "skill_name": "Solidity", "skill_category": "Blockchain", "normalized_form": "solidity",
         "pattern": r"\bsolidity\b"},
        {"skill_id": 118, "skill_name": "Smart Contracts", "skill_category": "Blockchain",
         "normalized_form": "smart contract", "pattern": r"\bsmart\s*contracts?\b"},
        {"skill_id": 119, "skill_name": "Web3 / Ethereum", "skill_category": "Blockchain", "normalized_form": "web3",
         "pattern": r"\bweb3(?:\.js)?\b|\bethereum\b"},

        # --- 12. Architecture / Concepts / Methodologies ---
        {"skill_id": 120, "skill_name": "Agile", "skill_category": "Methodology", "normalized_form": "agile",
         "pattern": r"\bagile\b"},
        {"skill_id": 121, "skill_name": "Scrum", "skill_category": "Methodology", "normalized_form": "scrum",
         "pattern": r"\bscrum\b"},
        {"skill_id": 122, "skill_name": "REST API", "skill_category": "Concept", "normalized_form": "rest api",
         "pattern": r"\brest(?:ful)?\s*api\b|\bapi\b"},
        {"skill_id": 123, "skill_name": "Microservices", "skill_category": "Concept",
         "normalized_form": "microservices", "pattern": r"\bmicroservices\b"},
        {"skill_id": 124, "skill_name": "OOP", "skill_category": "Concept", "normalized_form": "oop",
         "pattern": r"\boop\b|\bobject\s*oriented\s*programming\b"},
        {"skill_id": 125, "skill_name": "Design Patterns", "skill_category": "Concept",
         "normalized_form": "design patterns", "pattern": r"\bdesign\s*patterns?\b"},
        {"skill_id": 126, "skill_name": "SOLID Principles", "skill_category": "Concept", "normalized_form": "solid",
         "pattern": r"\bsolid\b"},
        {"skill_id": 127, "skill_name": "MVC / MVVM", "skill_category": "Concept", "normalized_form": "mvc",
         "pattern": r"\bmvc\b|\bmvvm\b|\bmvp\b"},
        {"skill_id": 128, "skill_name": "TDD / BDD", "skill_category": "Concept", "normalized_form": "tdd",
         "pattern": r"\btdd\b|\bbdd\b"},
        {"skill_id": 129, "skill_name": "System Design", "skill_category": "Concept",
         "normalized_form": "system design", "pattern": r"\bsystem\s*design\b"},
        {"skill_id": 130, "skill_name": "T-SQL", "skill_category": "Concept", "normalized_form": "t-sql",
         "pattern": r"\bt-sql\b|\btransact-sql\b"},
        {"skill_id": 131, "skill_name": "LINQ / Entity Framework", "skill_category": "Framework/Library",
         "normalized_form": "ef", "pattern": r"\blinq\b|\bentity\s*framework\b|\bef\b"}
    ]

    # Thiết lập đường dẫn tương đối dựa trên vị trí của file hiện tại
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(base_dir, "data", "processed")

    # Tạo thư mục con nếu chưa tồn tại
    os.makedirs(processed_dir, exist_ok=True)

    # 1. Xuất Từ Điển Kỹ Năng (Skills_Dict.csv)
    skills_export_df = pd.DataFrame(skills_data)[['skill_id', 'skill_name', 'skill_category', 'normalized_form']]
    dict_output_path = os.path.join(processed_dir, 'Skills_Dict.csv')
    skills_export_df.to_csv(dict_output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Đã xuất từ điển mở rộng sang: {dict_output_path}")

    # -----------------------------------------------------------------
    # 2. THUẬT TOÁN QUÉT VÀ TRÍCH XUẤT (Job_Skill)
    # -----------------------------------------------------------------
    # [QUAN TRỌNG] Đổi tên file input theo đúng yêu cầu của người dùng
    input_file = os.path.join(processed_dir, "clean_all_jobs.csv")
    print(f"--- ĐANG ĐỌC FILE DỮ LIỆU ĐÃ CHUẨN HÓA: {input_file} ---")

    if not os.path.exists(input_file):
        print(f"❌ Thất bại: Không tìm thấy file {input_file}. Hãy kiểm tra lại tiến trình tiền xử lý!")
        return

    df = pd.read_csv(input_file)
    df = df.fillna('')  # Thay thế NaN bằng chuỗi trống

    job_skills = []

    print("--- ĐANG QUÉT KỸ NĂNG BẰNG NLP (REGEX) ---")
    for index, row in df.iterrows():
        job_id = row['job_id']

        # Thu thập toàn bộ ngữ cảnh văn bản liên quan đến kỹ năng
        req_text = str(row.get('req', '')).lower()
        desc_text = str(row.get('desc', '')).lower()
        title_text = str(row.get('title', '')).lower()
        full_text = f"{title_text} {req_text} {desc_text}"

        extracted_skills = set()

        for skill in skills_data:
            if re.search(skill['pattern'], full_text):
                extracted_skills.add(skill['skill_id'])

        for skill_id in extracted_skills:
            job_skills.append({"job_id": job_id, "skill_id": skill_id})

    # 2. Xuất bảng quan hệ Job_Skill.csv
    job_skill_df = pd.DataFrame(job_skills)
    job_skill_output_path = os.path.join(processed_dir, 'Job_Skill.csv')
    job_skill_df.to_csv(job_skill_output_path, index=False, encoding='utf-8-sig')

    print(f"✅ Hoàn tất! Đã ánh xạ {len(job_skills)} liên kết kỹ năng cho {len(df)} công việc.")
    print(f"📁 Lưu tại: {job_skill_output_path}")


if __name__ == "__main__":
    extract_skills_pipeline()