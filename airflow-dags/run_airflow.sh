# (0) 환경 변수 세팅
export AIRFLOW_HOME=~/workspace/GSBE/project-root/airflow-dags

# (1) db 마이그레이션
# 이건 초기화 
airflow db reset 
airflow db migrate


# (2) 로컬 airflow 서버 실행
airflow standalone 


# (3) 접속은
http://localhost:8080

- 3.0.0 관련 질문 사항
https://stackoverflow.com/questions/79592889/airflow-users-create-command-not-working-with-3-0-version

- airflow release_notes
https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html#airflow-3-0-0-2025-04-22

- FAB 인증 방식을 활성화 하면 create가 가능 
pip install apache-airflow-providers-flask-appbuilder

# (4) 비번도 설정함 
(venv) jjlee@DESKTOP-T4DM29K:~/workspace/GSBE/project-root/airflow-dags$ cat passwords.json
{
  "admin": "admin",
  "jjlee": "$pbkdf2-sha256$29000$D8FYizFmjBFCKKXUeo9xLg$0dwhIctlvk9XXnpOy3rbb/x9Nr6FHSGFuDmoRO4DGNo"
}


# v airflow.cfg 
# The json file where the simple auth manager stores passwords for the configured users.
# By default this is ``AIRFLOW_HOME/simple_auth_manager_passwords.json.generated``.
#
# Example: simple_auth_manager_passwords_file = /path/to/passwords.json
#
# Variable: AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE
#
simple_auth_manager_passwords_file = ./passwords.json


# (5) cfg 수정
load_examples=False
(venv) jjlee@DESKTOP-T4DM29K:~/workspace/GSBE/project-root/airflow-dags$ cat airflow.cfg | grep dags_folder
dags_folder = /home/jjlee/workspace/GSBE/project-root/airflow-dags/dags


# (6) 확인 명령어 
airflow dags list
airflow dags show player_summary_update
