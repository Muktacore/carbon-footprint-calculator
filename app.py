from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, make_response,jsonify
import random, json, os
from PIL import Image, ImageDraw, ImageFont
import pdfkit

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Load or initialize user data
users = {}
user_scores = {}

if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        users = json.load(f)

if os.path.exists("scores.json"):
    with open("scores.json", "r") as f:
        user_scores = json.load(f)

fun_facts = [
    "If everyone in the U.S. recycled one-tenth of their newspapers, we could save 25 million trees each year!",
    "Producing recycled paper takes 40% less energy than making paper from virgin wood.",
    "Turning off your car instead of idling for 2+ minutes saves gas and reduces emissions!",
    "One meatless day per week can reduce your carbon footprint by over 100 kg annually."
]

tips = [
    "Switch to LED light bulbs to save energy.",
    "Unplug devices when not in use — phantom energy is real!",
    "Consider carpooling or using public transport once a week.",
    "Cut down on single-use plastics and recycle more often."
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/questionnaire')
def questionnaire():
    if 'username' not in session:
        flash("Please log in to access the questionnaire.")
        return redirect(url_for('login'))
    return render_template('questionnaire.html', username=session.get('username'))

@app.route('/result', methods=['POST'])
def result():
    username = session.get('username')
    if not username:
        flash("You must be logged in to submit results.")
        return redirect(url_for('login'))

    car_km = float(request.form.get('car_km', 0))
    electricity_kwh = float(request.form.get('electricity_kwh', 0))
    meat_meals = int(request.form.get('meat_meals', 0))
    tv_hours = float(request.form.get('tv_hours', 0))
    plastic_items = int(request.form.get('plastic_items', 0))
    recycle = request.form.get('recycle', 'no') == 'yes'

    car_emission = car_km * 0.21
    electricity_emission = electricity_kwh * 0.4
    meat_emission = meat_meals * 2.5
    tv_emission = tv_hours * 0.098
    plastic_emission = plastic_items * 0.08
    recycle_emission = 5 if recycle else 0

    total_emissions = round(car_emission + electricity_emission + meat_emission +
                            tv_emission + plastic_emission - recycle_emission, 2)

    session['score'] = total_emissions

    if username not in user_scores:
        user_scores[username] = []
    user_scores[username].append(total_emissions)

    with open("scores.json", "w") as f:
        json.dump(user_scores, f)

    if total_emissions < 50:
        avatar_file = "happy-earth.png.jpg"
        message = "You're an Eco Hero! 🌱 Keep it up!"
        session['eligible_for_certificate'] = True
    elif total_emissions < 100:
        avatar_file = "dizzy-earth.png.jpg"
        message = "Not bad! But there's room to improve 🌍"
        session['eligible_for_certificate'] = False
    elif total_emissions < 150:
        avatar_file = "sick-earth.png.jpg"
        message = "Try to cut down on emissions 🚗⚡️"
        session['eligible_for_certificate'] = False
    else:
        avatar_file = "crying-earth.png.jpg"
        message = "Oh no! Time to make eco-friendly changes 😢"
        session['eligible_for_certificate'] = False

    return render_template("result.html",
                           total=total_emissions,
                           car_emission=round(car_emission, 2),
                           electricity_emission=round(electricity_emission, 2),
                           meat_emission=round(meat_emission, 2),
                           recycle_emission=round(recycle_emission, 2),
                           avatar_path=f"images/{avatar_file}",
                           message=message,
                           fun_fact=random.choice(fun_facts),
                           tip=random.choice(tips),
                           username=username)

@app.route('/certificate')
def certificate():
    if session.get('eligible_for_certificate'):
        score = session.get('score', 0)
        return render_template('certificate.html', username=session['username'], score=score)
    else:
        flash("Certificate is only available for eco-friendly users!")
        return redirect(url_for('profile'))

@app.route('/download_certificate')
def download_certificate():
    username = session.get('username', 'Eco User')

    if not session.get('eligible_for_certificate'):
        flash("Certificate is only available for eco-friendly users!")
        return redirect(url_for('profile'))

    rendered = render_template('certificate.html', username=username, score=session['score'], download_mode=True)

    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')  # Update if needed
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={username}_certificate.pdf'
    return response

# === AUTH ===

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname in users and users[uname] == pwd:
            session['username'] = uname
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname in users:
            flash('Username already taken', 'warning')
        else:
            users[uname] = pwd
            user_scores[uname] = []

            # Save updated users
            with open("users.json", "w") as f:
                json.dump(users, f)

            with open("scores.json", "w") as f:
                json.dump(user_scores, f)

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    username = session.get('username')
    if not username:
        flash("You must be logged in to delete your account.", "warning")
        return redirect(url_for('login'))

    # Remove user from users and scores
    users.pop(username, None)
    user_scores.pop(username, None)

    # Save changes
    with open("users.json", "w") as f:
        json.dump(users, f)
    with open("scores.json", "w") as f:
        json.dump(user_scores, f)

    session.clear()
    flash("Your account has been deleted. We’ll miss you! 🌿", "info")
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        flash("Please log in to view your profile.")
        return redirect(url_for('login'))

    history = user_scores.get(username, [])
    score = history[-1] if history else None
    return render_template('profile.html', username=username, score=score, history=history)

   
@app.route('/clear_scores', methods=['POST'])
def clear_scores():
    username = session.get('username')
    if not username:
        flash("You must be logged in to clear your scores.")
        return redirect(url_for('login'))

    user_scores[username] = []
    with open("scores.json", "w") as f:
        json.dump(user_scores, f)

    flash("Your score history has been cleared.", "info")
    return redirect(url_for('profile'))


# Route for eco-tree (Your main route)
@app.route('/submit_score', methods=['POST'])
def submit_score():
    username = session.get('username')  # Assuming username is stored in session after login
    if username:
        score = request.form.get('score')  # Assuming you send score from the form
        score = int(score)  # Convert score to integer

        # Load the current scores from the JSON file
        with open('scores.json', 'r') as f:
            score_data = json.load(f)

        # Initialize the user's score history if they don't exist yet
        if username not in score_data:
            score_data[username] = []

        # Append the current score to the user's score history
        score_data[username].append(score)

        # Save the updated scores back to the JSON file
        with open('scores.json', 'w') as f:
            json.dump(score_data, f)

    return redirect(url_for('eco_tree'))

@app.route('/eco-tree')
def eco_tree():
    username = session.get('username')
    
    if not username:
        return render_template('eco_tree.html', username=None, user_tree_stage=None)

    # Load user scores from scores.json
    with open('scores.json', 'r') as f:
        score_data = json.load(f)

    user_history = score_data.get(username, [])
    if len(user_history) == 0:
        return render_template('eco_tree.html', username=username, user_tree_stage=None)

    initial_score = user_history[0]  # First score is considered the baseline (initial score)
    latest_score = user_history[-1]  # Latest score is the most recent score

    improvement = max(0, initial_score - latest_score)  # How much the user improved

    # Tree growth logic based on improvement
    if improvement < 10:
        user_tree_stage = 'seedling'
    elif improvement < 20:
        user_tree_stage = 'sapling'
    elif improvement < 35:
        user_tree_stage = 'young_tree'
    elif improvement < 50:
        user_tree_stage = 'growing_tree'
    elif improvement < 70:
        user_tree_stage = 'flourishing_tree'
    elif improvement < 90:
        user_tree_stage = 'mighty_tree'
    else:
        user_tree_stage = 'grand_oak'

    return render_template('eco_tree.html', username=username, user_tree_stage=user_tree_stage)

if __name__ == "__main__":
    app.run(debug=True)