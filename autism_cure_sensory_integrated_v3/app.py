import os, sqlite3, json, secrets
from datetime import datetime, timedelta, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app=Flask(__name__); app.secret_key=os.environ.get('SECRET_KEY',secrets.token_hex(32))
DB=os.environ.get('DATABASE_PATH',os.path.join(os.path.dirname(__file__),'autism_cure.db'))
ADMIN_USER=os.environ.get('ADMIN_USERNAME','admin'); ADMIN_PASS=os.environ.get('ADMIN_PASSWORD','CHANGE_ME_NOW')
NAYAPAY_NAME='Muhammad Raffy Umer'; NAYAPAY_NUMBER='03250150477'; MONTHLY_PRICE=799

ACTIVITIES=[
('Communication','Picture Choice','Choose between two options and communicate your choice.','🖼️'),('Communication','Request Practice','Practice asking for an item using speech, gesture, sign or picture.','💬'),('Communication','Yes / No','Practice answering simple yes/no questions.','✅'),
('Attention','Find & Tap','Find the requested object from a small set.','🔎'),('Cognitive','Memory Match','Match pairs and build working memory.','🧩'),('Cognitive','Sort It','Sort everyday objects into simple categories.','🗂️'),
('Social','Emotion Match','Match an emotion to a face or situation.','🙂'),('Social','Turn Taking','Practice “my turn / your turn” with a caregiver.','🤝'),('Social','Social Story','Read a short visual story about a common situation.','📖'),
('Daily Living','Hand Washing','Practice the visual sequence for hand washing.','🧼'),('Daily Living','Getting Dressed','Practice a simple dressing sequence.','👕'),('Daily Living','Tooth Brushing','Follow a visual tooth-brushing routine.','🪥'),
('Fine Motor','Trace Shapes','Trace lines and simple shapes.','✏️'),('Motor','Movement Break','Do a short, safe movement break.','🏃'),('Regulation','Calm Corner','Identify a feeling and choose a calming strategy.','🌿'),('Sensory','Sensory Choice','Identify preferred/overwhelming sensory inputs.','🎧')]

SENSORY_EXERCISES=[
('Regulation','Bubble Breathing','🌬️','2–3 min','Slow breathing with a visual bubble pace.','Sit comfortably. Breathe in gently through the nose, then breathe out slowly as if making a bubble. Repeat 5–8 times.','Most ages','Stop if breathing feels uncomfortable; never force breath-holding.'),
('Proprioception','Wall Push','🧱','1–2 min','Gentle pushing for body awareness and a movement break.','Stand facing a wall. Place both hands on it and gently push for 5 seconds, relax for 5 seconds. Repeat 5 times.','3+','Use a stable wall and comfortable effort; stop if pain occurs.'),
('Proprioception','Carry & Place','📦','3–5 min','Move light objects between two safe locations.','Choose 3–5 light objects. Carry one at a time from a start point to a basket, then return. Repeat at an easy pace.','3+','Use only light, safe objects and adult supervision for young children.'),
('Tactile','Texture Detective','🖐️','3–5 min','Explore different safe textures at the child’s pace.','Offer 3–4 familiar textures such as a soft cloth, smooth spoon, sponge and textured ball. Touch or look at each and choose “like”, “not sure” or “no”.','2+','Never force touching. Avoid known allergens, sharp items and extreme temperatures.'),
('Tactile','Hand Squeeze & Release','🤲','1–2 min','Gentle hand movement and release practice.','Squeeze a soft foam ball or folded towel gently for 3 seconds, then release for 3 seconds. Repeat 6–8 times.','3+','Use a soft item; avoid hard squeezing or painful pressure.'),
('Movement','Animal Walk Break','🐻','2–4 min','Short playful whole-body movement.','Choose 1–2 easy movements: bear walk, penguin steps or slow marching. Do 20–30 seconds, rest, then repeat 2–3 times.','3+','Clear the floor and choose movements the child can do safely.'),
('Balance','Line Walk','⚖️','2–3 min','Slow walking along a visible line for balance and body awareness.','Place a strip of tape on the floor. Walk heel-to-toe or normally along the line. Repeat 3 times at a comfortable speed.','3+','Use a non-slip surface and stay beside the child when needed.'),
('Visual','Slow Follow','👀','2–3 min','Follow a slow moving object with the eyes.','Move a bright but comfortable object slowly left/right and up/down. Ask the child to follow it with their eyes without moving the head if comfortable.','2+','Keep the object at a comfortable distance and stop if eye strain or discomfort occurs.'),
('Auditory','Sound Pause','🔇','2–5 min','Practice noticing sound level and choosing a quieter space.','Play or notice a normal household sound briefly. Ask: “comfortable or too much?” Then move to a quieter area and compare.','Most ages','Do not deliberately expose someone to loud or distressing sounds.'),
('Visual + Regulation','Calm Look & Count','🔵','2–3 min','Simple visual focus with counting.','Choose one calm object or picture. Look at it and slowly count 1–5, then name one thing you notice. Repeat 3 times.','2+','Use a calm, non-flashing visual.'),
('Regulation','Choice-Based Calm Break','🌿','3–5 min','Child-led choice of a calming activity.','Offer two safe choices: quiet corner, slow breathing, gentle stretching or looking at a favorite picture. Let the child choose and stop whenever they want.','Most ages','Follow the child’s cues; the goal is comfort, not compliance.'),
('Movement','Reach & Stretch','🙆','2–3 min','Gentle reaching and stretching to reset after sitting.','Reach both hands up, lower slowly, reach side-to-side, then roll shoulders gently. Repeat 3–5 times.','3+','Keep movements gentle and within a comfortable range.')
]

SCHEMA='''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,phone TEXT UNIQUE NOT NULL,password TEXT NOT NULL,language TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS patients(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,name TEXT NOT NULL,dob TEXT,age INTEGER,support_level TEXT,diagnosis_status TEXT,communication_level TEXT,sensory_notes TEXT,strengths TEXT,goals TEXT,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS activities(id INTEGER PRIMARY KEY AUTOINCREMENT,domain TEXT,title TEXT,description TEXT,icon TEXT);
CREATE TABLE IF NOT EXISTS activity_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,activity_id INTEGER,score REAL DEFAULT 0,duration INTEGER DEFAULT 0,status TEXT,note TEXT,logged_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS routines(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,routine_date TEXT,morning TEXT,afternoon TEXT,evening TEXT,completed INTEGER DEFAULT 0,note TEXT,UNIQUE(patient_id,routine_date));
CREATE TABLE IF NOT EXISTS food_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,log_date TEXT,meals TEXT,appetite TEXT,water TEXT,note TEXT);
CREATE TABLE IF NOT EXISTS exercise_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,log_date TEXT,activity TEXT,minutes INTEGER,completed INTEGER DEFAULT 0,note TEXT);
CREATE TABLE IF NOT EXISTS wellbeing_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,log_date TEXT,mood TEXT,energy TEXT,sleep_hours REAL,stress TEXT,note TEXT);
CREATE TABLE IF NOT EXISTS sensory_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,log_date TEXT,trigger_text TEXT,intensity TEXT,strategy TEXT,outcome TEXT);
CREATE TABLE IF NOT EXISTS sensory_exercise_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,exercise_name TEXT,category TEXT,minutes INTEGER,comfort TEXT,note TEXT,log_date TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,title TEXT,domain TEXT,baseline REAL DEFAULT 0,target REAL DEFAULT 100,current REAL DEFAULT 0,status TEXT DEFAULT 'active',created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS subscriptions(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,start_date TEXT,end_date TEXT,status TEXT,source TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,trx_id TEXT,amount REAL,status TEXT DEFAULT 'pending',submitted_at TEXT,reviewed_at TEXT,admin_note TEXT);
CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,week_start TEXT,week_end TEXT,summary TEXT,pdf_path TEXT,created_at TEXT,UNIQUE(patient_id,week_start));
CREATE TABLE IF NOT EXISTS appointments(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,appt_date TEXT,provider TEXT,purpose TEXT,note TEXT);
CREATE TABLE IF NOT EXISTS safety_plans(id INTEGER PRIMARY KEY AUTOINCREMENT,patient_id INTEGER,calm_steps TEXT,contacts TEXT,notes TEXT);
'''
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
 c=db(); c.executescript(SCHEMA)
 if c.execute('SELECT COUNT(*) n FROM activities').fetchone()['n']==0: c.executemany('INSERT INTO activities(domain,title,description,icon) VALUES(?,?,?,?)',ACTIVITIES)
 c.commit(); c.close()
init_db()

def user():
 if not session.get('uid'): return None
 c=db(); u=c.execute('SELECT * FROM users WHERE id=?',(session['uid'],)).fetchone(); c.close(); return u
def trial(uid):
 c=db(); u=c.execute('SELECT created_at FROM users WHERE id=?',(uid,)).fetchone(); c.close()
 return bool(u and datetime.fromisoformat(u['created_at'])+timedelta(days=30)>=datetime.now())
def sub(uid):
 c=db(); s=c.execute("SELECT * FROM subscriptions WHERE user_id=? AND status='active' AND date(end_date)>=date('now') ORDER BY end_date DESC LIMIT 1",(uid,)).fetchone(); c.close(); return s
def access(uid): return trial(uid) or bool(sub(uid))
def req(f):
 @wraps(f)
 def w(*a,**k):
  if not user(): return redirect(url_for('login'))
  return f(*a,**k)
 return w
def active(f):
 @wraps(f)
 def w(*a,**k):
  if not user(): return redirect(url_for('login'))
  if not access(session['uid']): flash('Free 30-day period khatam ho gaya. Monthly plan activate karein.','warning'); return redirect(url_for('subscribe'))
  return f(*a,**k)
 return w
def patient(pid):
 c=db(); p=c.execute('SELECT * FROM patients WHERE id=? AND user_id=?',(pid,session['uid'])).fetchone(); c.close(); return p
@app.context_processor
def ctx():
 u=user(); return {'me':u,'access':access(u['id']) if u else False,'trial':trial(u['id']) if u else False,'sub':sub(u['id']) if u else None,'price':MONTHLY_PRICE}

@app.route('/')
def home(): return redirect(url_for('dashboard')) if user() else render_template('landing.html')
@app.route('/register',methods=['GET','POST'])
def register():
 if request.method=='POST':
  f=request.form; name=f.get('name','').strip(); email=f.get('email','').strip().lower(); phone=f.get('phone','').strip(); pw=f.get('password',''); lang=f.get('language','English')
  if not name or not email or not phone or len(pw)<8: flash('Complete details dein. Password minimum 8 characters.','danger'); return render_template('register.html')
  c=db()
  try: c.execute('INSERT INTO users(name,email,phone,password,language,created_at) VALUES(?,?,?,?,?,?)',(name,email,phone,generate_password_hash(pw),lang,datetime.now().isoformat())); c.commit(); uid=c.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone()['id']; session['uid']=uid
  except sqlite3.IntegrityError: c.close(); flash('Email ya phone already registered hai.','danger'); return render_template('register.html')
  c.close(); return redirect(url_for('setup'))
 return render_template('register.html')
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  ident=request.form.get('identity','').strip().lower(); pw=request.form.get('password',''); c=db(); u=c.execute('SELECT * FROM users WHERE lower(email)=? OR phone=?',(ident,ident)).fetchone(); c.close()
  if u and check_password_hash(u['password'],pw): session['uid']=u['id']; return redirect(url_for('dashboard'))
  flash('Login details ghalat hain.','danger')
 return render_template('login.html')
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('home'))
@app.route('/setup',methods=['GET','POST'])
@req
def setup():
 if request.method=='POST':
  f=request.form; c=db(); c.execute('INSERT INTO patients(user_id,name,dob,age,support_level,diagnosis_status,communication_level,sensory_notes,strengths,goals,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(session['uid'],f['patient_name'],f.get('dob'),f.get('age') or None,f.get('support_level'),f.get('diagnosis_status'),f.get('communication_level'),f.get('sensory_notes'),f.get('strengths'),f.get('goals'),datetime.now().isoformat())); pid=c.execute('SELECT last_insert_rowid() id').fetchone()['id']; c.execute('INSERT OR IGNORE INTO routines(patient_id,routine_date,morning,afternoon,evening) VALUES(?,?,?,?,?)',(pid,date.today().isoformat(),'Wake • Hygiene • Breakfast','Learning • Movement • Lunch','Social • Calm • Dinner')); c.commit(); c.close(); return redirect(url_for('dashboard'))
 return render_template('setup.html')
@app.route('/dashboard')
@active
def dashboard():
 c=db(); ps=c.execute('SELECT * FROM patients WHERE user_id=? ORDER BY id',(session['uid'],)).fetchall(); stats=[]
 for p in ps:
  n=c.execute("SELECT COUNT(*) n FROM activity_logs WHERE patient_id=? AND date(logged_at)>=date('now','-6 day')",(p['id'],)).fetchone()['n']; avg=c.execute("SELECT COALESCE(AVG(score),0) a FROM activity_logs WHERE patient_id=? AND date(logged_at)>=date('now','-6 day')",(p['id'],)).fetchone()['a']; stats.append((p,n,round(avg,1)))
 c.close(); return render_template('dashboard.html',stats=stats)
@app.route('/patient/<int:pid>')
@active
def profile(pid):
 p=patient(pid)
 if not p:return redirect(url_for('dashboard'))
 c=db(); goals=c.execute('SELECT * FROM goals WHERE patient_id=?',(pid,)).fetchall(); logs=c.execute("SELECT a.title,l.score,l.status,l.logged_at FROM activity_logs l JOIN activities a ON a.id=l.activity_id WHERE l.patient_id=? ORDER BY l.id DESC LIMIT 8",(pid,)).fetchall(); c.close(); return render_template('patient.html',p=p,goals=goals,logs=logs)
@app.route('/communication/<int:pid>')
@active
def communication(pid):
 p=patient(pid)
 if not p:return redirect(url_for('dashboard'))
 return render_template('communication.html',p=p)
@app.route('/activities/<int:pid>')
@active
def activities(pid):
 p=patient(pid); c=db(); acts=c.execute('SELECT * FROM activities ORDER BY domain,id').fetchall(); c.close(); return render_template('activities.html',p=p,acts=acts)
@app.route('/activity/log',methods=['POST'])
@active
def activity_log():
 f=request.form; pid=int(f['patient_id']); aid=int(f['activity_id']);
 if not patient(pid): return jsonify(ok=False),403
 c=db(); c.execute('INSERT INTO activity_logs(patient_id,activity_id,score,duration,status,note,logged_at) VALUES(?,?,?,?,?,?,?)',(pid,aid,float(f.get('score',0)),int(f.get('duration',0)),f.get('status','completed'),f.get('note',''),datetime.now().isoformat())); c.commit(); c.close(); return jsonify(ok=True)
@app.route('/routine/<int:pid>',methods=['GET','POST'])
@active
def routine(pid):
 p=patient(pid); c=db(); rd=date.today().isoformat()
 if request.method=='POST':
  f=request.form; c.execute('INSERT INTO routines(patient_id,routine_date,morning,afternoon,evening,completed,note) VALUES(?,?,?,?,?,?,?) ON CONFLICT(patient_id,routine_date) DO UPDATE SET morning=excluded.morning,afternoon=excluded.afternoon,evening=excluded.evening,completed=excluded.completed,note=excluded.note',(pid,rd,f.get('morning'),f.get('afternoon'),f.get('evening'),int(f.get('completed',0)),f.get('note',''))); c.commit()
 r=c.execute('SELECT * FROM routines WHERE patient_id=? AND routine_date=?',(pid,rd)).fetchone(); c.close(); return render_template('routine.html',p=p,r=r)
@app.route('/food/<int:pid>',methods=['GET','POST'])
@active
def food(pid):
 p=patient(pid); c=db()
 if request.method=='POST': c.execute('INSERT INTO food_logs(patient_id,log_date,meals,appetite,water,note) VALUES(?,?,?,?,?,?)',(pid,date.today().isoformat(),request.form.get('meals'),request.form.get('appetite'),request.form.get('water'),request.form.get('note'))); c.commit()
 rows=c.execute('SELECT * FROM food_logs WHERE patient_id=? ORDER BY id DESC LIMIT 10',(pid,)).fetchall(); c.close(); return render_template('food.html',p=p,rows=rows)
@app.route('/exercise/<int:pid>',methods=['GET','POST'])
@active
def exercise(pid):
 p=patient(pid); c=db()
 if request.method=='POST': c.execute('INSERT INTO exercise_logs(patient_id,log_date,activity,minutes,completed,note) VALUES(?,?,?,?,?,?)',(pid,date.today().isoformat(),request.form.get('activity'),int(request.form.get('minutes') or 0),int(request.form.get('completed',0)),request.form.get('note'))); c.commit()
 rows=c.execute('SELECT * FROM exercise_logs WHERE patient_id=? ORDER BY id DESC LIMIT 10',(pid,)).fetchall(); c.close(); return render_template('exercise.html',p=p,rows=rows)
@app.route('/wellbeing/<int:pid>',methods=['GET','POST'])
@active
def wellbeing(pid):
 p=patient(pid); c=db()
 if request.method=='POST': c.execute('INSERT INTO wellbeing_logs(patient_id,log_date,mood,energy,sleep_hours,stress,note) VALUES(?,?,?,?,?,?,?)',(pid,date.today().isoformat(),request.form.get('mood'),request.form.get('energy'),float(request.form.get('sleep_hours') or 0),request.form.get('stress'),request.form.get('note'))); c.commit()
 rows=c.execute('SELECT * FROM wellbeing_logs WHERE patient_id=? ORDER BY id DESC LIMIT 14',(pid,)).fetchall(); c.close(); return render_template('wellbeing.html',p=p,rows=rows)
@app.route('/sensory/<int:pid>',methods=['GET','POST'])
@active
def sensory(pid):
 p=patient(pid); c=db()
 if request.method=='POST': c.execute('INSERT INTO sensory_logs(patient_id,log_date,trigger_text,intensity,strategy,outcome) VALUES(?,?,?,?,?,?)',(pid,date.today().isoformat(),request.form.get('trigger_text'),request.form.get('intensity'),request.form.get('strategy'),request.form.get('outcome'))); c.commit()
 rows=c.execute('SELECT * FROM sensory_logs WHERE patient_id=? ORDER BY id DESC LIMIT 12',(pid,)).fetchall()
 ex_rows=c.execute('SELECT * FROM sensory_exercise_logs WHERE patient_id=? ORDER BY id DESC LIMIT 12',(pid,)).fetchall()
 c.close(); return render_template('sensory.html',p=p,rows=rows,exercises=SENSORY_EXERCISES,ex_rows=ex_rows)
@app.route('/sensory-exercises/<int:pid>',methods=['GET','POST'])
@active
def sensory_exercises(pid):
 p=patient(pid)
 if not p:return redirect(url_for('dashboard'))
 c=db()
 if request.method=='POST':
  try: minutes=max(1,min(60,int(request.form.get('minutes') or 3)))
  except ValueError: minutes=3
  c.execute('INSERT INTO sensory_exercise_logs(patient_id,exercise_name,category,minutes,comfort,note,log_date,created_at) VALUES(?,?,?,?,?,?,?,?)',(pid,request.form.get('exercise_name'),request.form.get('category'),minutes,request.form.get('comfort'),request.form.get('note'),date.today().isoformat(),datetime.now().isoformat()))
  c.commit(); flash('Sensory exercise session save ho gaya.','success')
 rows=c.execute('SELECT * FROM sensory_exercise_logs WHERE patient_id=? ORDER BY id DESC LIMIT 12',(pid,)).fetchall(); c.close()
 return render_template('sensory_exercises.html',p=p,exercises=SENSORY_EXERCISES,rows=rows)

@app.route('/goals/<int:pid>',methods=['GET','POST'])
@active
def goals(pid):
 p=patient(pid); c=db()
 if request.method=='POST': c.execute('INSERT INTO goals(patient_id,title,domain,baseline,target,current,created_at) VALUES(?,?,?,?,?,?,?)',(pid,request.form.get('title'),request.form.get('domain'),float(request.form.get('baseline') or 0),float(request.form.get('target') or 100),float(request.form.get('current') or 0),datetime.now().isoformat())); c.commit()
 gs=c.execute('SELECT * FROM goals WHERE patient_id=? ORDER BY id DESC',(pid,)).fetchall(); c.close(); return render_template('goals.html',p=p,goals=gs)
@app.route('/appointments/<int:pid>',methods=['GET','POST'])
@active
def appointments(pid):
 p=patient(pid); c=db()
 if request.method=='POST': c.execute('INSERT INTO appointments(patient_id,appt_date,provider,purpose,note) VALUES(?,?,?,?,?)',(pid,request.form.get('appt_date'),request.form.get('provider'),request.form.get('purpose'),request.form.get('note'))); c.commit()
 rows=c.execute('SELECT * FROM appointments WHERE patient_id=? ORDER BY appt_date DESC',(pid,)).fetchall(); c.close(); return render_template('appointments.html',p=p,rows=rows)
@app.route('/safety/<int:pid>',methods=['GET','POST'])
@active
def safety(pid):
 p=patient(pid); c=db(); s=c.execute('SELECT * FROM safety_plans WHERE patient_id=?',(pid,)).fetchone()
 if request.method=='POST':
  f=request.form; c.execute('INSERT INTO safety_plans(patient_id,calm_steps,contacts,notes) VALUES(?,?,?,?) ON CONFLICT(patient_id) DO UPDATE SET calm_steps=excluded.calm_steps,contacts=excluded.contacts,notes=excluded.notes',(pid,f.get('calm_steps'),f.get('contacts'),f.get('notes'))); c.commit(); s=c.execute('SELECT * FROM safety_plans WHERE patient_id=?',(pid,)).fetchone()
 c.close(); return render_template('safety.html',p=p,s=s)
@app.route('/report/<int:pid>')
@active
def report(pid):
 p=patient(pid); c=db(); logs=c.execute("SELECT a.domain,a.title,l.score,l.status,l.logged_at FROM activity_logs l JOIN activities a ON a.id=l.activity_id WHERE l.patient_id=? AND date(l.logged_at)>=date('now','-6 day') ORDER BY l.id DESC",(pid,)).fetchall(); wb=c.execute("SELECT * FROM wellbeing_logs WHERE patient_id=? AND date(log_date)>=date('now','-6 day')",(pid,)).fetchall(); ex=c.execute("SELECT COALESCE(SUM(minutes),0) m FROM exercise_logs WHERE patient_id=? AND date(log_date)>=date('now','-6 day')",(pid,)).fetchone()['m']; sensory_minutes=c.execute("SELECT COALESCE(SUM(minutes),0) m FROM sensory_exercise_logs WHERE patient_id=? AND date(log_date)>=date('now','-6 day')",(pid,)).fetchone()['m']; sensory_sessions=c.execute("SELECT COUNT(*) n FROM sensory_exercise_logs WHERE patient_id=? AND date(log_date)>=date('now','-6 day')",(pid,)).fetchone()['n']; goals=c.execute('SELECT * FROM goals WHERE patient_id=?',(pid,)).fetchall(); c.close(); avg=round(sum(x['score'] for x in logs)/len(logs),1) if logs else 0; return render_template('report.html',p=p,logs=logs,wb=wb,exercise=ex,sensory_minutes=sensory_minutes,sensory_sessions=sensory_sessions,goals=goals,avg=avg)
@app.route('/report/<int:pid>/pdf')
@active
def report_pdf(pid):
 p=patient(pid); c=db(); logs=c.execute("SELECT a.title,l.score,l.status,l.logged_at FROM activity_logs l JOIN activities a ON a.id=l.activity_id WHERE l.patient_id=? AND date(l.logged_at)>=date('now','-6 day') ORDER BY l.id DESC",(pid,)).fetchall(); c.close(); path=os.path.join('/tmp',f'autism_report_{pid}.pdf'); pdf=canvas.Canvas(path,pagesize=A4); y=800; pdf.setFont('Helvetica-Bold',18); pdf.drawString(50,y,'Autism Cure — Weekly Practice Report'); y-=35; pdf.setFont('Helvetica',11); pdf.drawString(50,y,f'Patient: {p["name"]}'); y-=18; pdf.drawString(50,y,f'Generated: {date.today().isoformat()}'); y-=28; pdf.drawString(50,y,'This is a practice/progress summary, not a medical diagnosis.'); y-=30
 for l in logs[:25]:
  pdf.drawString(55,y,f'{l["title"]}: score {l["score"]:.0f} — {l["status"]}'); y-=17
  if y<60: pdf.showPage(); y=800
 pdf.save(); return send_file(path,as_attachment=True,download_name='autism_cure_weekly_report.pdf')
@app.route('/subscribe',methods=['GET','POST'])
@req
def subscribe():
 if request.method=='POST':
  trx=request.form.get('trx_id','').strip(); amount=float(request.form.get('amount') or 0)
  if not trx or amount<MONTHLY_PRICE: flash('Valid TRX ID aur 799 PKR payment required hai.','danger')
  else:
   c=db(); c.execute('INSERT INTO payments(user_id,trx_id,amount,submitted_at) VALUES(?,?,?,?)',(session['uid'],trx,amount,datetime.now().isoformat())); c.commit(); c.close(); flash('Payment request admin ko bhej di gayi hai. Approval ke baad access active hoga.','success'); return redirect(url_for('dashboard'))
 return render_template('subscribe.html',nayapay_name=NAYAPAY_NAME,nayapay_number=NAYAPAY_NUMBER)
@app.route('/ai',methods=['GET','POST'])
@active
def ai():
 answer=None
 if request.method=='POST':
  q=request.form.get('question','').lower()
  if any(x in q for x in ['medicine','medication','dawai','dose','tablet']): answer='Main medicine prescribe ya dose suggest nahi kar sakta. Medication ke liye qualified doctor/clinician se consult karein.'
  elif any(x in q for x in ['cure','theek','recovery']): answer='Autism ke liye guaranteed cure ka claim safe nahi hai. App ka focus communication, daily living, social, regulation aur functional skills ki practice aur progress par hai.'
  elif 'payment' in q or '799' in q: answer='Monthly plan PKR 799 hai. NayaPay par payment bhej kar TRX ID submit karein; admin approval ke baad access activate hoga.'
  elif 'routine' in q: answer='Short, predictable routine use karein: visual schedule, 5–15 minute practice blocks, movement breaks, aur preferred interests ko learning mein include karein.'
  elif 'sensory' in q: answer='Sensory trigger note karein, intensity track karein, environment ko calm karein aur individual preference ke mutabiq break/quiet space/protective strategy use karein.'
  else: answer='Aap app, activities, communication practice, daily living, sensory support, routine, food/exercise tracking ya progress reports ke bare mein pooch sakte hain.'
 return render_template('ai.html',answer=answer)
@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
 if request.method=='POST' and request.form.get('username')==ADMIN_USER and request.form.get('password')==ADMIN_PASS: session['admin']=True; return redirect(url_for('admin'))
 if request.method=='POST': flash('Invalid admin credentials','danger')
 return render_template('admin_login.html')
@app.route('/admin')
def admin():
 if not session.get('admin'): return redirect(url_for('admin_login'))
 c=db(); payments=c.execute('SELECT p.*,u.name,u.email FROM payments p JOIN users u ON u.id=p.user_id ORDER BY p.id DESC').fetchall(); users=c.execute('SELECT COUNT(*) n FROM users').fetchone()['n']; patients=c.execute('SELECT COUNT(*) n FROM patients').fetchone()['n']; c.close(); return render_template('admin.html',payments=payments,users=users,patients=patients)
@app.route('/admin/payment/<int:pid>/<action>',methods=['POST'])
def admin_payment(pid,action):
 if not session.get('admin'): return jsonify(ok=False),403
 c=db(); pay=c.execute('SELECT * FROM payments WHERE id=?',(pid,)).fetchone()
 if not pay:return jsonify(ok=False),404
 if action=='approve':
  start=date.today(); s=c.execute("SELECT * FROM subscriptions WHERE user_id=? AND status='active' AND date(end_date)>=date('now') ORDER BY end_date DESC LIMIT 1",(pay['user_id'],)).fetchone(); end=(date.fromisoformat(s['end_date'])+timedelta(days=30)) if s else (start+timedelta(days=30)); c.execute('INSERT INTO subscriptions(user_id,start_date,end_date,status,source,created_at) VALUES(?,?,?,?,?,?)',(pay['user_id'],start.isoformat(),end.isoformat(),'active','NayaPay',datetime.now().isoformat())); c.execute("UPDATE payments SET status='approved',reviewed_at=? WHERE id=?",(datetime.now().isoformat(),pid))
 else: c.execute("UPDATE payments SET status='rejected',reviewed_at=? WHERE id=?",(datetime.now().isoformat(),pid))
 c.commit(); c.close(); return jsonify(ok=True)
@app.route('/health')
def health(): return {'status':'ok','app':'Autism Cure'}
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
