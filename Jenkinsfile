pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'nguyenduyanh221204/vdt-backend'
        CONFIG_REPO_URL = 'github.com/duyanh221204/vdt-backend-config.git'
        GITHUB_CREDENTIALS_ID = 'github-credentials'
        DOCKER_HUB_CREDENTIALS_ID = 'docker-hub-credentials'

        // Đường dẫn gọi lệnh docker đã cấu hình
        DOCKER_PATH = '/var/jenkins_home/docker'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                // Tự động tải source code tại thời điểm có thay đổi hoặc tag mới
                checkout scm
            }
        }

        stage('Check Git Tag') {
            steps {
                script {
                    echo "Kiểm tra tag hiện tại: ${env.GIT_BRANCH}"
                    
                    // Nếu chuỗi lưu tên nhánh không chứa từ khóa 'tags/'
                    if (!env.GIT_BRANCH.contains('tags/')) {
                        // Lệnh error() của Jenkins sẽ lập tức in ra log và đánh dấu Pipeline là FAILURE, dừng mọi xử lý phía sau
                        error("Không phải tag hợp lệ")
                    }
                    
                    echo "Tag hợp lệ: ${env.GIT_BRANCH}"
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Lấy tag của Git làm tag cho Docker Image
                    // Biến env.GIT_BRANCH của Jenkins có định dạng 'refs/tags/v1.0.0'
                    // Hàm split('/')[-1] dùng để cắt chuỗi, chỉ lấy phần chữ 'v1.0.0'
                    def imageTag = env.GIT_BRANCH.split('/')[-1]

                    // Gọi phương thức withCredentials để lấy credentials từ Jenkins một cách an toàn
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CREDENTIALS_ID}", passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh """
                        echo "Đăng nhập hệ thống Docker Hub"
                        echo "\$DOCKER_PASSWORD" | ${DOCKER_PATH} login -u "\$DOCKER_USERNAME" --password-stdin

                        echo "Tiến hành build Image với tag: ${imageTag}"
                        ${DOCKER_PATH} build -t ${DOCKER_IMAGE}:${imageTag} .

                        echo "Tiến hành đẩy Image lên Docker Hub"
                        ${DOCKER_PATH} push ${DOCKER_IMAGE}:${imageTag}
                        """
                    }
                }
            }
        }

        stage('Update Config Repo') {
            steps {
                script {
                    def imageTag = env.GIT_BRANCH.split('/')[-1]
                    
                    withCredentials([usernamePassword(credentialsId: "${GITHUB_CREDENTIALS_ID}", passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                        sh """
                        echo "Tải config repo từ GitHub"
                        rm -rf config-repo
                        git clone https://\${GIT_USERNAME}:\${GIT_PASSWORD}@${CONFIG_REPO_URL} config-repo
                        cd config-repo

                        echo "Cấu hình thông tin user Git"
                        git config user.email "devops@vdt2026.com"
                        git config user.name "Jenkins CI"

                        echo "Chỉnh sửa version tag trong tệp values.yaml"
                        # Cú pháp sed -i dùng để sửa trực tiếp tệp
                        # 's/chuỗi_cũ/chuỗi_mới/g' sẽ tìm thuộc tính 'tag: ' và ghi đè tag mới vào sau nó
                        sed -i "s/tag: .*/tag: ${imageTag}/g" values.yaml

                        # Kiểm tra thay đổi
                        # Lệnh 'git diff --quiet' sẽ kiểm tra xem có dòng code nào bị thay đổi không
                        if git diff --quiet values.yaml; then
                            echo "Phiên bản tag '${imageTag}' đã tồn tại trong cấu hình hiện tại"
                            echo "Từ chối cập nhật"
                            # Dừng pipeline với trạng thái FAILURE
                            exit 1
                        else
                            echo "Phát hiện tag mới, commit và push thay đổi lên GitHub"
                            git add values.yaml
                            git commit -m "Update image tag to ${imageTag} via Jenkins Pipeline"
                            git push origin main
                        fi
                        """
                    }
                }
            }
        }
    }

    // Xử lý sau khi pipeline kết thúc
    post {
        success {
            // Ghi log xác nhận pipeline đã chạy thành công
            echo 'Pipeline thành công'
        }
        failure {
            // Log lỗi
            echo 'Pipeline thất bại. Cần kiểm tra log chi tiết ở các stage trên'
        }
    }
}