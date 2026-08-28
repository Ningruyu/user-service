// ============================================
// Jenkins 声明式 Pipeline - 用户管理服务
//
// 演示完整的 CI/CD 流程：
// 代码检出 -> 依赖安装 -> 代码检查 -> 单元测试 -> 集成测试
//          -> 覆盖率报告 -> Docker 构建 -> 镜像推送 -> 部署测试环境
//
// 所需 Jenkins 插件：
//   - Pipeline (workflow-aggregator)
//   - JUnit Plugin (junit)
//   - Cobertura Plugin (cobertura)
//   - Docker Pipeline (docker-workflow)
//   - Warnings Next Generation (可选，用于 flake8 报告)
// ============================================

pipeline {
    // 使用带有 Docker 的 agent，便于构建镜像
    agent any

    // 定义全局环境变量
    // DATABASE_URL: 指向测试用的内存 SQLite 数据库
    // TESTING: 开启测试模式（跳过生产建表逻辑）
    // IMAGE_NAME: Docker 镜像名称（占位符，替换为你的 Docker Hub 用户名）
    environment {
        DATABASE_URL      = 'sqlite:///:memory:'
        TESTING           = 'true'
        PYTHON_VERSION    = 'python3'
        IMAGE_NAME        = 'user-service'
        IMAGE_TAG         = "${env.BUILD_NUMBER}"
        // Docker Hub 凭证 ID（在 Jenkins 全局凭证中配置）
        // 类型：Username with password，ID 为 docker-hub-credentials
        DOCKER_HUB_CREDS  = 'docker-hub-credentials'
    }

    // 构建选项：超时和重试配置
    options {
        timestamps()                    // 日志添加时间戳
        timeout(time: 30, unit: 'MINUTES')  // 整体超时 30 分钟
        buildDiscarder(logRotator(numToKeepStr: '20'))  // 保留最近 20 次构建
        disableConcurrentBuilds()       // 禁止并发构建（避免资源竞争）
    }


    stages {

        // ============================================
        // 阶段 1：检出代码
        // Jenkins 默认会检出 SCM，此阶段用于显式说明
        // ============================================
        stage('Checkout') {
            steps {
                checkout scm
                echo "代码已检出，当前分支：${env.BRANCH_NAME ?: 'detached'}"
                echo "构建编号：${env.BUILD_NUMBER}"
                echo "工作目录：${env.WORKSPACE}"
            }
        }

        // ============================================
        // 阶段 2：环境搭建
        // 创建虚拟环境并安装依赖（包含开发依赖）
        // ============================================
        stage('Setup') {
            steps {
                sh '''
                    # 检查 Python 版本
                    ${PYTHON_VERSION} --version

                    # 创建虚拟环境（不使用系统包，保证隔离）
                    ${PYTHON_VERSION} -m venv .venv

                    # 激活并升级 pip
                    . .venv/bin/activate
                    pip install --upgrade pip

                    # 安装开发依赖（含 requirements.txt 和测试工具）
                    pip install -r requirements-dev.txt

                    # 验证关键依赖已安装
                    python -c "import fastapi; print(fastapi.__version__)"
                    python -c "import pytest; print(pytest.__version__)"
                '''
            }
        }

        // ============================================
        // 阶段 3：代码质量检查
        // 使用 flake8 检查代码风格
        // ============================================
        stage('Code Quality') {
            steps {
                sh '''
                    . .venv/bin/activate
                    # 运行 flake8，输出格式为 pylint 兼容
                    # --exit-zero: 即使有警告也不让阶段失败（演示用）
                    # 生产环境可移除 --exit-zero 让检查失败中断流水线
                    flake8 app tests --exit-zero --output-file=flake8-report.txt || true
                    echo "flake8 检查完成，报告见 flake8-report.txt"
                    cat flake8-report.txt
                '''
            }
            post {
                always {
                    // 归档报告，便于在 Jenkins UI 查看
                    archiveArtifacts artifacts: 'flake8-report.txt', allowEmptyArchive: true
                }
            }
        }

        // ============================================
        // 阶段 4：单元测试
        // 只运行 tests/test_unit.py，测试 CRUD 逻辑
        // ============================================
        stage('Unit Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    # 仅运行单元测试，输出 JUnit XML 报告
                    # --cov 生成覆盖率报告（覆盖 app 包）
                    pytest tests/test_unit.py \
                        -v \
                        --junitxml=unit-results.xml \
                        --cov=app \
                        --cov-report=xml:unit-coverage.xml \
                        --cov-report=term
                '''
            }
            post {
                always {
                    // 发布 JUnit 测试报告（Jenkins UI 会显示测试趋势）
                    junit 'unit-results.xml'
                }
            }
        }

        // ============================================
        // 阶段 5：集成测试
        // 运行 tests/test_api.py，通过 HTTP 客户端测试 API
        // ============================================
        stage('Integration Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    # 运行集成测试
                    pytest tests/test_api.py \
                        -v \
                        --junitxml=integration-results.xml \
                        --cov=app \
                        --cov-report=xml:integration-coverage.xml \
                        --cov-report=term
                '''
            }
            post {
                always {
                    junit 'integration-results.xml'
                }
            }
        }

        // ============================================
        // 阶段 6：覆盖率报告
        // 合并所有测试的覆盖率并展示
        // 使用 Cobertura 插件渲染报告
        // ============================================
        stage('Coverage') {
            steps {
                sh '''
                    . .venv/bin/activate
                    # 运行全部测试生成总体覆盖率报告
                    pytest tests/ \
                        --cov=app \
                        --cov-report=xml:coverage.xml \
                        --cov-report=term-missing \
                        --junitxml=results.xml \
                        --cov-report=html:htmlcov
                '''
            }
            post {
                always {
                    // 发布 Cobertura 覆盖率报告
                    // 需在 Jenkins 安装 Cobertura 插件
                    recordCoverage(tools: [[parser: 'COBERTURA', pattern: 'coverage.xml']])

                    // 归档 HTML 覆盖率报告
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])

                    junit 'results.xml'
                }
            }
        }

        // ============================================
        // 阶段 7：构建 Docker 镜像
        // 仅在 main 分支上执行（演示分支策略）
        // 镜像标签使用构建号
        // ============================================
        stage('Build Docker Image') {
            when {
                // 仅在主干分支（main 或 master）执行
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                sh '''
                    echo "开始构建 Docker 镜像：${IMAGE_NAME}:${IMAGE_TAG}"
                    # 使用多阶段 Dockerfile 构建镜像
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker build -t ${IMAGE_NAME}:latest .

                    # 列出镜像确认
                    docker images ${IMAGE_NAME}
                '''
            }
        }

        // ============================================
        // 阶段 8：推送 Docker 镜像
        // 推送到 Docker Hub，需配置凭证
        // ============================================
        stage('Push Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                script {
                    try {
                        withCredentials([usernamePassword(
                            credentialsId: "${DOCKER_HUB_CREDS}",
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            sh '''
                                echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                                docker push ${IMAGE_NAME}:${IMAGE_TAG}
                                docker push ${IMAGE_NAME}:latest
                                docker logout
                            '''
                        }
                    } catch (e) {
                        echo '未配置 docker-hub-credentials 凭证，跳过推送（以后想练：Manage Jenkins → Credentials → 添加后重跑即可）'
                    }
                }
            }
        }

        // ============================================
        // 阶段 9：部署到测试环境
        // 使用 Docker 运行容器，模拟部署
        // 端口映射 8000:8000
        // ============================================
        stage('Deploy to Test') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                sh '''
                    echo "部署到测试环境..."

                    # 清理可能存在的旧容器
                    docker rm -f user-service-test 2>/dev/null || true

                    # 运行新容器
                    # -d: 后台运行
                    # --name: 容器名称
                    # -p 8000:8000: 端口映射（主机:容器）
                    # -e: 环境变量
                    docker run -d \
                        --name user-service-test \
                        -p 8000:8000 \
                        -e DATABASE_URL=sqlite:///./user_service.db \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    # 等待应用启动（最多 30 秒）
                    echo "等待应用启动..."
                    for i in $(seq 1 30); do
                        if curl -s http://localhost:8000/health | grep -q "healthy"; then
                            echo "应用已启动！"
                            curl -s http://localhost:8000/ | python3 -m json.tool
                            break
                        fi
                        sleep 1
                        echo "等待中... (${i}/30)"
                    done

                    # 健康检查
                    if ! curl -s http://localhost:8000/health | grep -q "healthy"; then
                        echo "错误：应用未能在 30 秒内启动"
                        docker logs user-service-test
                        exit 1
                    fi

                    echo "部署成功！访问 http://localhost:8000/docs 查看 API 文档"
                '''
            }
        }
    }

    // ============================================
    // Post 阶段：无论成功失败都执行
    // ============================================
    post {
        always {
            echo "Pipeline 执行结束，开始归档报告..."

            // 归档测试报告
            archiveArtifacts artifacts: '**/*results.xml, **/*coverage.xml, flake8-report.txt',
                             allowEmptyArchive: true

            // 发布 JUnit 报告（兜底，确保所有报告都被收集）
            junit allowEmptyResults: true, testResults: '**/*results.xml'
        }
        success {
            echo '✅ Pipeline 执行成功！'
        }
        unstable {
            echo '⚠️ Pipeline 执行不稳定（测试有失败）'
        }
        failure {
            echo '❌ Pipeline 执行失败'
            // 可在此发送通知（邮件、Slack 等）
            // emailext subject: '构建失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}',
            //          body: '请查看: ${env.BUILD_URL}',
            //          to: 'dev-team@example.com'
        }
        changed {
            echo 'Pipeline 状态发生变化'
        }
        // 清理工作空间（可选，根据需要开启）
        // cleanup {
        //     cleanWs()
        // }
    }
}
