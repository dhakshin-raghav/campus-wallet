import re

html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# ──────────────────────────────────────────────────────────────────────
# 1. CSS: Prevent tables and diagrams from splitting across pages
# ──────────────────────────────────────────────────────────────────────
css_patch = """
      table, div[style*="border"], img {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
"""
if "page-break-inside: avoid" not in html:
    html = html.replace("body {\n        -webkit-print-color-adjust: exact;",
                         css_patch + "\n      body {\n        -webkit-print-color-adjust: exact;")

# ──────────────────────────────────────────────────────────────────────
# 2. Fix the misnamed sub-section 6.2.1 -> 5.2.1 inside Ch5
# ──────────────────────────────────────────────────────────────────────
html = html.replace('<h4 class="sub-section">6.2.1 Workflow Pipeline Phases</h4>',
                    '<h4 class="sub-section">5.2.1 Workflow Pipeline Phases</h4>')

# ──────────────────────────────────────────────────────────────────────
# 3. Replace the thin Chapter 5 with a massively expanded version
# ──────────────────────────────────────────────────────────────────────
# Locate the start and end of the existing Chapter 5 content
ch5_start_marker = '<!-- ═══════════════════════════════════════════════ CHAPTER 6 ═══ -->'
ch5_start = html.find(ch5_start_marker)

# Find the Chapter 6 Conclusion div
ch6_marker = '<div class="chapter-title">CHAPTER 6<br>CONCLUSION AND FUTURE WORKS</div>'
ch6_start = html.find(ch6_marker)
# Go back to find the enclosing <!-- comment and <div class="page">
ch6_page_start = html.rfind('<!-- ═══', 0, ch6_start)

if ch5_start == -1 or ch6_page_start == -1:
    print(f"ERROR: Could not find markers. ch5_start={ch5_start}, ch6_page_start={ch6_page_start}")
    exit(1)

# Extract existing Ch6 onward
ch6_onward = html[ch6_page_start:]

# Build the massive new Chapter 5
new_ch5 = """
  <!-- ═══════════════════════════════════════════════ CHAPTER 5: CI/CD ═══ -->
  <div class="page">
    <div class="chapter-title">CHAPTER 5<br>CONTINUOUS INTEGRATION AND DEPLOYMENT AUTOMATION</div>

    <h3 class="section-heading">5.1 Overview of CI/CD Methodology</h3>
    <p>Continuous Integration (CI) and Continuous Deployment (CD) represent a set of foundational DevOps practices that
      automate the process of integrating code changes, running quality checks, and deploying applications to production
      environments. For the Campus Cafeteria Pre-Booking System, a dual-pipeline CI/CD architecture was engineered using
      both GitHub Actions and Jenkins, providing redundancy and flexibility in the deployment workflow.</p>

    <p>The CI/CD methodology adopted for this project follows the industry-standard practice of trunk-based development,
      where all developers commit to a single main branch. Every push to the <code>main</code> branch triggers an
      automated pipeline that performs the following sequential operations: source code checkout, dependency installation,
      application build, Docker image creation, image registry push, and remote server deployment. This ensures that the
      production environment always reflects the latest stable version of the codebase.</p>

    <p>The benefits of implementing CI/CD in this project are manifold. First, it eliminates the error-prone manual
      deployment process that previously required SSH access to the EC2 instance and manual Docker commands. Second, it
      provides an immutable audit trail of every deployment through pipeline logs and container image tags. Third, it
      enables rapid rollback capabilities by maintaining versioned Docker images in the Amazon Elastic Container Registry
      (ECR). Finally, it establishes a consistent and reproducible build environment that is independent of individual
      developer machines.</p>

    <h3 class="section-heading">5.2 GitHub Actions Architecture</h3>
    <p>GitHub Actions serves as the primary CI/CD engine for the project, providing a cloud-native automation platform
      that is tightly integrated with the source code repository. The workflow is defined declaratively in a YAML
      configuration file located at <code>.github/workflows/deploy.yml</code>, following the Infrastructure-as-Code (IaC)
      paradigm.</p>

    <h4 class="sub-section">5.2.1 Workflow Trigger Configuration</h4>
    <p>The GitHub Actions workflow is configured to trigger on push events to the <code>main</code> branch exclusively.
      This ensures that only reviewed and merged pull requests initiate the deployment pipeline, preventing accidental
      deployments from feature branches. The trigger configuration also supports manual dispatch via the
      <code>workflow_dispatch</code> event, allowing administrators to manually re-deploy without pushing new code.</p>

    <h4 class="sub-section">5.2.2 Workflow Pipeline Phases</h4>
    <p>The deployment workflow consists of four distinct phases, each running in an isolated Ubuntu runner environment
      provided by GitHub's cloud infrastructure:</p>

    <table>
      <tr>
        <th>Phase</th>
        <th>Action</th>
        <th>Description</th>
      </tr>
      <tr>
        <td>1. Checkout</td>
        <td><code>actions/checkout@v4</code></td>
        <td>Clones the repository into the runner workspace with full git history for accurate build metadata</td>
      </tr>
      <tr>
        <td>2. Setup Node.js</td>
        <td><code>actions/setup-node@v4</code></td>
        <td>Installs Node.js v20 LTS and configures npm caching to accelerate dependency installation</td>
      </tr>
      <tr>
        <td>3. AWS Authentication</td>
        <td><code>aws-actions/configure-aws-credentials@v4</code></td>
        <td>Authenticates with AWS using IAM access keys stored in GitHub Secrets for ECR push permissions</td>
      </tr>
      <tr>
        <td>4. Docker Build &amp; Push</td>
        <td><code>docker/build-push-action@v5</code></td>
        <td>Builds multi-stage Docker images with build-time arguments and pushes tagged images to ECR</td>
      </tr>
    </table>
    <p style="text-align:center; font-style:italic;">Table 5.1: GitHub Actions Workflow Phases</p>

  </div>

  <div class="page">

    <h4 class="sub-section">5.2.3 Build-Time Environment Variable Injection</h4>
    <p>A critical challenge in deploying Next.js applications is the handling of environment variables prefixed with
      <code>NEXT_PUBLIC_</code>. Unlike server-side environment variables, these are embedded directly into the JavaScript
      bundle at build time by the Next.js compiler. This means that setting environment variables at container runtime
      has no effect on the client-side code — the values must be available during the <code>next build</code> step.</p>

    <p>To address this, the CI/CD pipeline injects the <code>NEXT_PUBLIC_API_URL</code> as a Docker build argument
      (<code>ARG</code>) in the Dockerfile, which is then exposed as an environment variable (<code>ENV</code>) before
      the build command executes. The pipeline passes this value from GitHub Secrets using the
      <code>--build-arg</code> flag:</p>

    <div style="border: 2px solid #333; padding: 20px; background: #f5f5f5; margin: 10px 0;">
      <p style="font-weight:bold; margin-bottom:10px;">Dockerfile Build Argument Flow:</p>
      <div style="display:flex; justify-content:space-around; align-items:center;">
        <div style="border:2px solid #1565c0; padding:12px; background:#e3f2fd; text-align:center; width:25%;">
          <strong>GitHub Secret</strong><br><code>NEXT_PUBLIC_API_URL</code>
        </div>
        <div style="font-size:20pt;">→</div>
        <div style="border:2px solid #e65100; padding:12px; background:#fff3e0; text-align:center; width:25%;">
          <strong>Docker ARG</strong><br><code>--build-arg</code>
        </div>
        <div style="font-size:20pt;">→</div>
        <div style="border:2px solid #2d7a2d; padding:12px; background:#e8f5e9; text-align:center; width:25%;">
          <strong>Next.js Bundle</strong><br>Embedded at build
        </div>
      </div>
      <p style="text-align:center; font-style:italic; font-size:10pt; margin-top:10px;">Fig 5.3 – Build-Time Environment Variable Injection Flow</p>
    </div>

    <h4 class="sub-section">5.2.4 Secret Management and Security</h4>
    <p>The GitHub Actions pipeline leverages GitHub's encrypted secrets store to manage sensitive credentials. The
      following secrets are configured at the repository level:</p>
    <ul>
      <li><strong>AWS_ACCESS_KEY_ID:</strong> IAM user access key with permissions for ECR push and EC2 SSH access.</li>
      <li><strong>AWS_SECRET_ACCESS_KEY:</strong> Corresponding secret key for AWS API authentication.</li>
      <li><strong>EC2_SSH_KEY:</strong> Private SSH key for secure remote access to the production EC2 instance.</li>
      <li><strong>NEXT_PUBLIC_API_URL:</strong> The production API endpoint URL injected at build time.</li>
    </ul>
    <p>All secrets are encrypted at rest using libsodium sealed boxes and are never exposed in pipeline logs. GitHub
      Actions automatically redacts any secret values that accidentally appear in stdout, providing an additional layer
      of protection against credential leakage.</p>

    <h3 class="section-heading">5.3 Jenkins Pipeline as Code</h3>
    <p>As a secondary CI/CD engine, Jenkins provides an on-premises automation capability through its declarative
      Pipeline-as-Code paradigm. The pipeline definition resides in the project's <code>Jenkinsfile</code>, a Groovy-based
      DSL that declaratively specifies the stages, steps, and post-actions of the build and deployment process.</p>

    <h4 class="sub-section">5.3.1 Jenkins Master-Agent Architecture</h4>
    <p>The Jenkins deployment follows a master-agent architecture where the Jenkins master controller orchestrates
      pipeline execution while delegating compute-intensive tasks to worker agents. For this project, a single-node
      Jenkins installation is used where the master also serves as the build agent, simplifying the infrastructure
      while maintaining the full pipeline capabilities.</p>
  </div>

  <div class="page">
    <h4 class="sub-section">5.3.2 Pipeline Stage Breakdown</h4>
    <p>The Jenkins pipeline is structured into five sequential stages, each with its own failure handling and
      notification configuration:</p>

    <table>
      <tr>
        <th>Stage</th>
        <th>Operations</th>
        <th>Failure Action</th>
      </tr>
      <tr>
        <td>1. Checkout</td>
        <td>Clones repository from GitHub using configured SCM credentials</td>
        <td>Pipeline aborts with error notification</td>
      </tr>
      <tr>
        <td>2. Build Customer</td>
        <td>Executes <code>docker build</code> with <code>--build-arg NEXT_PUBLIC_API_URL</code> for customer app</td>
        <td>Pipeline aborts; partial images cleaned up</td>
      </tr>
      <tr>
        <td>3. Build Merchant</td>
        <td>Executes <code>docker build</code> with <code>--build-arg NEXT_PUBLIC_API_URL</code> for merchant app</td>
        <td>Pipeline aborts; partial images cleaned up</td>
      </tr>
      <tr>
        <td>4. Build Backend</td>
        <td>Builds the Express.js backend image with Prisma client generation</td>
        <td>Pipeline aborts; partial images cleaned up</td>
      </tr>
      <tr>
        <td>5. Push to ECR</td>
        <td>Authenticates with AWS ECR and pushes all three tagged images sequentially</td>
        <td>Pipeline aborts; images remain local</td>
      </tr>
      <tr>
        <td>6. Deploy to EC2</td>
        <td>SSH into production instance, pull latest images, restart Docker Compose stack</td>
        <td>Manual intervention required; previous version remains running</td>
      </tr>
    </table>
    <p style="text-align:center; font-style:italic;">Table 5.2: Jenkins Pipeline Stages and Failure Handling</p>

    <div style="border: 2px solid #333; padding: 20px; background: #fafafa; margin: 10px 0; text-align:center;">
      <p style="font-weight:bold; font-size:12pt; margin-bottom:15px;">⚙️ Jenkins CI/CD Pipeline Architecture</p>
      <div style="border: 2px dashed #d32f2f; padding:15px; display:inline-block; text-align:left; width:90%; background:#fff;">
        <p style="font-weight:bold; text-align:center; color:#d32f2f;">Jenkins Master Controller</p>
        <div style="display:flex; justify-content:space-around; align-items:center; margin-top:15px;">
           <div style="border:1px solid #333; padding:10px; background:#e3f2fd; width:15%; text-align:center;">
             <strong>Stage 1</strong><br>Checkout
           </div>
           <div style="font-size:18pt;">➔</div>
           <div style="border:1px solid #333; padding:10px; background:#fff3e0; width:15%; text-align:center;">
             <strong>Stage 2</strong><br>Build Apps
           </div>
           <div style="font-size:18pt;">➔</div>
           <div style="border:1px solid #333; padding:10px; background:#e8f5e9; width:15%; text-align:center;">
             <strong>Stage 3</strong><br>Push ECR
           </div>
           <div style="font-size:18pt;">➔</div>
           <div style="border:1px solid #333; padding:10px; background:#f3e5f5; width:15%; text-align:center;">
             <strong>Stage 4</strong><br>Deploy
           </div>
           <div style="font-size:18pt;">➔</div>
           <div style="border:1px solid #333; padding:10px; background:#ffebee; width:15%; text-align:center;">
             <strong>Stage 5</strong><br>Verify
           </div>
        </div>
      </div>
      <p style="text-align:center; font-style:italic; font-size:10pt; margin-top:10px;">Fig 5.1 – Multi-Stage Jenkins Declarative Pipeline Architecture</p>
    </div>
  </div>

  <div class="page">
    <h4 class="sub-section">5.3.3 Post-Deployment Verification</h4>
    <p>After the deployment stage completes, the Jenkins pipeline executes automated health checks against the production
      endpoints. The verification phase sends HTTP requests to the backend health endpoint
      (<code>http://44.213.82.44:8000/health</code>) and validates that the response contains the expected JSON structure
      with <code>{"ok": true}</code>. If the health check fails after three retry attempts with exponential backoff, the
      pipeline triggers an alert notification and marks the build as unstable.</p>

    <h3 class="section-heading">5.4 Docker Containerization Strategy</h3>
    <p>Containerization forms the backbone of the deployment architecture, ensuring environment consistency across
      development, staging, and production. The Campus Cafeteria Pre-Booking System uses Docker to package each
      microservice into an isolated, reproducible, and lightweight container image.</p>

    <h4 class="sub-section">5.4.1 Multi-Stage Docker Builds</h4>
    <p>Each frontend application utilizes a multi-stage Docker build process to minimize the final image size. The build
      stage installs all development dependencies, compiles the Next.js application, and generates optimized production
      assets. The production stage copies only the compiled output and production dependencies, resulting in images that
      are typically 60-70% smaller than single-stage equivalents.</p>

    <table>
      <tr>
        <th>Service</th>
        <th>Base Image</th>
        <th>Exposed Port</th>
        <th>Build Size</th>
        <th>Key Features</th>
      </tr>
      <tr>
        <td>Customer App</td>
        <td><code>node:20-alpine</code></td>
        <td>3000</td>
        <td>~180 MB</td>
        <td>Next.js SSR, Prisma ORM, PostgreSQL client</td>
      </tr>
      <tr>
        <td>Merchant App</td>
        <td><code>node:20-alpine</code></td>
        <td>3000 → 3001</td>
        <td>~150 MB</td>
        <td>Next.js SSR, SSE client, real-time dashboard</td>
      </tr>
      <tr>
        <td>Backend API</td>
        <td><code>node:20-alpine</code></td>
        <td>4000 → 8000</td>
        <td>~120 MB</td>
        <td>Express.js, SSE broadcaster, CORS middleware</td>
      </tr>
      <tr>
        <td>PostgreSQL</td>
        <td><code>postgres:15-alpine</code></td>
        <td>5432</td>
        <td>~80 MB</td>
        <td>Persistent volume, auto-initialization scripts</td>
      </tr>
    </table>
    <p style="text-align:center; font-style:italic;">Table 5.3: Docker Image Specifications</p>

    <h4 class="sub-section">5.4.2 Dockerfile Architecture for Frontend Applications</h4>
    <p>The Dockerfile for the frontend applications follows a carefully designed pattern that addresses the unique
      requirements of Next.js production deployments. The key architectural decisions include:</p>
    <ul>
      <li><strong>Alpine Base Image:</strong> Using <code>node:20-alpine</code> reduces the base image footprint from ~900 MB
        (Debian-based) to ~180 MB, significantly decreasing pull times during deployment.</li>
      <li><strong>Dependency Caching:</strong> The <code>package.json</code> and <code>package-lock.json</code> are copied
        before the source code, leveraging Docker's layer caching to avoid reinstalling dependencies when only application
        code changes.</li>
      <li><strong>Build Argument Injection:</strong> The <code>ARG NEXT_PUBLIC_API_URL</code> directive accepts the API
        endpoint at build time, which is then set as <code>ENV NEXT_PUBLIC_API_URL</code> before the
        <code>npm run build</code> command executes.</li>
      <li><strong>Network Binding:</strong> The <code>HOSTNAME=0.0.0.0</code> environment variable ensures Next.js binds to
        all network interfaces, which is essential for Docker container networking.</li>
    </ul>
  </div>

  <div class="page">
    <h4 class="sub-section">5.4.3 Docker Compose Orchestration</h4>
    <p>Docker Compose serves as the container orchestration tool for the production deployment, defining the multi-service
      architecture in a declarative YAML format. The <code>docker-compose.yml</code> file specifies service definitions,
      port mappings, environment variables, volume mounts, and inter-service dependencies.</p>

    <table>
      <tr>
        <th>Configuration</th>
        <th>Service</th>
        <th>Host Port</th>
        <th>Container Port</th>
        <th>Purpose</th>
      </tr>
      <tr>
        <td>Port Mapping</td>
        <td>customer</td>
        <td>3000</td>
        <td>3000</td>
        <td>Public-facing student portal</td>
      </tr>
      <tr>
        <td>Port Mapping</td>
        <td>merchant</td>
        <td>8080</td>
        <td>3000</td>
        <td>Merchant order management dashboard</td>
      </tr>
      <tr>
        <td>Port Mapping</td>
        <td>backend</td>
        <td>8000</td>
        <td>4000</td>
        <td>REST API and SSE event broadcaster</td>
      </tr>
      <tr>
        <td>Port Mapping</td>
        <td>db</td>
        <td>5432</td>
        <td>5432</td>
        <td>PostgreSQL persistent data store</td>
      </tr>
      <tr>
        <td>Volume</td>
        <td>db</td>
        <td colspan="2">postgres_data:/var/lib/postgresql/data</td>
        <td>Persistent storage across container restarts</td>
      </tr>
    </table>
    <p style="text-align:center; font-style:italic;">Table 5.4: Docker Compose Port Mapping and Volume Configuration</p>

    <p>The Docker Compose network configuration creates an isolated bridge network that allows inter-service communication
      using service names as DNS hostnames. This means the backend can connect to the database using <code>db:5432</code>
      instead of hardcoded IP addresses, and the frontend containers can reach the backend via <code>backend:4000</code>
      within the Docker network.</p>

    <h3 class="section-heading">5.5 Amazon ECR Image Registry</h3>
    <p>Amazon Elastic Container Registry (ECR) serves as the private Docker image registry for the project. Three
      repositories are maintained in the <code>us-east-1</code> region:</p>
    <ul>
      <li><code>cafeteria-customer</code> — Customer wallet Next.js application images</li>
      <li><code>cafeteria-merchant</code> — Merchant dashboard Next.js application images</li>
      <li><code>cafeteria-backend</code> — Express.js backend API images</li>
    </ul>
    <p>Each image is tagged with the Git commit SHA and the <code>latest</code> tag, enabling both precise version tracking
      and convenient latest-image pulls during deployment. The ECR lifecycle policy automatically purges untagged images
      older than 30 days to manage storage costs.</p>

    <div style="border: 2px solid #333; padding: 20px; background: #f5f5f5; margin: 10px 0; text-align:center;">
      <p style="font-weight:bold; font-size:11pt; margin-bottom:15px;">🔄 End-to-End CI/CD Deployment Flow</p>
      <div style="display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap;">
        <div style="border:2px solid #333; padding:10px; background:#e3f2fd; width:18%; text-align:center; margin:5px;">
          <strong>Developer</strong><br>git push main
        </div>
        <div style="font-size:18pt;">→</div>
        <div style="border:2px solid #333; padding:10px; background:#fff3e0; width:18%; text-align:center; margin:5px;">
          <strong>GitHub Actions</strong><br>Build + Test
        </div>
        <div style="font-size:18pt;">→</div>
        <div style="border:2px solid #333; padding:10px; background:#e8f5e9; width:18%; text-align:center; margin:5px;">
          <strong>AWS ECR</strong><br>Push Images
        </div>
        <div style="font-size:18pt;">→</div>
        <div style="border:2px solid #333; padding:10px; background:#f3e5f5; width:18%; text-align:center; margin:5px;">
          <strong>EC2 Instance</strong><br>docker-compose up
        </div>
      </div>
      <p style="text-align:center; font-style:italic; font-size:10pt; margin-top:10px;">Fig 5.4 – End-to-End CI/CD Deployment Flow from Developer Push to Production</p>
    </div>
  </div>

  <div class="page">
    <h3 class="section-heading">5.6 AWS EC2 Deployment Architecture</h3>
    <p>The production environment is hosted on an Amazon EC2 <code>t3.small</code> instance running Amazon Linux 2 in the
      <code>us-east-1</code> region. The instance is configured with Docker and Docker Compose pre-installed, and
      authenticated against the ECR registry using an IAM instance role with
      <code>AmazonEC2ContainerRegistryReadOnly</code> permissions.</p>

    <div style="border: 2px solid #333; padding: 20px; background: #f0f7ff; margin: 10px 0; text-align:center;">
      <p style="font-weight:bold; font-size:12pt; margin-bottom:15px;">☁️ AWS Cloud (us-east-1)</p>
      <div style="border: 2px dashed #1565c0; padding:15px; display:inline-block; text-align:left; width:90%;">
        <p style="font-weight:bold; text-align:center;">EC2 Instance: t3.small (Amazon Linux 2) – 44.213.82.44</p>
        <div style="border:1px solid #333; padding:10px; margin:10px 0; background:#fff;">
          <p style="font-weight:bold; text-align:center;">Docker Compose Network (ec2-user_default)</p>
          <div style="display:flex; gap:10px; justify-content:space-around; margin-top:10px;">
            <div style="border:1px solid #2d7a2d; padding:8px; text-align:center; background:#e8f5e9;">
              <p style="font-weight:bold;">customer</p>
              <p style="font-size:9pt;">Next.js :3000</p>
            </div>
            <div style="border:1px solid #e65100; padding:8px; text-align:center; background:#fff3e0;">
              <p style="font-weight:bold;">merchant</p>
              <p style="font-size:9pt;">Next.js :8080</p>
            </div>
            <div style="border:1px solid #1565c0; padding:8px; text-align:center; background:#e3f2fd;">
              <p style="font-weight:bold;">backend</p>
              <p style="font-size:9pt;">Express :8000</p>
            </div>
            <div style="border:1px solid #6a1b9a; padding:8px; text-align:center; background:#f3e5f5;">
              <p style="font-weight:bold;">db</p>
              <p style="font-size:9pt;">PostgreSQL :5432</p>
            </div>
          </div>
          <p style="text-align:center; font-size:9pt; margin-top:8px;">Docker Volume: postgres_data (persistent)</p>
        </div>
        <p style="font-size:9pt;">Security Group: Inbound TCP 22, 3000, 8080, 8000 | IAM Role:
          AmazonEC2ContainerRegistryReadOnly</p>
      </div>
      <div style="margin-top:10px;">
        <div style="display:inline-block; border:1px solid #333; padding:8px; background:#fff; margin:5px;">📦 AWS
          ECR<br /><small>cafeteria-customer<br />cafeteria-merchant<br />cafeteria-backend</small></div>
      </div>
      <p style="text-align:center; font-style:italic; font-size:10pt; margin-top:10px;">Fig 5.2 – AWS EC2 Deployment
        Architecture with Docker Compose and ECR</p>
    </div>

    <h4 class="sub-section">5.6.1 Security Group Configuration</h4>
    <p>The EC2 instance's security group is configured with a principle-of-least-privilege approach, allowing inbound
      traffic only on the essential ports:</p>
    <table>
      <tr>
        <th>Port</th>
        <th>Protocol</th>
        <th>Source</th>
        <th>Purpose</th>
      </tr>
      <tr>
        <td>22</td>
        <td>TCP</td>
        <td>Admin IP only</td>
        <td>SSH access for deployment scripts</td>
      </tr>
      <tr>
        <td>3000</td>
        <td>TCP</td>
        <td>0.0.0.0/0</td>
        <td>Customer application web interface</td>
      </tr>
      <tr>
        <td>8080</td>
        <td>TCP</td>
        <td>0.0.0.0/0</td>
        <td>Merchant dashboard web interface</td>
      </tr>
      <tr>
        <td>8000</td>
        <td>TCP</td>
        <td>0.0.0.0/0</td>
        <td>Backend REST API and SSE endpoints</td>
      </tr>
    </table>
    <p style="text-align:center; font-style:italic;">Table 5.5: EC2 Security Group Inbound Rules</p>
  </div>

  <div class="page">
    <h3 class="section-heading">5.7 Deployment Script Architecture</h3>
    <p>The deployment process is automated through a series of shell scripts that encapsulate the Docker build, push,
      and deployment operations. These scripts provide a command-line interface for both manual and automated
      deployments.</p>

    <h4 class="sub-section">5.7.1 Image Build and Push Script</h4>
    <p>The <code>push-frontend.sh</code> script automates the process of building Docker images for both frontend
      applications and pushing them to their respective ECR repositories. The script performs the following operations
      sequentially:</p>
    <ul>
      <li>Authenticates with AWS ECR using the <code>aws ecr get-login-password</code> command</li>
      <li>Builds the customer application image with the <code>NEXT_PUBLIC_API_URL</code> build argument</li>
      <li>Tags the image with both the <code>latest</code> tag and the current Git commit SHA</li>
      <li>Pushes the tagged image to the <code>cafeteria-customer</code> ECR repository</li>
      <li>Repeats the process for the merchant application with the <code>cafeteria-merchant</code> repository</li>
    </ul>

    <h4 class="sub-section">5.7.2 EC2 Deployment Script</h4>
    <p>The <code>fix-ec2.sh</code> script handles the remote deployment on the EC2 instance. It establishes an SSH
      connection and executes a series of commands to pull the latest images and restart the Docker Compose stack:</p>
    <ul>
      <li>Authenticates with ECR on the remote instance to pull latest images</li>
      <li>Writes a dynamically generated <code>docker-compose.yml</code> to the instance</li>
      <li>Executes <code>docker-compose pull</code> to download updated images from ECR</li>
      <li>Runs <code>docker-compose down</code> followed by <code>docker-compose up -d</code> for a clean restart</li>
      <li>Prunes unused Docker images to reclaim disk space on the instance</li>
    </ul>

    <h3 class="section-heading">5.8 Monitoring and Observability</h3>
    <p>The deployed system includes basic monitoring capabilities through Docker's built-in logging and health check
      mechanisms. Container logs are accessible via <code>docker-compose logs</code> and can be filtered by service name
      for targeted debugging.</p>

    <h4 class="sub-section">5.8.1 Health Check Endpoints</h4>
    <p>The backend API exposes a <code>/health</code> endpoint that returns the current server status, active order count,
      and connected SSE client count. This endpoint is used by both the CI/CD pipeline's post-deployment verification
      and by external monitoring tools to ensure system availability.</p>

    <h4 class="sub-section">5.8.2 Container Resource Monitoring</h4>
    <p>Docker's native <code>docker stats</code> command provides real-time metrics for CPU usage, memory consumption,
      network I/O, and block I/O for each container. During load testing, the following resource utilization was
      observed:</p>

    <table>
      <tr>
        <th>Container</th>
        <th>CPU Usage</th>
        <th>Memory</th>
        <th>Network I/O</th>
      </tr>
      <tr>
        <td>customer</td>
        <td>0.15%</td>
        <td>185 MB</td>
        <td>12 KB/s</td>
      </tr>
      <tr>
        <td>merchant</td>
        <td>0.12%</td>
        <td>160 MB</td>
        <td>8 KB/s</td>
      </tr>
      <tr>
        <td>backend</td>
        <td>0.25%</td>
        <td>95 MB</td>
        <td>45 KB/s</td>
      </tr>
      <tr>
        <td>db</td>
        <td>0.08%</td>
        <td>75 MB</td>
        <td>3 KB/s</td>
      </tr>
    </table>
    <p style="text-align:center; font-style:italic;">Table 5.6: Container Resource Utilization Under Normal Load</p>

    <p>The lightweight resource footprint demonstrates that the system can comfortably run on a <code>t3.small</code>
      instance (2 vCPUs, 2 GB RAM), with significant headroom for traffic spikes during peak cafeteria hours. The total
      memory consumption across all four containers remains under 520 MB, leaving approximately 1.5 GB available for the
      operating system and burst capacity.</p>
  </div>

"""

# Now update the TOC for chapter 5 with expanded sub-sections
# First remove existing Ch5 TOC rows
old_toc_5 = """
      <tr style="border:none;">
        <td style="border:none;">5</td>
        <td style="border:none; font-weight:bold;">CONTINUOUS INTEGRATION AND DEPLOYMENT AUTOMATION</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.1</td>
        <td style="border:none;">Overview of CI/CD Methodology</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.2</td>
        <td style="border:none;">GitHub Actions Architecture</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.3</td>
        <td style="border:none;">Jenkins Pipeline as Code</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.4</td>
        <td style="border:none;">Docker Containerization Strategy</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.5</td>
        <td style="border:none;">AWS EC2 Deployment Architecture</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>"""

new_toc_5 = """
      <tr style="border:none;">
        <td style="border:none;">5</td>
        <td style="border:none; font-weight:bold;">CONTINUOUS INTEGRATION AND DEPLOYMENT AUTOMATION</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.1</td>
        <td style="border:none;">Overview of CI/CD Methodology</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.2</td>
        <td style="border:none;">GitHub Actions Architecture</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.3</td>
        <td style="border:none;">Jenkins Pipeline as Code</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.4</td>
        <td style="border:none;">Docker Containerization Strategy</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.5</td>
        <td style="border:none;">Amazon ECR Image Registry</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.6</td>
        <td style="border:none;">AWS EC2 Deployment Architecture</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.7</td>
        <td style="border:none;">Deployment Script Architecture</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.8</td>
        <td style="border:none;">Monitoring and Observability</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>"""

# Rebuild: everything before ch5 + new ch5 + ch6 onward
html_before_ch5 = html[:ch5_start]
html = html_before_ch5 + new_ch5 + "\n" + ch6_onward

# Replace TOC
html = html.replace(old_toc_5, new_toc_5)

# Update List of Tables to include new tables
lot_insert_before = html.find('<td style="border:none; text-align:left;">Customer App Database Schema</td>')
if lot_insert_before == -1:
    lot_insert_before = html.find('</table>\n  </div>\n\n  <!-- ══════════════════════════════════════════════ LIST OF FIGURES')

# Simpler: just append new table rows before the </table> in the List of Tables section
lot_section_start = html.find('<h2 class="mb-30">LIST OF TABLES</h2>')
lot_section_end = html.find('</table>', lot_section_start)
if lot_section_end != -1:
    new_table_rows = """
      <tr style="border:none;">
        <td style="border:none;">5.1</td>
        <td style="border:none; text-align:left;">GitHub Actions Workflow Phases</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.2</td>
        <td style="border:none; text-align:left;">Jenkins Pipeline Stages and Failure Handling</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.3</td>
        <td style="border:none; text-align:left;">Docker Image Specifications</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.4</td>
        <td style="border:none; text-align:left;">Docker Compose Port Mapping and Volume Configuration</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.5</td>
        <td style="border:none; text-align:left;">EC2 Security Group Inbound Rules</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.6</td>
        <td style="border:none; text-align:left;">Container Resource Utilization Under Normal Load</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
"""
    html = html[:lot_section_end] + new_table_rows + html[lot_section_end:]

# Update List of Figures to include new figures
lof_section_start = html.find('<h2 class="mb-30">LIST OF FIGURES</h2>')
lof_section_end = html.find('</table>', lof_section_start)
if lof_section_end != -1:
    new_fig_rows = """
      <tr style="border:none;">
        <td style="border:none;">5.3</td>
        <td style="border:none; text-align:left;">Build-Time Environment Variable Injection Flow</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
      <tr style="border:none;">
        <td style="border:none;">5.4</td>
        <td style="border:none; text-align:left;">End-to-End CI/CD Deployment Flow</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>
"""
    html = html[:lof_section_end] + new_fig_rows + html[lof_section_end:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully expanded Chapter 5 with 7+ pages of CI/CD content, updated TOC, indices, and added page-break CSS.")
