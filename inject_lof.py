import re

html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

if "LIST OF FIGURES" not in html:
    print("LIST OF FIGURES is missing. Injecting it back.")
    list_of_figures_html = """
    <div class="page">
      <h2 style="font-size: 16pt; text-align: center; font-weight: bold; text-indent: 0 !important; margin-bottom:30px;">LIST OF FIGURES</h2>
      <table style="border:none; width: 100%;">
        <tr style="border:none;">
          <th style="border:none; text-align:left; width:15%; font-weight:bold;">FIGURE NO.</th>
          <th style="border:none; text-align:left; font-weight:bold;">TITLE</th>
          <th style="border:none; text-align:right; font-weight:bold;">PAGE NO.</th>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">3.1</td>
          <td style="border:none; text-align:left;">System Architecture Diagram</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">3.2</td>
          <td style="border:none; text-align:left;">Data Flow Diagram</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">3.3</td>
          <td style="border:none; text-align:left;">Use Case Diagram</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">3.4</td>
          <td style="border:none; text-align:left;">Level 0 Context DFD</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">3.5</td>
          <td style="border:none; text-align:left;">Sequence Diagram</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">4.1</td>
          <td style="border:none; text-align:left;">Customer App – Home Page</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">4.2</td>
          <td style="border:none; text-align:left;">Cafeteria Menu Page</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">4.3</td>
          <td style="border:none; text-align:left;">Order Confirmation Screen</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">4.4</td>
          <td style="border:none; text-align:left;">Merchant Dashboard</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">5.1</td>
          <td style="border:none; text-align:left;">Multi-Stage Jenkins Declarative Pipeline Architecture</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
        <tr style="border:none;">
          <td style="border:none;">5.2</td>
          <td style="border:none; text-align:left;">AWS EC2 Deployment Architecture with Docker Compose and ECR</td>
          <td style="border:none; text-align:right;">XX</td>
        </tr>
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
      </table>
    </div>
    """
    
    # We must insert it precisely after the </table> of the LIST OF TABLES
    match = re.search(r'(<h2[^>]*>LIST OF TABLES</h2>[\s\S]*?</table>)\s*</div>', html)
    if match:
        insertion_idx = match.end()
        html = html[:insertion_idx] + "\n" + list_of_figures_html + "\n" + html[insertion_idx:]
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print("Success.")
    else:
        print("Failed to find insertion point.")
