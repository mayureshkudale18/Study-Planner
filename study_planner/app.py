from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html')


# Result route
@app.route('/result', methods=['POST'])
def result():
    subjects_input = request.form['subjects']
    difficulty_input = request.form['difficulty']
    days = int(request.form['days'])
    total_pages = int(request.form['pages'])
    study_hours = int(request.form['hours'])

    subjects = [s.strip() for s in subjects_input.split(',')]
    difficulties = [d.strip().lower() for d in difficulty_input.split(',')]

    # Validate input
    if len(subjects) != len(difficulties):
        return "Error: Subjects and difficulties count must match!"

    # Maps
    pages_per_hour_map = {}
    weight_map = {}

    for i in range(len(subjects)):
        diff = difficulties[i]

        if diff == "easy":
            pages_per_hour_map[subjects[i]] = 2.5
            weight_map[subjects[i]] = 1
        elif diff == "medium":
            pages_per_hour_map[subjects[i]] = 2.0
            weight_map[subjects[i]] = 2
        else:
            pages_per_hour_map[subjects[i]] = 1.5
            weight_map[subjects[i]] = 3

    # Total hours calculation
    total_hours_needed = 0
    pages_per_subject = total_pages / len(subjects)

    for subject in subjects:
        total_hours_needed += pages_per_subject / pages_per_hour_map[subject]

    pages_per_day = total_pages / days
    hours_per_day_needed = total_hours_needed / days

    # Priority scheduling
    weighted_subjects = []
    for subject in subjects:
        weighted_subjects.extend([subject] * weight_map[subject])

    plan = []
    count = {subject: 0 for subject in subjects}

    for i in range(days):
        subject = weighted_subjects[i % len(weighted_subjects)]
        plan.append(f"Day {i+1}: Study {subject}")
        count[subject] += 1

    # Hours-based graph
    hours_distribution = {}
    for subject in subjects:
        hours_distribution[subject] = count[subject] * hours_per_day_needed

    plt.figure(figsize=(5,4))
    plt.bar(hours_distribution.keys(), hours_distribution.values())
    plt.xlabel("Subjects")
    plt.ylabel("Hours Allocated")
    plt.title("Study Hours Distribution")

    graph_path = os.path.join('static', 'graph.png')
    plt.savefig(graph_path)
    plt.close()

    # Smart suggestion
    if hours_per_day_needed > study_hours:
        status = " Increase study hours or extend days."
    else:
        status = " Your plan is manageable."

    return render_template('result.html',
                           plan=plan,
                           graph='graph.png',
                           total_hours=round(total_hours_needed, 2),
                           pages_per_day=round(pages_per_day, 2),
                           hours_per_day=round(hours_per_day_needed, 2),
                           status=status)


if __name__ == '__main__':
    app.run(debug=True)