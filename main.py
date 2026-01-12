from flask import Flask, render_template_string, request, redirect, session, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
import json, os

app = Flask(__name__)
app.secret_key = "1crCYMD09$Qb8of2dLxYL^$G9pMu%4D!VQU*-IMkSO@oxefL+Z$vb_DS55+*roJ@d46LHBRluq5xGS(X$XJm)GW=rQleJK!T9%Fk"

# -------------------- DATA FILES --------------------
USERS_FILE = "users.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({"users": {}}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

if os.path.exists("embed.json"):
    with open("embed.json", "r", encoding="utf-8") as f:
        games = json.load(f)
else:
    games = []

# -------------------- HTML & CSS --------------------
HTML = """ 
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Gamesplat</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
/* GLOBAL */
body{font-family:Poppins;background:#05061d;color:white;margin:0;overflow-x:hidden;transition:background .3s}

/* HEADER */
header{padding:20px;text-align:center;position:relative}
header img{width:120px}
header h1{margin:10px 0 0 0;font-weight:800;letter-spacing:1px}
header p{margin:5px 0 0 0;font-weight:300;color:#aaa}

/* GRID CARDS */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:25px;padding:40px}
.card{background:#111;border-radius:20px;cursor:pointer;overflow:hidden;position:relative;transition:transform .3s, box-shadow .3s;border: 1px solid #222}
.card:hover{transform:scale(1.05);box-shadow:0 0 20px #4ef2ff, 0 0 40px #00ffff inset;border-color: #4ef2ff}
.card img{width:100%;height:160px;object-fit:cover;transition:transform .3s}
.card h3{padding:10px;text-align:center;transition:text-shadow .3s;margin:0}
.card:hover h3{color:#4ef2ff;text-shadow:0 0 10px #4ef2ff}

/* BADGES & COUNTS */
.badge{position:absolute;top:10px;left:10px;background:rgba(0,0,0,0.8);padding:5px 10px;border-radius:20px;font-size:12px;border:1px solid #4ef2ff}
.vote-count{position:absolute;top:10px;right:10px;background:#4ef2ff;color:black;padding:5px 10px;border-radius:20px;font-size:14px;font-weight:600}

/* MODALS */
.modal{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:2000;animation:fadeIn 0.4s ease forwards;backdrop-filter: blur(5px)}
.modal-box{background:#111;padding:30px;border-radius:20px;width:90%;max-width:500px;position:relative;animation:scaleInGlow 0.5s ease forwards;box-shadow:0 0 20px #4ef2ff,0 0 40px #4ef2ff inset; max-height: 85vh; overflow-y: auto; border: 1px solid #4ef2ff}

/* PLAYER */
.player{position:fixed;inset:0;background:black;display:none;z-index:4000;align-items:center;justify-content:center}
.player iframe{width:95%;height:85%;border:none;border-radius:20px;box-shadow:0 0 50px #4ef2ff;animation:scaleInGlow 0.6s ease forwards}

/* BUTTONS */
button{padding:12px 20px;border-radius:25px;border:none;cursor:pointer;transition:all .3s;font-family:Poppins;font-weight:600}
button:hover{transform:scale(1.1);filter:brightness(1.2)}

.like{background:#4ef2ff;color:black;box-shadow:0 0 10px #4ef2ff}
.dislike{background:#ff4e4e;color:white;box-shadow:0 0 10px #ff4e4e}

/* INPUTS */
input, select{width:100%;padding:12px;margin:8px 0;border-radius:12px;border:1px solid #333;background:#1a1a1a;color:white;outline:none;transition:all .3s;box-sizing: border-box}
input:focus{box-shadow:0 0 10px #4ef2ff;border-color: #4ef2ff}

/* CLOSE BUTTONS */
.close-modal{position:absolute;top:-20px;left:50%;transform:translateX(-50%);font-size:28px;background:#ff4e4e;border:none;border-radius:50%;width:50px;height:50px;cursor:pointer;color:white;display:flex;align-items:center;justify-content:center;box-shadow:0 0 15px #ff4e4e;z-index:100;transition: all 0.3s;animation:glowPulse 2s infinite}
.close-modal:hover{transform:translateX(-50%) scale(1.2);background:#ff1a1a;box-shadow:0 0 30px #ff4e4e}

/* TOP NAVIGATION */
.top-btn{position:absolute;padding:10px 20px;border-radius:25px;border:none;cursor:pointer;transition:all .3s;font-weight:600}
#login-btn, #logout-btn {top:20px;left:20px;background:#4ef2ff;color:black}
#logout-btn {background:#ffcc00} 
#leaderboard-btn {top:20px;left:185px;background:#a34eff;color:white;box-shadow:0 0 10px #a34eff}
#settings-btn {top:20px;right:20px;background:#ff4e4e;color:white;box-shadow:0 0 10px #ff4e4e}

/* LEADERBOARD TABLE */
table {width:100%; border-collapse: collapse; margin-top: 20px;}
th, td {padding: 15px; text-align: left; border-bottom: 1px solid #222;}
th {color: #4ef2ff; font-weight: 800; text-transform: uppercase; font-size: 12px}
.rank-1 {color: #ffd700; font-weight: 800}

/* CATEGORY BAR */
.category-bar{display:flex;gap:12px;justify-content:center;margin:30px;flex-wrap: wrap}
.cat-btn{padding:10px 20px;border-radius:20px;border:1px solid #333;background:#111;color:white;cursor:pointer;transition:all .3s}
.cat-btn:hover, .cat-active{background:#4ef2ff;color:black;border-color: #4ef2ff;box-shadow: 0 0 15px #4ef2ff}

/* ANIMATIONS */
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes scaleInGlow{0%{transform:scale(0.8);opacity:0;box-shadow:0 0 5px #4ef2ff}60%{transform:scale(1.05);opacity:1;box-shadow:0 0 30px #4ef2ff}100%{transform:scale(1);opacity:1;box-shadow:0 0 20px #4ef2ff}}
@keyframes glowPulse{0%{box-shadow:0 0 10px #ff4e4e}50%{box-shadow:0 0 25px #ff4e4e, 0 0 40px #ff4e4e}100%{box-shadow:0 0 10px #ff4e4e}}

/* STATS LIST */
#game-time-list {list-style: none; padding: 0}
#game-time-list li {background: #1a1a1a; margin-bottom: 8px; padding: 12px; border-radius: 10px; border-left: 4px solid #4ef2ff; display: flex; justify-content: space-between}
</style>
</head>
<body>

<header>
    <img src="{{ url_for('static', filename='logo.png') }}">
    <h1>Gamesplat</h1>
    <p>Play Beyond Reality • The Ultimate Browser Experience</p>

    {% if user %}
    <button class="top-btn" id="logout-btn" onclick="logout()">Logout</button>
    <button class="top-btn" id="settings-btn" onclick="openSettings()">Settings</button>
    {% else %}
    <button class="top-btn" id="login-btn" onclick="openAuth()">Login / Signup</button>
    {% endif %}
    <button class="top-btn" id="leaderboard-btn" onclick="openLeaderboard()">🏆 Leaderboard</button>
</header>

<div class="category-bar">
    <button class="cat-btn cat-active" onclick="filterCategory('all', event)">All Games</button>
    {% for cat in all_cats %}
    <button class="cat-btn" onclick="filterCategory('{{ cat }}', event)">{{ cat }}</button>
    {% endfor %}
</div>

<div class="grid" id="gameGrid">
{% for g in games %}
<div class="card" data-category="{{ (g.categories or g.category)|join(',') }}" onclick="openVote({{ loop.index }})">
    <div class="badge">GAME ID: {{ loop.index }}</div>
    <img src="{{ g.image }}">
    <h3>{{ g.title }}</h3>
    <div class="vote-count" id="vote-{{ loop.index }}">0 👍 / 0 👎</div>
</div>
{% endfor %}
</div>

<div class="modal" id="auth">
    <div class="modal-box">
        <button class="close-modal" onclick="auth.style.display='none'">✕</button>
        <h3>Welcome Back</h3>
        <p style="color: #888; font-size: 13px">Sign in to track your global ranking and playtime.</p>
        <input id="user" placeholder="Username">
        <input id="pass" type="password" placeholder="Password">
        <button onclick="login()" style="background:#4ef2ff; width: 100%; margin-top: 10px">Login</button>
        <button onclick="signup()" style="background:transparent; color: #4ef2ff; border: 1px solid #4ef2ff; width: 100%; margin-top: 10px">Create New Account</button>
    </div>
</div>

<div class="modal" id="leaderboard">
    <div class="modal-box">
        <button class="close-modal" onclick="closeLeaderboard()">✕</button>
        <h3>Global Leaderboard</h3>
        <select id="leaderboard-game" onchange="fetchLeaderboard()">
            <option value="total">Overall Total Playtime</option>
            {% for g in games %}<option value="{{ loop.index }}">{{ g.title }}</option>{% endfor %}
        </select>
        <table>
            <thead><tr><th>Rank</th><th>Player</th><th>Time Spent</th></tr></thead>
            <tbody id="leaderboard-body"></tbody>
        </table>
    </div>
</div>

<div class="modal" id="vote">
    <div class="modal-box">
        <button class="close-modal" onclick="closeVote()">✕</button>
        <h3 id="vtitle"></h3>
        <p id="vdesc" style="color: #aaa; line-height: 1.6"></p>
        <div style="background: #1a1a1a; padding: 15px; border-radius: 15px; margin: 20px 0; display: flex; justify-content: space-around; align-items: center">
            <div><span id="vote-like" style="font-size: 20px; font-weight: 800; color: #4ef2ff">0</span> Likes</div>
            <div><span id="vote-dislike" style="font-size: 20px; font-weight: 800; color: #ff4e4e">0</span> Dislikes</div>
        </div>
        <div style="display: flex; gap: 10px">
            <button class="like" style="flex: 1" onclick="sendVote('like')">👍 Like</button>
            <button class="dislike" style="flex: 1" onclick="sendVote('dislike')">👎 Dislike</button>
        </div>
        <button onclick="play()" style="width: 100%; margin-top: 15px; background: white; color: black; font-size: 18px">PLAY GAME</button>
    </div>
</div>

<div class="modal" id="settings">
    <div class="modal-box">
        <button class="close-modal" onclick="closeSettings()">✕</button>
        <h3>User Settings & Stats</h3>
        <div style="text-align: center; margin: 20px 0">
            <p style="margin: 0; color: #888">Total Combined Playtime</p>
            <h2 id="ptime" style="color: #4ef2ff; font-size: 32px; margin: 5px 0"></h2>
        </div>
        <h4>Individual Game Breakdown:</h4>
        <ul id="game-time-list"></ul>
        <hr style="border: 0; border-top: 1px solid #333; margin: 20px 0">
        <button onclick="resetTime()" style="width: 100%; background: #333; color: white; margin-bottom: 10px">Reset All Stats</button>
        <div style="display: flex; gap: 10px">
            <button onclick="deactivate()" style="flex: 1; background: #ffcc00; color: black">Deactivate</button>
            <button onclick="deleteAcc()" style="flex: 1; background: #ff4e4e; color: white">Delete Account</button>
        </div>
    </div>
</div>

<div class="player" id="player">
    <button class="close-modal" style="top: 30px; left: auto; right: 30px; transform: none; animation: none" onclick="closePlayer()">✕</button>
    <iframe id="frame" allow="fullscreen autoplay"></iframe>
</div>

<script>
// --- TIME SCALING ENGINE ---
function formatTime(seconds) {
    if (seconds < 60) return seconds + " seconds";
    let minutes = seconds / 60;
    if (minutes < 60) return minutes.toFixed(1) + " minutes";
    let hours = minutes / 60;
    if (hours < 24) return hours.toFixed(1) + " hours";
    let days = hours / 24;
    if (days < 7) return days.toFixed(1) + " days";
    let weeks = days / 7;
    if (weeks < 4) return weeks.toFixed(1) + " weeks";
    let months = days / 30.44;
    if (months < 12) return months.toFixed(1) + " months";
    let years = days / 365.25;
    return years.toFixed(1) + " years";
}

const auth=document.getElementById("auth"), vote=document.getElementById("vote"), player=document.getElementById("player"), frame=document.getElementById("frame"), vtitle=document.getElementById("vtitle"), vdesc=document.getElementById("vdesc"), settings=document.getElementById("settings"), ptime=document.getElementById("ptime"), user=document.getElementById("user"), pass=document.getElementById("pass"), voteLike=document.getElementById("vote-like"), voteDislike=document.getElementById("vote-dislike"), gameTimeList=document.getElementById("game-time-list"), leaderboard=document.getElementById("leaderboard"), leaderboardBody=document.getElementById("leaderboard-body");

const games={{ games|tojson }};
let currentGame=null, startTime=null;

function openAuth(){auth.style.display="flex";}
function openSettings(){
    fetch("/me").then(r=>r.json()).then(d=>{
        ptime.innerText = formatTime(d.playtime);
        gameTimeList.innerHTML="";
        for(let g in d.games){
            let gam=games[g-1];
            if(gam) gameTimeList.innerHTML+=`<li><span>${gam.title}</span> <b>${formatTime(d.games[g])}</b></li>`;
        }
        settings.style.display="flex";
    });
}
function fetchLeaderboard(){
    const gameId = document.getElementById("leaderboard-game").value;
    fetch(`/leaderboard_api?game=${gameId}`).then(r=>r.json()).then(data=>{
        leaderboardBody.innerHTML = "";
        data.forEach((entry, index) => {
            leaderboardBody.innerHTML += `<tr><td class="${index==0?'rank-1':''}">#${index+1}</td><td>${entry.u}</td><td>${formatTime(entry.t)}</td></tr>`;
        });
    });
}

function signup(){fetch("/signup",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({u:user.value,p:pass.value})}).then(r=>{if(r.ok)location.reload();else alert("Username taken");});}
function login(){fetch("/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({u:user.value,p:pass.value})}).then(r=>{if(r.ok)location.reload();else alert("Invalid login");});}
function logout(){fetch("/logout").then(()=>location.reload());}
function closeSettings(){settings.style.display="none";}
function openLeaderboard(){leaderboard.style.display="flex"; fetchLeaderboard();}
function closeLeaderboard(){leaderboard.style.display="none";}

function openVote(id){
    currentGame=id; vtitle.textContent=games[id-1].title; vdesc.textContent=games[id-1].description; vote.style.display="flex";
    fetch(`/votes/${id}`).then(r=>r.json()).then(d=>{ voteLike.textContent=d.likes; voteDislike.textContent=d.dislikes; });
}
function closeVote(){vote.style.display="none";currentGame=null;}

function sendVote(type){
    if(!{{ 'true' if user else 'false' }}){ alert("Account required to vote!"); return; }
    fetch("/vote",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:currentGame,v:type})})
    .then(()=>{ fetch(`/votes/${currentGame}`).then(r=>r.json()).then(d=>{
        voteLike.textContent=d.likes; voteDislike.textContent=d.dislikes;
        document.getElementById(`vote-${currentGame}`).textContent=`${d.likes} 👍 / ${d.dislikes} 👎`;
    }); });
}

function play(){vote.style.display="none";player.style.display="flex";frame.src=games[currentGame-1].embed;startTime=Date.now();}
function closePlayer(){
    player.style.display="none"; frame.src="";
    if(startTime){ fetch("/track",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:currentGame,t:Math.floor((Date.now()-startTime)/1000)})}); startTime=null; }
}

function resetTime(){ if(confirm("Reset all stats?")) fetch("/reset_playtime",{method:"POST"}).then(()=>openSettings()); }
function deactivate(){ if(confirm("Log out and hide profile?")) fetch("/deactivate",{method:"POST"}).then(()=>location.reload()); }
function deleteAcc(){ if(confirm("PERMANENTLY DELETE ACCOUNT?")) fetch("/delete",{method:"POST"}).then(()=>location.reload()); }

function filterCategory(cat, event){
    document.querySelectorAll(".cat-btn").forEach(b=>b.classList.remove("cat-active"));
    event.target.classList.add("cat-active");
    document.querySelectorAll("#gameGrid .card").forEach(c=>{
        const cats = c.dataset.category.split(',');
        if(cat=="all" || cats.includes(cat)) c.style.display="block"; else c.style.display="none";
    });
}
</script>
</body>
</html>
"""

# -------------------- SERVER ROUTES (RESTORED) --------------------
@app.route("/")
def index():
    all_cats = set()
    for g in games:
        cats = g.get("categories") or g.get("category") or []
        for c in cats: all_cats.add(c)
    return render_template_string(HTML, games=games, user=session.get("user"), all_cats=sorted(list(all_cats)))

@app.route("/leaderboard_api")
def leaderboard_api():
    game_filter = request.args.get("game", "total")
    users = load_users()["users"]
    lb_data = []
    for username, data in users.items():
        if not data.get("active", True): continue
        time = data.get("playtime", 0) if game_filter == "total" else data.get("games", {}).get(str(game_filter), 0)
        if time > 0: lb_data.append({"u": username, "t": time})
    return jsonify(sorted(lb_data, key=lambda x: x["t"], reverse=True)[:15])

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    users = load_users()
    if data["u"] in users["users"]: abort(400)
    users["users"][data["u"]] = {"password":generate_password_hash(data["p"]),"active":True,"playtime":0,"games":{},"votes":{}}
    save_users(users)
    session["user"] = data["u"]
    return "",204

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = load_users()
    u = users["users"].get(data["u"])
    if not u or not check_password_hash(u["password"],data["p"]): abort(403)
    u["active"]=True # Re-activate on login
    save_users(users)
    session["user"]=data["u"]
    return "",204

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/vote", methods=["POST"])
def vote_route():
    if "user" not in session: abort(403)
    data = request.json
    users = load_users()
    users["users"][session["user"]]["votes"][str(data["id"])] = data["v"]
    save_users(users)
    return "",204

@app.route("/votes/<int:game_id>")
def global_votes(game_id):
    users = load_users()["users"]
    l=d=0
    for u in users.values():
        v = u.get("votes", {}).get(str(game_id))
        if v=="like": l+=1
        elif v=="dislike": d+=1
    return jsonify({"likes":l,"dislikes":d})

@app.route("/track", methods=["POST"])
def track():
    if "user" not in session: return "",204
    d = request.json
    users = load_users()
    if session["user"] not in users["users"]: return "", 204
    u = users["users"][session["user"]]
    u["playtime"] += d["t"]
    u["games"][str(d["id"])] = u["games"].get(str(d["id"]),0)+d["t"]
    save_users(users)
    return "",204

@app.route("/reset_playtime", methods=["POST"])
def reset_playtime():
    if "user" not in session: abort(403)
    users = load_users()
    users["users"][session["user"]]["playtime"]=0
    users["users"][session["user"]]["games"]={}
    save_users(users)
    return "",204

@app.route("/me")
def me():
    if "user" not in session: abort(403)
    return jsonify(load_users()["users"][session["user"]])

@app.route("/deactivate", methods=["POST"])
def deactivate():
    users = load_users()
    users["users"][session["user"]]["active"]=False
    save_users(users)
    session.clear()
    return "",204

@app.route("/delete", methods=["POST"])
def delete():
    users = load_users()
    del users["users"][session["user"]]
    save_users(users)
    session.clear()
    return "",204

if __name__=="__main__":
    app.run(debug=True)