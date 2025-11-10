pipeline {
  agent any
  options { timestamps() }

  triggers {
    githubPush()
    pollSCM('H/2 * * * *')  // fallback polling
  }

  environment {
    APP_DIR = "/home/Monitoring"
    VENV = "/home/Monitoring/.venv"
    SERVICE = "monitoring.service"
    SCRIPT = "monitoring.py"
  }

  stages {

    /* -------------------------------------------
       🚀 CI START NOTIFICATION
    -------------------------------------------- */
    stage('Notify Build Start') {
      steps {
        sh '''
          . /home/Monitoring/.venv/bin/activate || true
          python3 - << 'EOF'
from dotenv import load_dotenv
import os, requests, socket, datetime

load_dotenv('/home/Monitoring/.env')
token = os.getenv("FONNTE_TOKEN")
targets = [t.strip() for t in os.getenv("FONNTE_TARGETS","").split(',') if t.strip()]

hostname = socket.gethostname()
ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
msg = f"🚀 *CI Deploy Started*\nServer: {hostname}\nTime: {ts}"

for t in targets:
    try:
        requests.post("https://api.fonnte.com/send",
            headers={"Authorization": token},
            data={"target": t, "message": msg})
    except Exception as e:
        print("Send failed:", e)
EOF
        '''
      }
    }

    /* -------------------------------------------
       ✅ CHECKOUT SOURCE
    -------------------------------------------- */
    stage('Checkout') {
      steps {
        checkout scm
        sh 'echo "[CHECKOUT] Listing files:" && ls -la'
      }
    }

    /* -------------------------------------------
       📦 SYNC FILE TO SERVER DIRECTORY
    -------------------------------------------- */
    stage('Deploy Script to Server') {
      steps {
        sh '''
          set -e
          echo "[DEPLOY] Updating $SCRIPT in $APP_DIR"
          install -m 644 $SCRIPT $APP_DIR/$SCRIPT
          echo "[DEPLOY] Done."
        '''
      }
    }

    /* -------------------------------------------
       🐍 ENSURE PYTHON ENV
    -------------------------------------------- */
    stage('Setup Python Environment') {
      steps {
        sh '''
          set -e
          if [ ! -x "$VENV/bin/python" ]; then
            echo "[VENV] Creating virtual environment..."
            python3 -m venv "$VENV"
          fi
          "$VENV/bin/pip" install --upgrade pip
          "$VENV/bin/pip" install requests google-generativeai python-dotenv
        '''
      }
    }

    /* -------------------------------------------
       🔁 RESTART SYSTEMD SERVICE
    -------------------------------------------- */
    stage('Restart Monitoring Service') {
      steps {
        sh '''
          set -e
          echo "[SYSTEMD] Restarting service $SERVICE"
          sudo systemctl daemon-reload
          sudo systemctl restart "$SERVICE"
          sleep 2
          sudo systemctl is-active "$SERVICE"
        '''
      }
    }

    /* -------------------------------------------
       📄 FETCH & ARCHIVE LOGS
    -------------------------------------------- */
    stage('Fetch Logs') {
      steps {
        sh '''
          echo "[LOG] Showing last 200 lines:"
          sudo journalctl -u "$SERVICE" -n 200 --no-pager || true
          sudo journalctl -u "$SERVICE" -n 500 --no-pager > jenkins_service_tail.txt || true
        '''
      }
    }
  }

  /* -------------------------------------------
     ✅ POST BUILD: SUCCESS / FAILURE NOTIF
  -------------------------------------------- */
  post {

    always {
      archiveArtifacts artifacts: 'jenkins_service_tail.txt', allowEmptyArchive: true
    }

    success {
      sh '''
        . /home/Monitoring/.venv/bin/activate
        python3 - << 'EOF'
from dotenv import load_dotenv
import os, requests, socket, datetime

load_dotenv('/home/Monitoring/.env')
token = os.getenv("FONNTE_TOKEN")
targets = [t.strip() for t in os.getenv("FONNTE_TARGETS","").split(',') if t.strip()]

hostname = socket.gethostname()
ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
msg = f"✅ *CI Deploy Success*\nServer: {hostname}\nTime: {ts}"

for t in targets:
    requests.post("https://api.fonnte.com/send",
        headers={"Authorization": token},
        data={"target": t, "message": msg})
EOF
      '''
    }

    failure {
      sh '''
        . /home/Monitoring/.venv/bin/activate
        python3 - << 'EOF'
from dotenv import load_dotenv
import os, requests, socket, datetime

load_dotenv('/home/Monitoring/.env')
token = os.getenv("FONNTE_TOKEN")
targets = [t.strip() for t in os.getenv("FONNTE_TARGETS","").split(',') if t.strip()]

hostname = socket.gethostname()
ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
msg = f"❌ *CI Deploy Failed*\nServer: {hostname}\nTime: {ts}"

for t in targets:
    requests.post("https://api.fonnte.com/send",
        headers={"Authorization": token},
        data={"target": t, "message": msg})
EOF
      '''
    }
  }
}
