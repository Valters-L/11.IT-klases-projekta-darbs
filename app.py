from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load the data
df = pd.read_excel('data/form_results.xlsx')
avg_sleep_per_grade = df.groupby('grade')['avg_sleep'].mean()

# Function to generate bar plot
def generate_plot(selected_grades=None, user_sleep=None):
    if not selected_grades:
        selected_grades = avg_sleep_per_grade.index.tolist()

    filtered_data = avg_sleep_per_grade[avg_sleep_per_grade.index.isin(selected_grades)]
    
    if filtered_data.empty:
        filtered_data = avg_sleep_per_grade
    
    plt.figure(figsize=(8, 6))
    plt.bar(filtered_data.index, filtered_data.values, color='skyblue', width=0.5)
    plt.xlabel("Grade")
    plt.ylabel("Average Sleep (Hours)")
    plt.title("Average Sleep per Grade")

    if user_sleep is not None:
        plt.axhline(user_sleep, color='red', linestyle='--', label=f'Your Sleep ({user_sleep} hrs)')
        plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return img_base64

# Function to generate pie chart (without any additional effects)
def generate_pie_chart():
    used_before_sleep_counts = df['used_before_sleep'].value_counts()
    
    plt.figure(figsize=(6, 6))
    plt.pie(used_before_sleep_counts, labels=used_before_sleep_counts.index, autopct='%1.1f%%', startangle=90, colors=['lightcoral', 'lightgreen', 'lightskyblue'])
    plt.title("Do you use your phone before sleeping?")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return img_base64

# Function to generate correlation graph
def generate_correlation_graph():
    grouped_data = df.groupby('phone_time_usage_before_sleep')['avg_sleep'].mean().reset_index()
    
    plt.figure(figsize=(8, 6))
    plt.plot(grouped_data['phone_time_usage_before_sleep'], grouped_data['avg_sleep'], marker='o', color='blue', linestyle='-', linewidth=1, markersize=5)
    plt.xlabel("Phone usage before sleep (minutes)")
    plt.ylabel("Average sleep time (hours)")
    plt.title("Average sleep time depending on phone usage before sleep")
    plt.grid(True, linestyle='--', alpha=0.7)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return img_base64

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/page1', methods=['GET'])
def page1():
    plot_url = generate_plot()
    return render_template('page1.html', plot_url=plot_url, grades=avg_sleep_per_grade.index.tolist())

@app.route('/update-graph', methods=['POST'])
def update_graph():
    selected_grades = request.json.get('grades', [])
    user_sleep = request.json.get('user_sleep', None)
    plot_url = generate_plot(selected_grades, user_sleep)
    return jsonify({'plot_url': plot_url})

@app.route('/page2')
def page2():
    pie_chart_url = generate_pie_chart()  # No effect added to pie chart here
    correlation_graph_url = generate_correlation_graph()
    
    used_before_sleep_counts = df['used_before_sleep'].value_counts(normalize=True) * 100
    correct_answer = round(used_before_sleep_counts.get('jā', 94.3), 1)
    
    return render_template('page2.html', pie_chart_url=pie_chart_url, correlation_graph_url=correlation_graph_url, correct_answer=correct_answer)



@app.route('/page3')
def page3():
    return render_template('page3.html')


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
