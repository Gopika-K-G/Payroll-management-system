from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'gopi@08'

def get_db_connection():
    try:
        myconn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Gopi@sql08',
            database='payroll_system'
        )
        print("Connected successfully")
        return myconn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND role = 'admin'", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error_message = "Invalid username or password"
            return render_template('admin_login.html', error=error_message)

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' in session:
        return render_template('admin_dashboard.html')
    return redirect('/admin')

@app.route('/employee', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND role = 'employee'", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['employee'] = username  
            return redirect(url_for('employee_dashboard'))
        else:
            error_message = "Invalid username or password"
            return render_template('employee_login.html', error=error_message)

    return render_template('employee_login.html')

@app.route('/employee/dashboard')
def employee_dashboard():
    if 'employee' in session:
        username = session['employee']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT emp_name FROM employees WHERE emp_id = %s", (username,))
        employee_name = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return render_template('employee_dashboard.html', employee_name=employee_name)
    return redirect('/employee')

@app.route('/admin/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'admin' in session:
        if request.method == 'POST':
            emp_id = request.form['emp_id']
            name = request.form['name']
            position = request.form['position']
            age = request.form['age']
            dob = request.form['dob']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            basic_salary = request.form['basic_salary']
            da = request.form['da']
            hra = request.form['hra']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO employees (emp_id, emp_name, position, age, dob, email_id, phone_no, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (emp_id, name, position, age, dob, email, phone, address))
            conn.commit()
            cursor.execute("INSERT INTO salaries (emp_id, basic_salary, da, hra) VALUES (%s, %s, %s, %s)", (emp_id, basic_salary, da, hra))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('view_employees'))
        return render_template('add_employee.html')
    return redirect('/admin')

@app.route('/admin/view_employees')
def view_employees():
    if 'admin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT e.*, s.basic_salary, s.da, s.hra FROM employees e JOIN salaries s ON e.emp_id = s.emp_id")
        employees = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('view_employees.html', employees=employees)
    return redirect(url_for('admin_login'))

@app.route('/admin/update_employee', methods=['GET', 'POST'])
def update_employee():
    if 'admin' in session:
        if request.method == 'POST':
            emp_id = request.form['emp_id']
            name = request.form['name']
            position = request.form['position']
            age = request.form['age']
            dob = request.form['dob']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            basic_salary = request.form['basic_salary']
            da = request.form['da']
            hra = request.form['hra']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE employees SET emp_name=%s, position=%s, age=%s, dob=%s, email_id=%s, phone_no=%s, address=%s WHERE emp_id=%s", (name, position, age, dob, email, phone, address, emp_id))
            conn.commit()
            cursor.execute("UPDATE salaries SET basic_salary=%s, da=%s, hra=%s WHERE emp_id=%s", (basic_salary, da, hra, emp_id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('view_employees'))
        else:
            return render_template('update_employee.html')
    return redirect('/admin')

@app.route('/admin/delete_employee/', methods=['GET', 'POST'])
def delete_employee():
    if 'admin' in session:
        if request.method == 'POST':
            emp_id = request.form['emp_id']  
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE emp_id=%s", (emp_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('view_employees'))
        else:
            return render_template('delete_employee.html')
    return redirect('/admin')

@app.route('/admin/view_salary', methods=['GET'])
def fetch_salary():
    if 'admin' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT e.emp_name FROM employees e INNER JOIN salaries s ON e.emp_id = s.emp_id")
        employee_names = cursor.fetchall()

        salaries = []
        for employee_name in employee_names:
            cursor.execute("""SELECT a.month, a.No_of_days_Present, a.Leave_taken_Days, 
                                    a.late_entry, a.overtime_hours, s.basic_salary, s.da, s.hra
                              FROM attendance a 
                              INNER JOIN salaries s ON a.emp_id = s.emp_id 
                              INNER JOIN employees e ON a.emp_id = e.emp_id 
                              WHERE e.emp_name = %s""", (employee_name['emp_name'],))
            salary_records = cursor.fetchall()

            salary_details = []
            for salary_record in salary_records:
                No_of_days_Present = salary_record['No_of_days_Present']
                total_late_entries = salary_record['late_entry']
                total_leave_taken = salary_record['Leave_taken_Days']
                overtime_hours = salary_record['overtime_hours']

                total_salary = salary_record['basic_salary'] + salary_record['da'] + salary_record['hra']
                total_salary -= total_late_entries * 100
                if No_of_days_Present != 0:
                    total_salary -= total_leave_taken * (salary_record['basic_salary'] / 28)
                total_salary=float(total_salary)
                total_salary += overtime_hours * (float(salary_record['basic_salary']) / 28) * 1.5

                salary_details.append({
                    'month': salary_record['month'],
                    'No_of_days_Present': No_of_days_Present,
                    'total_leave_taken': total_leave_taken,
                    'total_late_entries': total_late_entries,
                    'total_overtime_hours': overtime_hours,
                    'total_salary': total_salary
                })

            salaries.append({
                'emp_name': employee_name['emp_name'],
                'salary_details': salary_details
            })

        cursor.close()
        conn.close()
        return render_template('view_salary.html', salaries=salaries)
    else:
        return redirect(url_for('admin_dashboard'))


@app.route('/employee/view_profile')
def view_profile():
    if 'employee' in session:
        username = session['employee']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT emp_id, emp_name, position, age, dob, email_id, phone_no, address FROM employees WHERE emp_id = %s", (username,))
        employee = cursor.fetchone()
        cursor.close()
        conn.close()

        return render_template('employee_profile.html', employee=employee)
    return redirect('/employee')

@app.route('/employee/view_salary', methods=['GET', 'POST'])
def view_employee_salary():
    if 'employee' in session:
        username = session['employee']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT emp_name FROM employees WHERE emp_id = %s", (username,))
        employee = cursor.fetchone()
        
        cursor.execute("SELECT * FROM salaries WHERE emp_id = %s", (username,))
        salary_details = cursor.fetchone()
        
        attendance_details = None
        total_salary = None
        
        if request.method == 'POST':
            month = request.form['month']
            year = request.form['year']
            
            cursor.execute("SELECT * FROM attendance WHERE emp_id = %s AND month = %s AND year = %s", (username, month, year))
            attendance_details = cursor.fetchone()
            
            if salary_details and attendance_details:
                No_of_days_Present = attendance_details['No_of_days_Present']
                total_late_entries = attendance_details['late_entry']
                total_leave_taken = attendance_details['Leave_taken_Days']
                overtime_hours = attendance_details['overtime_hours']

                total_salary = salary_details['basic_salary'] + salary_details['da'] + salary_details['hra']
                total_salary -= total_late_entries * 100
                if No_of_days_Present != 0:
                 total_salary -= total_leave_taken * (salary_details['basic_salary'] / 28)
                total_salary = float(total_salary)
                total_salary += overtime_hours * (float(salary_details['basic_salary']) / 28) * 1.5

        
        cursor.close()
        conn.close()
        
        return render_template('employee_salary.html', employee=employee, salary_details=salary_details, 
                               attendance_details=attendance_details, total_salary=total_salary)
    return redirect('/employee')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin')

@app.route('/employee/logout')
def employee_logout():
    session.pop('employee', None)
    return redirect('/employee')

if __name__ == '__main__':
    app.run(debug=True)
