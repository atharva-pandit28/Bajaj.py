from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

form_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Webhook Submission</title>
</head>
<body>
    <h2>Submit Details for Webhook</h2>
    <form method="POST">
        <label>Name:</label><br>
        <input type="text" name="name" required><br><br>

        <label>Registration Number:</label><br>
        <input type="text" name="regNo" required><br><br>

        <label>Email:</label><br>
        <input type="email" name="email" required><br><br>

        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

def generate_query(reg_no):
    last_digit = int(reg_no[-1])
    is_odd = last_digit % 2 != 0

    query = """
    SELECT 
        p.AMOUNT AS SALARY,
        CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS NAME,
        TIMESTAMPDIFF(YEAR, e.DOB, CURDATE()) AS AGE,
        d.DEPARTMENT_NAME
    FROM PAYMENTS p
    JOIN EMPLOYEE e ON p.EMP_ID = e.EMP_ID
    JOIN DEPARTMENT d ON e.DEPARTMENT = d.DEPARTMENT_ID
    WHERE DAY(p.PAYMENT_TIME) != 1
    ORDER BY p.AMOUNT DESC
    LIMIT 1;
    """
    return query

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        reg_no = request.form['regNo']
        email = request.form['email']

        user_data = {
            "name": name,
            "regNo": reg_no,
            "email": email
        }

        webhook_url = "https://bfhldevapigw.healthrx.co.in/hiring/generateWebhook/PYTHON"

        try:
            webhook_response = requests.post(webhook_url, json=user_data)

            if webhook_response.status_code == 200:
                response_data = webhook_response.json()
                result_webhook = response_data.get("webhook")
                access_token = response_data.get("accessToken")

                final_query = generate_query(reg_no)

                headers = {
                    "Authorization": access_token,
                    "Content-Type": "application/json"
                }

                solution_data = {
                    "finalQuery": final_query
                }

                submit_response = requests.post(result_webhook, headers=headers, json=solution_data)

                if submit_response.status_code == 200:
                    return f"<h3>✅ Success!<br><br>Response: {submit_response.text}</h3>"
                else:
                    return f"<h3>❌ Error submitting solution: {submit_response.status_code}</h3><p>{submit_response.text}</p>"
            else:
                return f"<h3>❌ Error generating webhook: {webhook_response.status_code}</h3><p>{webhook_response.text}</p>"
        except Exception as e:
            return f"<h3>⚠️ Exception occurred:</h3><p>{str(e)}</p>"

    return render_template_string(form_html)

if __name__ == '__main__':
    app.run(debug=True)

