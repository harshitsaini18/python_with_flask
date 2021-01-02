from flask import Flask,render_template,request, session,redirect
import mysql.connector
import json 
from werkzeug.utils import secure_filename
import math
from datetime import datetime
import os
 
with open("config.json","r") as c:
	params=json.load(c)["params"]
app=Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER']=params["file_path"]
#app.config.update(
#MAIL_SERVER="smtp.gmail.com",
#MAIL_PORT=535,
#MAIL_USERNAME=params["mail_user"],
#MAIL_PASSWORD=params["mail_password"],
#MAIL_USE_SSL=True 
#)
#mail=Mail(app)

mydb=mysql.connector.connect(
host=params["host"] ,
user=params["user"],
password=params["password"],
database=params["database"]
)
cur=mydb.cursor()

def Contact(Value):
	s="INSERT INTO Contact (Name, Email, Phone_no, Msg) VALUE (%s,%s,%s,%s)"
	cur.execute(s, Value)
	
def Add_post(Value):
	s="INSERT INTO Posts(Title, Content, Slug,Date,Img_file,Titletag) VALUE (%s,%s,%s,%s,%s,%s)"
	cur.execute(s, Value)

def Edit_post(Value):
	s="UPDATE Posts SET Title= %s, Content=%s, Slug=%s, Img_file=%s, Titletag=%s WHERE Sno=%s"
	cur.execute(s,Value)

def Delete (num):
	s="DELETE FROM Posts WHERE Sno=%s"
	cur.execute(s,num)
	
def Post():
	s="SELECT *from Posts"
	cur.execute(s)	
	record=cur.fetchall()
	return record
	
#Home page
@app.route("/", methods=["GET","POST"])
def home():
	posts=Post()
	last=math.floor(len(posts)/params["no_of_post"])+1
	page=request.args.get("page")
	if (not str(page).isnumeric()):
		page=1
	page=int(page)	
	posts=Post()[(int(page)-1)*params["no_of_post"]: int(page)*params["no_of_post"]]	
		
	if page==1:
		nxt ="/?page="+ str(page+1)
		prev ="#"
	elif page==last:
		prev ="/?page="+ str(page-1)
		nxt ="#"
	else:
		nxt ="/?page="+ str(page+1)
		prev ="/?page="+ str(page-1)
	
	return render_template("index.html",params=params,posts=posts,nxt=nxt,prev=prev) 

#Posts page
@app.route("/post/<string:post_slug>", methods=["GET"])
def post_data(post_slug):
	record=Post()
	for item in record:
		if post_slug==item[3]:
			post=item	
	return render_template("post.html",post=post,params=params)

#About page	
@app.route("/about")
def about():
	return render_template("about.html",params=params)


#login page		
@app.route("/userarea", methods=['GET','POST'])
def login():
	if "user" in session and session["user"]==params["admin_name"]:
		posts=Post()
		return render_template("userarea.html",params=params,posts=posts)
				
	elif request.method=='POST':
		username=request.form.get('uname')
		password=request.form.get('password')
		
		if username==params["admin_name"] and password==params["admin_password"]:
			session["user"]=username
			posts=Post()
			return render_template("userarea.html",params=params,posts=posts)
	return render_template("login.html",params=params)	


#Edit and add
@app.route("/edit/<string:sno>", methods=['GET' , 'POST'])
def edit(sno):	
	if "user" in session and session["user"]==params["admin_name"]:
		if(request.method=='POST'):
		 title = request.form.get('title')
		 content = request.form.get('content')
		 slug = request.form.get('slug')
		 img_file = request.form.get('img_file')
		 tagtitle = request.form.get('tagtitle')
		 if sno=='0':
		 	data=(title,content,slug,datetime.now(),img_file,tagtitle)
		 	Add_post(data)
		 	mydb.commit()
		 else:
		 	if(request.method=='POST'):
		 		title = request.form.get('title')
		 		content = request.form.get('content')
		 		slug = request.form.get('slug')
		 		img_file = request.form.get('img_file')
		 		tagtitle = request.form.get('tagtitle')
		 							
		 	data=(title, content, slug,img_file,tagtitle,sno)
		 	Edit_post(data)
		 	mydb.commit()
	
	return render_template('edit.html',params=params,sno=int(sno), posts=Post())
				
#Contact page
@app.route("/contact", methods=['GET' , 'POST'])
def contact():
	if(request.method=='POST'):
		 name = request.form.get('name')
		 email = request.form.get('email')
		 phone = request.form.get('phone')
		 message = request.form.get('message')
		 data=(name,email,phone,message)
		 Contact(data)
		 mydb.commit()
		 #msg = Message('Hello', sender = params["mail_user"], recipients = ['someone1@gmail.com'])
#		 msg.body = "This is the email body"
#		 mail.send(msg)
	return render_template('contact.html',params=params)
	
@app.route("/uploader", methods=["POST", "GET"])
def upload ():
	if "user" in session and session["user"]==params["admin_name"]:
		if(request.method=='POST'):
			f=request.files["file1"]
			f.save( os.path.join(app.config['UPLOAD_FOLDER']
			,secure_filename(f.filename)))
			return "File Successfully Uploaded"

#delete  page
@app.route("/delete/<string:sno>")
def delete(sno):
	delt=(int(sno),)
	Delete(delt)
	mydb.commit()
	return render_template("userarea.html",params=params,posts=Post())
	

	#logout page
@app.route("/logout")
def logout ():
	session.pop("user")
	return redirect("/userarea")

app.run(debug=True)