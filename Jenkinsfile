def remote = [:]

pipeline {
    agent any

        environment {
            host = credentials('aclimate_v3_host')
        }

    stages {
        stage('Ssh to connect Melisa server') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'aclimate_v3_deploy', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        try {
                            remote.user = USER
                            remote.password = PASS
                            remote.host = host
                            remote.name = host
                            remote.allowAnyHosts = true

                            sshCommand remote: remote, command: "echo 'Connection successful!'"
                        } catch (Exception e) {
                            echo "SSH Connection Error: ${e.message}"
                            error("Failed to establish SSH connection: ${e.message}")
                        }
                    }
                }
            }
        }
        stage('Update API code') {
            steps {
                script {
                    try {
                        sshCommand remote: remote, command: """
                            # Stop at the first failing command so a broken update is not deployed
                            set -e
                            cd /var/www/aclimate/aclimate_v3_api/aclimate_v3_webapi
                            git checkout main
                            git pull origin main
                            source /opt/anaconda3/etc/profile.d/conda.sh
                            conda activate /home/scalderon/.conda/envs/aclimate_v3_api
                            # Make sure uv is available inside the conda environment
                            pip install --upgrade uv
                            # Export the production dependencies pinned in uv.lock (no dev group)
                            uv export --frozen --no-dev --no-hashes --no-emit-project -o /tmp/aclimate_v3_webapi_requirements.txt
                            # Install the locked dependencies into the active conda environment
                            uv pip install --python "\$CONDA_PREFIX" -r /tmp/aclimate_v3_webapi_requirements.txt
                        """
                    } catch (Exception e) {
                        echo "Git Pull Error: ${e.message}"
                        error("Failed to update code: ${e.message}")
                    }
                }
            }
        }
        stage('Restart API service') {
            steps {
                script {
                    try {
                        sshCommand remote: remote, command: """
                            cd /var/www/aclimate/aclimate_v3_api/aclimate_v3_webapi/src
                            source /opt/anaconda3/etc/profile.d/conda.sh
                            conda activate /home/scalderon/.conda/envs/aclimate_v3_api
                            fuser -k 3002/tcp || true
                            nohup uvicorn main:app --host 0.0.0.0 --port 3002 > /var/www/aclimate/aclimate_v3_api/aclimate_v3_webapi/api.log 2>&1 &
                        """
                    } catch (Exception e) {
                        echo "API Restart Error: ${e.message}"
                        error("Failed to restart API: ${e.message}")
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                echo "Pipeline failed"
            }
        }
        success {
            script {
                echo 'API deployed successfully!'
            }
        }
    }
}
