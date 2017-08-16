pipeline {
  agent any
  stages {
    stage('Setup Environment') {
      steps {
        sh '''python3 -m venv env
. env/bin/activate
pip install -e .[full]'''
      }
    }
    stage('Test') {
      steps {
        sh 'py.test --junitxml results.xml test/'
      }
    }
    stage('xUnit') {
      steps {
        junit 'results.xml'
      }
    }
  }
}