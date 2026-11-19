import os,sqlite3,secrets,random,string,json,re
from flask import Flask,render_template,request,redirect,url_for,session,abort,flash
app=Flask(__name__);app.secret_key=os.getenv('SECRET_KEY','replace-this-secret');DB=os.getenv('DATABASE_PATH','mahkama.db')
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
 c.execute('CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,jkey TEXT,status TEXT,duration INT,assign TEXT,scores TEXT)')
 c.execute('CREATE TABLE IF NOT EXISTS teams(id INTEGER PRIMARY KEY,game INT,slot INT,name TEXT,members TEXT,token TEXT UNIQUE,submitted INT DEFAULT 0,answers TEXT)');c.commit();return c
# 30 classroom-ready fictional/composite investigations; none attributes guilt to a real person.
seed=[
('اختفاء صندوق المزاد','سرقة','اختفى صندوق مقتنيات من غرفة جانبية أثناء مزاد. سجل البطاقة يثبت فتح الباب ببطاقة أمين المخزن، لكنه كان في اجتماع وقتها.','صورة قبل الإغلاق تُظهر الصندوق. البطاقة استُخدمت 8:40. أمين المخزن كان في اجتماع. موظفان يعرفان مكان البطاقة الاحتياطية.'),('الرسالة المجهولة','جريمة رقمية','نُشر ملف سري من حساب مشترك، وسجل النظام يثبت فتح الملف قبل النشر بربع ساعة.','الحساب يستخدمه أربعة أشخاص. أحدهم ترك جهازه مفتوحًا. لا يوجد سجل يحدد الجهاز الذي نشر الملف.'),('حقيبة المحطة','سرقة','اختفت حقيبة من صالة انتظار مزدحمة. شاهد قال إن شخصًا أخذها، وآخر ظن أن موظفًا نقلها للمفقودات.','الكاميرا لا تغطي المقعد. الشاهد الأول لم ير الوجه. مكتب المفقودات لا يملك تسجيلًا كاملًا.'),('الساعة المتوقفة','وفاة غامضة','عُثر على مالك قصر متوفى في مكتبه، وكانت ساعة الحائط متوقفة عند 9:10.','حدث انقطاع كهربائي. الحارس سمع صوتًا ولم ير أحدًا. لا يوجد تقرير يحدد وقت الوفاة.'),('ختم المخزن','اختلاس','نقصت أجهزة من المخزن، ونموذج الصرف يحمل توقيع أمين المخزن الذي كان في إجازة موثقة.','سجل الباب لا يحدد الداخل. التوقيع لم يُفحص فنيًا. موظفان يستطيعان الوصول للنماذج.'),('لوحة الميناء','سرقة فنية','اختفت لوحة أثناء نقلها بين قاعتين. وقع موظفان على الاستلام دون عدّ القطع.','لا توجد صورة لمحتويات العربة. الكاميرا تُظهر العربة فقط. نموذج التسليم غير مكتمل.'),('تذكرة القطار','احتيال','استُخدم رمز تذكرة إلكترونية في محطتين خلال فترة قصيرة.','الرمز قابل للنسخ. لا توجد صورة واضحة للمستخدمين. صاحب التذكرة ينفي السفر.'),('المكالمة الصامتة','تهديد','تلقى مدير رسائل تهديد من رقم افتراضي بعد اجتماع إداري.','المعلومة المذكورة في الرسالة تداولها عدة موظفين. الرقم لا يكشف المستخدم مباشرة.'),('الطرد الذي لم يصل','سرقة شحنة','سجلت شركة الشحن طردًا على أنه سُلّم، لكن المستلم ينفي استلامه.','الصورة لا تظهر رقم الوحدة. التوقيع حرف واحد. مسار السائق تغير بسبب أعمال طريق.'),('الملف المحذوف','تخريب رقمي','اختفى تقرير من خادم المؤسسة، وسجل الدخول باسم موظف سابق.','حساب الموظف ظل فعالًا بالخطأ. الحساب كان محفوظًا على أجهزة مشتركة. التقرير متاح لعدة موظفين.'),('المخطوطة المبدلة','سرقة','أعيدت مخطوطة إلى المكتبة بغلاف مختلف عن صورة الفهرسة.','سجل الصيانة لا يذكر رقم المخطوطة. الكاميرا لا تغطي الرف. أكثر من موظف تعامل معها.'),('الخزنة المفتوحة','سرقة','وجدت خزنة مكتب مفتوحة واختفى ظرف مالي دون آثار كسر.','سجل الخزنة غير مفعل. ثلاثة أشخاص يدخلون المكتب. لا توجد كاميرا داخلية.'),('المركبة المستعارة','سرقة مركبة','اختفت مركبة من موقف فندق ثم ظهرت في موقف قريب.','مفتاح احتياطي لدى خدمة صف السيارات. لوحة المركبة في التسجيل غير واضحة. سجل تسليم المفاتيح ناقص.'),('اللوحة المزيفة','تزوير','اكتشف مزاد أن شهادة أصالة لوحة لا تطابق توقيع الخبير.','البائع تسلم الشهادة من وسيط. لا توجد نسخة أصلية للمقارنة. أكثر من شخص تداول الوثيقة.'),('فاتورة منتصف الليل','احتيال مالي','ظهرت فاتورة كبيرة في حساب شركة بعد منتصف الليل.','النظام كان في وضع تحديث. المورد ينفي إرسالها. الفاتورة بلا توقيع اعتماد.'),('المفتاح المكرر','دخول غير مصرح','دخل شخص إلى مكتب مغلق واختفت وثيقة واحدة دون كسر.','مفتاح احتياطي لم يوثق. فني أقفال زار المبنى قبل يوم. كاميرا الممر معطلة.'),('حقيبة الفندق','سرقة','اختفت حقيبة من غرفة فندق خلال غياب النزيل.','سجل البطاقة يظهر فتح الباب لكن البطاقة مشتركة بين موظفي الخدمة. توقيت الكاميرا متأخر خمس دقائق.'),('الطابع النادر','احتيال','اشترى جامع طابعًا نادرًا ثم اكتشف أن شهادة البيع تخص قطعة أخرى.','رقم الشهادة لا يطابق الكتالوج. لا توجد صورة لحظة التسليم. عدة موظفين تعاملوا مع الطرد.'),('المكالمة المسجلة','ابتزاز','تلقى مسؤول تسجيلًا صوتيًا يطالبه بدفع مال مقابل عدم نشره.','صوته مسجل في اجتماع عام. لا يوجد تحليل صوتي. الرقم مخفي.'),('الوثيقة المختومة','تزوير','ظهرت وثيقة تحمل ختم مؤسسة غير موجود في سجلها.','الختم يبدو مطبوعًا. سجل الزوار ناقص. أكثر من موظف تعامل مع الوثيقة.'),('المستودع الليلي','سرقة','نقصت صناديق من مستودع بعد مناوبة ليلية وخرجت شاحنة.','ميزان البوابة معطل. نموذج الحمولة غير مكتمل. الكاميرا لا تظهر محتويات الشاحنة.'),('المزاد السري','انتحال واحتيال','استُخدم اسم جامع معروف للمزايدة ثم رفض الدفع.','البريد مشابه لعنوانه بحرف واحد. التحقق الإلكتروني ضعيف. عنوان الشبكة عام.'),('الطرد الثقيل','تهريب ممتلكات','أوقف طرد بسبب اختلاف وصف المحتوى بين بوليصة الشحن والسجل.','الوصف أدخله وسيط. الوزن يناسب أنواعًا مختلفة. لا توجد صورة عند الاستلام.'),('المنحة المفقودة','انتحال هوية','اكتشف طالب أن بياناته استُخدمت في طلب منحة آخر.','البريد يختلف بحرف واحد. لا يوجد سجل تعديل. الملفان يحملان بيانات متشابهة.'),('المتحف بعد الإغلاق','دخول غير مصرح','انطلق إنذار المتحف بعد الإغلاق واختفت بطاقة وصف من قاعة.','حساس الإنذار معطل أحيانًا. البطاقة قرب الباب. لا تصوير للممر الخلفي.'),('حساب المدير','انتحال رقمي','أرسل حساب المدير تعليمات تحويل أموال أثناء سفره.','الحساب بلا تحقق ثنائي. الجهاز الجديد غير معروف. البريد أصلي لكن قد يكون مخترقًا.'),('الساعة الأثرية','سرقة','اختفت ساعة من معرض مؤقت ووجد صندوقها فارغًا.','الصندوق غير مختوم. الصور لا تظهر محتواه. سجل نقل القطع غير موقع.'),('رسالة من رقم مجهول','تهديد','وصلت رسالة تهديد لشاهد واشتبه بزميله.','موعد الشهادة معلن. الرقم افتراضي. لا رابط تقني بين المشتبه بهم والرقم.'),('سجل الحضور','تزوير','عُدّل سجل حضور موظف لإظهاره في العمل وقت فقدان جهاز.','حساب المشرف هو المستخدم لكن الجهاز مشترك. لا كاميرا للمدخل. التعديل بعد يومين.'),('الخريطة الممزقة','سرقة','اختفت خريطة من أرشيف ووجدت قصاصة في آلة تصوير.','آلة التصوير مشتركة. القصاصة بلا رقم صفحة. نموذج خروج الوثائق غير موجود.')]
CASES=[]
for i,(title,cat,summary,clues) in enumerate(seed,1):
 CASES.append(dict(id=i,title=title,category=cat,summary=summary,story=summary,clues=clues.split('؛'),suspects=['الموظف المسؤول','صاحب صلاحية الوصول','شخص مجهول'],answer='لا يمكن الجزم بهوية الجاني من الأدلة الحالية',reason='المعطيات تثبت وجود فرصة أو فجوة في الإجراء، لكنها لا تثبت هوية من نفذ الفعل. يجب طلب سجل مستقل أو دليل مباشر قبل توجيه اتهام.',contradictions='الفجوة الأساسية أن السجل أو الشهادة لا يثبتان هوية الشخص الذي نفذ الفعل.',exception='لا تخلطوا بين فرصة الوصول والدليل المباشر على ارتكاب الفعل.'))
def getgame(code):
 c=db();r=c.execute('SELECT * FROM games WHERE code=?',(code,)).fetchone();c.close();return r
def getteam(tok):
 c=db();r=c.execute('SELECT * FROM teams WHERE token=?',(tok,)).fetchone();c.close();return r
def teams(gid):
 c=db();r=c.execute('SELECT * FROM teams WHERE game=? ORDER BY slot',(gid,)).fetchall();c.close();return r
def jfilter(v):
 try:return json.loads(v or '{}')
 except:return {}
app.jinja_env.filters['fromjson']=jfilter
@app.route('/')
def home():return render_template('home.html')
@app.post('/create')
def create():
 code=''.join(random.choices(string.ascii_uppercase+string.digits,k=6));key=secrets.token_urlsafe(24);c=db();gid=c.execute("INSERT INTO games(code,jkey,status,duration,assign,scores) VALUES(?,?,'setup',10,'{}','{}')",(code,key)).lastrowid
 for n in range(1,4):c.execute('INSERT INTO teams(game,slot,name,members,token,answers) VALUES(?,?,?,\'\',?,\'{}\')',(gid,n,'المجموعة '+str(n),secrets.token_urlsafe(20)))
 c.commit();c.close();session['jk']=key;return redirect(url_for('judge',code=code))
@app.route('/judge/<code>')
def judge(code):
 g=getgame(code)
 if not g or session.get('jk')!=g['jkey']:abort(403)
 return render_template('game.html',g=g,judge=True,team=None,teams=teams(g['id']),cases=CASES,assign=jfilter(g['assign']),scores=jfilter(g['scores']))
@app.route('/join/<token>')
def join(token):
 t=getteam(token)
 if not t:abort(404)
 session['tt']=token;c=db();g=c.execute('SELECT code FROM games WHERE id=?',(t['game'],)).fetchone();c.close();return redirect(url_for('play',code=g['code']))
@app.route('/play/<code>')
def play(code):
 g=getgame(code);t=getteam(session.get('tt',''))
 if not g or not t or t['game']!=g['id']:abort(403)
 return render_template('game.html',g=g,judge=False,team=t,teams=[],cases=CASES,assign=jfilter(g['assign']),scores={})
@app.post('/team/<code>')
def teamdata(code):
 g=getgame(code);t=getteam(session.get('tt',''))
 if not g or not t or t['game']!=g['id']:abort(403)
 c=db();c.execute('UPDATE teams SET name=?,members=? WHERE id=?',(request.form.get('name','')[:50],request.form.get('members','')[:1000],t['id']));c.commit();c.close();return redirect(url_for('play',code=code))
@app.post('/setup/<code>')
def setup(code):
 g=getgame(code)
 if not g or session.get('jk')!=g['jkey']:abort(403)
 ids=request.form.getlist('ids')
 if len(ids)!=3:flash('اختر ثلاث قضايا بالضبط');return redirect(url_for('judge',code=code))
 if request.form.get('random'):random.shuffle(ids)
 assign={str(i+1):int(ids[i]) for i in range(3)};c=db();c.execute("UPDATE games SET status='investigation',duration=?,assign=? WHERE id=?",(max(3,min(60,int(request.form.get('duration',10)))),json.dumps(assign),g['id']));c.commit();c.close();return redirect(url_for('judge',code=code))
@app.post('/submit/<code>')
def submit(code):
 g=getgame(code);t=getteam(session.get('tt',''))
 if not g or not t or t['game']!=g['id']:abort(403)
 a={k:request.form.get(k,'')[:4000] for k in ['suspect','reason','contradictions','exception','opposition']};c=db();c.execute('UPDATE teams SET answers=?,submitted=1 WHERE id=?',(json.dumps(a,ensure_ascii=False),t['id']));c.commit();c.close();flash('تم تسليم الإجابة للمقدم');return redirect(url_for('play',code=code))
@app.post('/status/<code>')
def status(code):
 g=getgame(code)
 if not g or session.get('jk')!=g['jkey']:abort(403)
 s=request.form.get('status')
 if s not in ['investigation','discussion','scoring','finished']:abort(400)
 c=db();c.execute('UPDATE games SET status=? WHERE id=?',(s,g['id']));c.commit();c.close();return redirect(url_for('judge',code=code))
def similarity(a,b):
 A=set(re.findall(r'[\w\u0600-\u06ff]{3,}',(a or '').lower()));B=set(re.findall(r'[\w\u0600-\u06ff]{3,}',(b or '').lower()));return round(100*len(A&B)/len(A|B)) if A|B else 0
@app.post('/score/<code>')
def score(code):
 g=getgame(code)
 if not g or session.get('jk')!=g['jkey']:abort(403)
 ass=jfilter(g['assign']);out={};c=db()
 for t in c.execute('SELECT * FROM teams WHERE game=?',(g['id'],)).fetchall():
  ca=CASES[ass[str(t['slot'])]-1];a=jfilter(t['answers']);vals={}
  for k,m in [('suspect',10),('reason',30),('contradictions',15),('exception',5),('delivery',20),('debate',20)]:
   try:vals[k]=max(0,min(m,float(request.form.get(f"{t['id']}_{k}",0))))
   except:vals[k]=0
  auto={k:similarity(a.get(k,''),v) for k,v in [('suspect',ca['answer']),('reason',ca['reason']),('contradictions',ca['contradictions']),('exception',ca['exception'])]};out[str(t['slot'])]={'name':t['name'],'answers':a,'auto':auto,'scores':vals,'total':sum(vals.values())}
 c.execute('UPDATE games SET scores=? WHERE id=?',(json.dumps(out,ensure_ascii=False),g['id']));c.commit();c.close();flash('تم حفظ الدرجات');return redirect(url_for('judge',code=code))
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.getenv('PORT',5000)))
