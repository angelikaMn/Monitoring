pipeline {
  agent any
  options { timestamps() }

  triggers {
    githubPush()
    pollSCM('H/2 * * * *')  // fallback polling
  }

  environment {
    VM_APP_DIR = "/home/Monitoring"
    VENV = "/home/Monitoring/.venv"
    SERVICE = "monitoring"
    SCRIPT = "monitoring.py"
    LOGFILE = "/var/log/monitoring.log"
  }

  stages {

    /* ----------------------------------------------------
       CI START WHATSAPP NOTIF
    ---------------------------------------------------- */
    stage('Notify Build Start') {
      steps {
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
msg = f"🚀 *CI Deploy Started*\nServer: {hostname}\nTime: {ts}"

for t in targets:
    requests.post("https://api.fonnte.com/send",
        headers={"Authorization": token},
        data={"target": t, "message": msg})
EOF
        '''
      }
    }

    /* ----------------------------------------------------
       CHECKOUT CODE
    ---------------------------------------------------- */
    stage('Checkout') {
      steps {
        checkout scm
        sh 'echo "[CHECKOUT] Files:" && ls -la'
      }
    }

    /* ----------------------------------------------------
       SYNC CODE TO SERVER DIR
    ---------------------------------------------------- */
    stage('Sync to Server App Directory') {
      steps {
        sh '''
          set -e
          echo "[SYNC] Updating script..."
          install -m 644 monitoring.py $VM_APP_DIR/monitoring.py
          echo "[SYNC] Done."
        '''
      }
    }

    /* ----------------------------------------------------
       ENSURE VENV + DEPENDENCIES
    ---------------------------------------------------- */
    stage('Ensure Python Environment') {
      steps {
        sh '''
          set -e
          if [ ! -x "$VENV/bin/python" ]; then
            echo "[VENV] Creating virtualenv..."
            python3 -m venv "$VENV"
          fi
          "$VENV/bin/pip" install --upgrade pip
          "$VENV/bin/pip" install requests google-generativeai python-dotenv
        '''
      }
    }

    /* ----------------------------------------------------
       RESTART SYSTEMD SERVICE
    ---------------------------------------------------- */
    stage('Restart Monitoring Service') {
      steps {
        sh '''
          set -e
          echo "[SYSTEMD] Restarting $SERVICE"
          sudo systemctl daemon-reload
          sudo systemctl restart "$SERVICE"
          sleep 2
          sudo systemctl is-active "$SERVICE"
        '''
      }
    }

    /* ----------------------------------------------------
       DISPLAY & ARCHIVE LOG SNAPSHOT
    ---------------------------------------------------- */
    stage('Fetch Logs') {
      steps {
        sh '''
          echo "[LOG] Recent logs:"
          sudo journalctl -u "$SERVICE" -n 200 --no-pager || true
          sudo journalctl -u "$SERVICE" -n 500 --no-pager > jenkins_service_tail.txt || true
        '''
      }
    }

    /* ----------------------------------------------------
       SUCCESS CI NOTIFICATION
    ---------------------------------------------------- */
    stage('Notify Success') {
      when { success() }
      steps {
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
    }
  }

  /* ----------------------------------------------------
     FAILURE NOTIFICATION + LOG ARCHIVE
  ---------------------------------------------------- */
  post {
    always {
      archiveArtifacts artifacts: 'jenkins_service_tail.txt', allowEmptyArchive: true
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
