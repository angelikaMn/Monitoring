pipeline {
  agent any
  options { timestamps() }

  triggers {
    githubPush()
    pollSCM('H/2 * * * *')  // fallback
  }

  environment {
    APP_DIR = "/home/Monitoring"
    VENV = "/home/Monitoring/.venv"
    SERVICE = "monitoring"
    SCRIPT = "monitoring.py"
    LOGFILE = "/var/log/monitoring.log"
  }

  stages {
    stage('Checkout') {
      steps {
        echo "[CHECKOUT] Fetching repo..."
        checkout scm
        sh 'ls -la'
      }
    }

    stage('Sync to App Dir') {
      steps {
        sh '''
          set -e
          echo "[SYNC] Copying script to $APP_DIR"
          install -m 644 monitoring.py $APP_DIR/monitoring.py
          # keep your .env untouched on server
          ls -l $APP_DIR/monitoring.py
        '''
      }
    }

    stage('Deps (venv)') {
      steps {
        sh '''
          set -e
          if [ ! -x "$VENV/bin/python" ]; then
            echo "[VENV] creating..."
            python3 -m venv "$VENV"
          fi
          "$VENV/bin/pip" install --upgrade pip
          "$VENV/bin/pip" install requests google-generativeai python-dotenv
          echo "[VENV] Python: $("$VENV/bin/python" -V)"
        '''
      }
    }

    stage('Restart service') {
      steps {
        sh '''
          set -e
          echo "[SYSTEMD] daemon-reload"
          sudo systemctl daemon-reload
          echo "[SYSTEMD] restart $SERVICE"
          sudo systemctl restart "$SERVICE"
          sleep 2
          sudo systemctl is-active "$SERVICE"
          echo "[SYSTEMD] status:"
          sudo systemctl status "$SERVICE" --no-pager || true
        '''
      }
    }

    stage('Health & Logs snapshot') {
      steps {
        sh '''
          set -e
          echo "[HEALTH] journalctl tail"
          sudo journalctl -u "$SERVICE" -n 200 --no-pager || true
          echo "[HEALTH] logfile tail"
          sudo tail -n 200 "$LOGFILE" || true
        '''
      }
    }
  }

  post {
    always {
      echo "[POST] Archiving latest service log snapshot"
      sh 'sudo journalctl -u "$SERVICE" -n 500 --no-pager > jenkins_service_tail.txt || true'
      archiveArtifacts artifacts: 'jenkins_service_tail.txt', allowEmptyArchive: true
    }
  }
}
