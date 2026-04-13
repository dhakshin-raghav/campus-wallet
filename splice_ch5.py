import re
import os

html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Rename Chapter 5 -> Chapter 6 (Conclusion)
# In body:
html = html.replace('<div class="chapter-title">CHAPTER 5<br>CONCLUSION AND FUTURE WORKS</div>',
                    '<div class="chapter-title">CHAPTER 6<br>CONCLUSION AND FUTURE WORKS</div>')
html = html.replace('<h3 class="section-heading">5.1 Conclusion</h3>', '<h3 class="section-heading">6.1 Conclusion</h3>')
html = html.replace('<h3 class="section-heading">5.2 Future Enhancement</h3>', '<h3 class="section-heading">6.2 Future Enhancement</h3>')
html = html.replace('<h3 class="section-heading">5.2 Future Works</h3>', '<h3 class="section-heading">6.2 Future Works</h3>')

# In TOC:
html = html.replace('<td style="border:none;">5</td>\n        <td style="border:none; font-weight:bold;">CONCLUSION',
                    '<td style="border:none;">6</td>\n        <td style="border:none; font-weight:bold;">CONCLUSION')
html = html.replace('<td style="border:none;">5.1</td>\n        <td style="border:none;">Conclusion',
                    '<td style="border:none;">6.1</td>\n        <td style="border:none;">Conclusion')
html = html.replace('<td style="border:none;">5.2</td>\n        <td style="border:none;">Future',
                    '<td style="border:none;">6.2</td>\n        <td style="border:none;">Future')

# 2. Extract Ch 4.7 EC2 Deployment Architecture
ec2_start = html.find('<h3 class="section-heading">4.7 AWS EC2 Deployment Architecture</h3>')
if ec2_start != -1:
    ec2_end = html.find('</div>', html.find('Fig 4.5 – AWS EC2 Deployment', ec2_start)) + 6
    ec2_html = html[ec2_start:ec2_end]
    html = html[:ec2_start] + html[ec2_end:]
    
    # Change numbering within ec2_html
    ec2_html = ec2_html.replace('4.7 AWS EC2 Deployment', '5.5 AWS EC2 Deployment')
    ec2_html = ec2_html.replace('Fig 4.5 – AWS EC2', 'Fig 5.2 – AWS EC2')
else:
    ec2_html = ""

# 3. Create Chapter 5 HTML
ch5_html = """
  <!-- ═══════════════════════════════════════════════ CHAPTER 5 ═══ -->
  <div class="page">
    <div class="chapter-title">CHAPTER 5<br>CONTINUOUS INTEGRATION AND DEPLOYMENT AUTOMATION</div>

    <h3 class="section-heading">5.1 Overview of CI/CD Methodology</h3>
    <p>In modern software engineering, Continuous Integration (CI) and Continuous Deployment (CD) are fundamental practices that ensure high code quality and rapid delivery. For the Campus Cafeteria Pre-Booking System, a robust CI/CD pipeline was architected to fully automate the build, testing, and deployment lifecycle. This pipeline eliminates the risk of manual deployment errors, enforces strict code quality gates, and guarantees that any code pushed to the main branch is consistently formatted and tested before being orchestrated into the live AWS cloud environment.</p>

    <h3 class="section-heading">5.2 GitHub Actions Architecture</h3>
    <p>GitHub Actions serves as the primary CI engine, orchestrating automated workflows triggered by critical repository events. High-velocity development requires reliable feedback loops, which GitHub Actions provides through isolated, ephemeral Ubuntu runner environments.</p>

    <h4 class="sub-section">5.2.1 Workflow Pipeline Phases</h4>
    <ul>
      <li><strong>Checkout and Setup:</strong> The pipeline initializes by cleanly checking out the repository and caching Node.js dependencies using <code>actions/setup-node</code>, accelerating subsequent execution times.</li>
      <li><strong>Concurrent Build Matrix:</strong> The system leverages a build matrix to parallelize the compilation of Next.js frontend applications, executing strict TypeScript type-checking to prevent runtime regressions.</li>
      <li><strong>Secret Management:</strong> Sensitive deployment variables, including the <code>NEXT_PUBLIC_API_URL</code>, are dynamically injected at build-time directly from GitHub's encrypted secrets vault to ensure secure environment configuration without exposing credentials.</li>
    </ul>

    <h3 class="section-heading">5.3 Jenkins Pipeline as Code</h3>
    <p>Alongside GitHub Actions, the deployment framework features a comprehensive Jenkins integration built on declarative Pipeline-as-Code principles. The <code>Jenkinsfile</code> defines a multi-stage delivery pipeline, ensuring consistency across environments.</p>
    
    <div style="border: 2px solid #333; padding: 20px; background: #fafafa; margin: 10px 0; text-align:center;">
      <p style="font-weight:bold; font-size:12pt; margin-bottom:15px;">⚙️ Jenkins CI/CD Pipeline Architecture</p>
      <div style="border: 2px dashed #d32f2f; padding:15px; display:inline-block; text-align:left; width:90%; background:#fff;">
        <p style="font-weight:bold; text-align:center; color:#d32f2f;">Jenkins Master Controller</p>
        <div style="display:flex; justify-content:space-around; align-items:center; margin-top:15px;">
           <div style="border:1px solid #333; padding:10px; background:#e3f2fd; width:22%; text-align:center;">
             <strong>Stage 1</strong><br>Checkout
           </div>
           <div style="font-size:24pt;">➔</div>
           <div style="border:1px solid #333; padding:10px; background:#fff3e0; width:22%; text-align:center;">
             <strong>Stage 2</strong><br>Build Images
           </div>
           <div style="font-size:24pt;">➔</div>
           <div style="border:1px solid #333; padding:10px; background:#e8f5e9; width:22%; text-align:center;">
             <strong>Stage 3</strong><br>Push to ECR
           </div>
           <div style="font-size:24pt;">➔</div>
           <div style="border:1px solid #333; padding:10px; background:#f3e5f5; width:22%; text-align:center;">
             <strong>Stage 4</strong><br>Deploy EC2
           </div>
        </div>
      </div>
      <p style="text-align:center; font-style:italic; font-size:10pt; margin-top:10px;">Fig 5.1 – Multi-Stage Jenkins Declarative Pipeline Architecture</p>
    </div>

    <p>The Jenkins master safely executes shell operations within secure workspace nodes. It handles Docker runtime execution to spin up isolated builder containers, pushing finalized immutable artifacts into Amazon Elastic Container Registry (ECR). Crucially, the deploy stage uses an SSH integration to securely trigger the <code>fix-ec2.sh</code> orchestration script directly on the production EC2 instance, causing a zero-downtime rolling update of the Docker Compose stack.</p>

  </div>

  <div class="page">
    <h3 class="section-heading">5.4 Docker Containerization Strategy</h3>
    <p>Modern microservice deployments rely heavily on containerization to ensure parity between development and production environments. The Campus Cafeteria Pre-Booking System establishes three discrete, immutable Docker images:</p>
    <ul>
      <li><strong>Customer Wallet Image:</strong> Configured to expose port 3000, optimized for Next.js production builds.</li>
      <li><strong>Merchant Dashboard Image:</strong> Configured to expose port 3001, stripped of development modules to ensure minimal footprint.</li>
      <li><strong>Backend API Image:</strong> Configured over port 4000 (mapped to 8000), implementing Prisma caching.</li>
    </ul>

""" + "\n" + ec2_html + "\n  </div>\n\n"

# 4. Insert Chapter 5 block before Chapter 6
# Look for "<!-- ═══════════════════════════════════════════════ CHAPTER 5 ═══ -->" (now maybe has 6, let's just find the chapter-title)
insertion_idx = html.find('<!-- ═══════════════════════════════════════════════ CHAPTER 5 ═══ -->')
if insertion_idx != -1:
    html = html[:insertion_idx] + ch5_html + html[insertion_idx:]
    # Replace the old comment banner for ch 6
    html = html.replace('<!-- ═══════════════════════════════════════════════ CHAPTER 5 ═══ -->', '<!-- ═══════════════════════════════════════════════ CHAPTER 6 ═══ -->', 1)

# 5. Insert Chapter 5 rows into TOC
toc_ch6_idx = html.find('<tr style="border:none;">\n        <td style="border:none;">6</td>\n        <td style="border:none; font-weight:bold;">CONCLUSION')
if toc_ch6_idx != -1:
    toc_ch5 = """
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
    html = html[:toc_ch6_idx] + toc_ch5 + "\n      " + html[toc_ch6_idx:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
    
print("Successfully spliced Chapter 5 CI/CD and shifted Conclusion to Chapter 6.")
