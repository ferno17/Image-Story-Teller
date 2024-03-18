import pandas as pd
import io
import os
import streamlit as st
import requests
from PIL import Image
from gtts import gTTS
from transformers import pipeline
from IPython.display import Audio
from langchain import PromptTemplate, LLMChain
from langchain.llms import GooglePalm
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
llm = GooglePalm(temperature=0.9, google_api_key=os.getenv("GOOGLE_API_KEY"))
HUGGINGFACEHUB_API_TOKEN=os.getenv("HUGGINGFACEHUB_API_TOKEN")
@st.cache_data
@st.cache_resource

def predict():
	img_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
	text = img_to_text('tmp.jpg')[0]["generated_text"]
	return text   
    
#llm
def generate_story(scenario):
    template = """
    you are a very good story teller and a very rude person:
    you can generate a short fairy tail based on a single narrative, the story should take 5 seconds to read.
    CONTEXT: {scenario}
    STORY:
    """

    prompt = PromptTemplate(template=template, input_variables=["scenario"])
    story_llm = LLMChain(llm=llm, prompt=prompt, verbose=True)
    story = story_llm.predict(scenario=scenario)
    return story


# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY,password TEXT)')

def delete_user(user):
    conn = sqlite3.connect("data.db", check_same_thread=False)
    conn.execute('DELETE FROM userstable WHERE username = ?',[user])
 
def delete_db():
	c.execute('drop table userstable')

def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

def sidebar_bg(side_bg):

   side_bg_ext = 'png'
   
   
def main():
	"""Simple Login App"""

	st.title("Image :violet[Story] Teller")
	page_bg_img = '''
	<style>
	body {
	background-image: url("https://images.unsplash.com/photo-1542281286-9e0a16bb7366");
	background-size: cover;
	}
	</style>
	'''
	st.markdown(page_bg_img, unsafe_allow_html=True)
	menu = ["Home","Login","SignUp","Admin"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.write("This is a web app which can help in identifying what an images contains and can develop a story thread from this. The output can be generated as a audio")
		st.write("Steps to follow")
		st.write("1.Toggle the arrow key on the upper left corner for options")
		st.write("2.Select sign up if you are a new user")
		st.write("3.Login to upload image and listen to the story")  
	elif choice == "Login":
		st.write(':violet[Login or sign up to access the features of this web site]')
		username = st.sidebar.text_input("Email")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)
			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:
				st.session_state.sidebar_state = 'collapsed'
				st.success("Logged In as {}".format(username))
				img_upload = st.file_uploader(label='Upload Image', type=['jpg', 'png', 'jpeg'])
				with st.expander("Camera"):
					cam_pic = st.camera_input('Take a photo')
				if st.button('CREATE'):
					if cam_pic != None:
						img = cam_pic.read()
					elif img_upload != None:
						img = img_upload.read()
					img = Image.open(io.BytesIO(img))
					img = img.convert('RGB')
					img.save('tmp.jpg')
					st.image(img)
					with st.spinner('Please Wait'):
						scenario=predict()
						story=generate_story(scenario)
						tts=gTTS(story)
						tts.save(r"C:\Users\Ferno\Downloads\img_cap\1.wav")
					os.remove('tmp.jpg')
					with st.expander("scenario"):
						st.write(scenario)
					with st.expander("story"):
						st.write(story)
					st.audio(r"C:\Users\Ferno\Downloads\img_cap\1.wav")
			else:
				st.warning("Incorrect Username/Password")
	elif choice == "SignUp":
		create_usertable()
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')
		if st.button("Signup"):
			r=view_all_users()
			for row in r:
				if row[0]==new_user:
					st.error('user exists')
				else:
					add_userdata(new_user,make_hashes(new_password))
					st.success("You have successfully created a valid Account")
					st.info("Go to Login Menu to login")				
	elif choice == "Admin":
		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			hashed_pswd = make_hashes(password)
			result = login_user(username,check_hashes(password,hashed_pswd))
			if username=='admin' and password=='admin@123':
				if st.button('show'):
					st.subheader("User Profiles")
					colms= st.columns((2,2,1))
					fields = ['Email','Password','Action']
					for col,field_name in zip(colms,fields):
						col.write(field_name)
						user_result = view_all_users()
						count=0
					for row in user_result:
						count=count+1
						col1, col2, col3= st.columns((2,2,1))
						name=row[0]
						col1.write(row[0])
						col2.write(row[1])
						with col3:
							st.button('Hide',key=count,on_click=delete_user,args=[name])
if __name__ == '__main__':
	main()
